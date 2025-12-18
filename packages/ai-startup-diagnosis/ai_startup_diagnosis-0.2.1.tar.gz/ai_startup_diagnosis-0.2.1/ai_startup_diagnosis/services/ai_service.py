"""AI service for analyzing diagnostic answers using OpenAI."""

from typing import List, Dict, Any
import json
import httpx
from ai_startup_diagnosis.config import settings


class AIService:
    """Service for AI-powered analysis."""

    @staticmethod
    async def analyze_diagnostic_answers(questions: List[str], answers: List[str]) -> Dict[str, Any]:
        """
        Analyze diagnostic answers using OpenAI and generate comprehensive report.
        
        Args:
            questions: List of diagnostic questions
            answers: List of user answers to diagnostic questions (must match questions length)
            
        Returns:
            Dictionary with score, level, analysis, advice, next_steps, strengths, and concerns
        """
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Validate that questions and answers have the same length
        if len(questions) != len(answers):
            raise ValueError(f"Number of questions ({len(questions)}) must match number of answers ({len(answers)})")
        
        # Build the prompt with questions and answers
        num_questions = len(questions)
        prompt = f"""You are an encouraging and supportive startup advisor analyzing an entrepreneur's readiness to start a venture. Your goal is to provide direction and actionable guidance, not to discourage them. Based on their answers to {num_questions} diagnostic questions, provide a comprehensive and encouraging analysis.

Questions and Answers:
"""
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            prompt += f"\n{i}. {question}\n   Answer: {answer}\n"
        
        prompt += f"""
CRITICAL INSTRUCTIONS:
1. **Be Encouraging and Solution-Focused**: Your role is to guide and empower, not to judge. Even if they mention obstacles or challenges, provide CONCRETE SOLUTIONS and actionable steps to overcome them. For example, if they mention obstacles (Question 3), don't just say "you're not ready" - give them SPECIFIC strategies to address those obstacles.

2. **Analyze Their Project Idea**: Pay special attention to their project idea (Question 4). Provide detailed feedback on:
   - The problem they're solving and its market potential
   - Strengths of their approach
   - Specific ways to validate or improve the idea
   - Concrete next steps to develop it further

3. **Address Obstacles with Solutions**: If they mention obstacles (Question 3), for EACH obstacle mentioned, provide:
   - A specific, actionable solution
   - Resources or steps they can take
   - Examples of how others have overcome similar challenges
   - Do NOT just say "this is a concern" - give them a path forward

4. **Personalize Everything**: Base ALL your analysis, advice, and next steps on what they ACTUALLY said in their answers. Reference their specific project idea, obstacles, and motivations.

Please analyze these answers and provide:
1. A readiness score from 0-200 (based on: clarity of idea, market validation, financial readiness, skills, commitment, risk management, passion, determination)
2. A readiness level: "Ready to Start" (score >= 150), "Think More" (score 100-149), or "Hold On" (score < 100)
3. A detailed, encouraging analysis paragraph (3-4 sentences) that:
   - Acknowledges their project idea specifically
   - Highlights their strengths and motivation
   - Addresses obstacles with solutions (not just concerns)
   - Provides direction and next steps
4. 4-5 specific pieces of advice tailored to their situation:
   - For obstacles: provide concrete solutions
   - For their project idea: provide validation strategies and improvement suggestions
   - Be actionable and encouraging
5. 3-4 concrete next steps they should take:
   - Specific actions they can do THIS WEEK
   - Resources or tools they can use
   - Ways to validate or develop their idea further
6. 2-4 key strengths you identified from their answers (be specific)
7. 2-4 areas that need attention, BUT for each one, provide a solution or path forward (not just the concern)
   - Format: Each concern should be a STRING that includes both the area and the solution
   - Example: "Limited time commitment - Solution: Start with 5 hours/week and use time-blocking techniques"
   - Example: "Need market validation - Solution: Conduct 10 customer interviews this week using a simple survey"

IMPORTANT: 
- ALWAYS analyze their project idea in detail
- For obstacles, provide SOLUTIONS, not just concerns
- Be encouraging and solution-focused
- Reference their specific answers and project idea
- Do NOT use generic or template responses
- "concerns" must be an array of STRINGS, not objects. Each string should include the concern area AND its solution.

Respond in JSON format:
{{
    "score": <number 0-200>,
    "level": "<Ready to Start | Think More | Hold On>",
    "analysis": "<encouraging analysis paragraph that addresses their project idea and obstacles with solutions>",
    "advice": ["<solution-focused advice 1>", "<solution-focused advice 2>", ...],
    "next_steps": ["<concrete actionable step 1>", "<concrete actionable step 2>", ...],
    "strengths": ["<specific strength 1 from their answers>", "<specific strength 2>", ...],
    "concerns": ["<area and solution as a single string>", "<area and solution as a single string>", ...]
}}

Be encouraging, solution-focused, and specific. Help them move forward, not hold them back."""
        
        # Call OpenAI API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an encouraging and supportive startup advisor with years of experience helping entrepreneurs. Your goal is to provide direction, solutions, and actionable guidance. You focus on helping people overcome obstacles and move forward, not on discouraging them. When entrepreneurs mention challenges, you provide concrete solutions and next steps."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1500,
                    },
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise ValueError(f"OpenAI API error: {response.status_code} - {error_data.get('error', {}).get('message', 'Unknown error')}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parse JSON response
                # Sometimes OpenAI returns markdown code blocks, so we need to extract JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                result = json.loads(content)
                
                # Validate and normalize the response
                score = int(result.get("score", 0))
                score = max(0, min(200, score))  # Ensure score is in range
                
                level = result.get("level", "Think More")
                if level not in ["Ready to Start", "Think More", "Hold On"]:
                    # Auto-correct level based on score if invalid
                    if score >= 150:
                        level = "Ready to Start"
                    elif score >= 100:
                        level = "Think More"
                    else:
                        level = "Hold On"
                
                # Normalize concerns to ensure they are strings
                concerns = result.get("concerns", [])
                normalized_concerns = []
                for concern in concerns:
                    if isinstance(concern, dict):
                        # If AI returned an object, convert it to a string
                        area = concern.get("area", "")
                        solution = concern.get("solution", "")
                        if area and solution:
                            normalized_concerns.append(f"{area} - Solution: {solution}")
                        elif area:
                            normalized_concerns.append(str(area))
                        else:
                            normalized_concerns.append(str(concern))
                    elif isinstance(concern, str):
                        normalized_concerns.append(concern)
                    else:
                        normalized_concerns.append(str(concern))
                
                # Normalize other list fields to ensure they are strings
                def normalize_list(items):
                    return [str(item) for item in items] if items else []
                
                return {
                    "score": score,
                    "level": level,
                    "analysis": result.get("analysis", ""),
                    "advice": normalize_list(result.get("advice", [])),
                    "next_steps": normalize_list(result.get("next_steps", [])),
                    "strengths": normalize_list(result.get("strengths", [])),
                    "concerns": normalized_concerns,
                }
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except httpx.RequestError as e:
            raise ValueError(f"Network error calling OpenAI API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error calling OpenAI API: {str(e)}")

