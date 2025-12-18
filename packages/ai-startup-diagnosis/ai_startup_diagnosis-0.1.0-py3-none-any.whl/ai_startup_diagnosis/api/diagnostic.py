"""Diagnostic test API endpoints."""

from typing import List, Dict, Any
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from ai_startup_diagnosis.models.schemas import (
    DiagnosticResultResponse,
    DiagnosticResult,
    StartSessionResponse,
    AnswerRequest,
    AnswerResponse,
    FinishRequest,
)
from ai_startup_diagnosis.api.auth import get_api_key
from ai_startup_diagnosis.services.ai_service import AIService
from ai_startup_diagnosis.config import settings
from ai_startup_diagnosis.utils.error_handler import handle_api_errors
from ai_startup_diagnosis.services.rate_limiter import limiter

router = APIRouter(prefix="/api/diagnostic", tags=["diagnostic"])

# In-memory session storage
# In production, consider using Redis or a database
sessions: Dict[str, Dict[str, Any]] = {}

# Session expiration time (1 hour)
SESSION_EXPIRY_SECONDS = 3600


def cleanup_expired_sessions():
    """Remove expired sessions to prevent memory leaks."""
    current_time = time.time()
    expired_sessions = [
        session_id for session_id, session_data in sessions.items()
        if current_time - session_data.get("created_at", 0) > SESSION_EXPIRY_SECONDS
    ]
    for session_id in expired_sessions:
        del sessions[session_id]
    if expired_sessions:
        print(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")


# Diagnostic questions
DIAGNOSTIC_QUESTIONS = [
    {
        "id": 0,
        "question": "Let's start with the basics - what's your startup idea or the problem you want to solve?",
        "analysis": "Understanding your core concept and problem-solution fit"
    },
    {
        "id": 1,
        "question": "Interesting! How much time can you realistically commit to this per week? Be honest - this is crucial.",
        "analysis": "Assessing time commitment and resource availability"
    },
    {
        "id": 2,
        "question": "What's your current financial runway? How long can you sustain yourself without income from this venture?",
        "analysis": "Evaluating financial readiness and risk tolerance"
    },
    {
        "id": 3,
        "question": "Have you validated this idea with potential customers? What feedback have you received?",
        "analysis": "Checking market validation and customer discovery"
    },
    {
        "id": 4,
        "question": "What specific skills do you bring to the table? What critical skills are you missing?",
        "analysis": "Analyzing capability gaps and team needs"
    },
    {
        "id": 5,
        "question": "Why now? What makes this the right timing for you personally to start this venture?",
        "analysis": "Understanding personal readiness and motivation"
    },
    {
        "id": 6,
        "question": "What's your biggest fear about starting this? Let's address it head-on.",
        "analysis": "Identifying psychological barriers and concerns"
    },
    {
        "id": 7,
        "question": "If this fails completely, what's your backup plan? How will you recover?",
        "analysis": "Evaluating risk management and resilience"
    },
    {
        "id": 8,
        "question": "On a scale of 1-10, how passionate are you about this? Can you sustain that passion for 3+ years?",
        "analysis": "Measuring commitment depth and long-term motivation"
    },
    {
        "id": 9,
        "question": "Final question - if I told you there's an 80% chance you'll fail, would you still do it? Why?",
        "analysis": "Testing true determination and founder mindset"
    }
]


@router.post("/start", response_model=StartSessionResponse, status_code=status.HTTP_200_OK)
@handle_api_errors
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def start_diagnostic_session(
    request: Request,
    api_key: str = Depends(get_api_key)
) -> StartSessionResponse:
    """
    Start a new diagnostic session and get the first question.
    
    This initiates a sequential question-answer flow where users answer
    one question at a time. Use POST /answer to submit answers and get
    the next question, then POST /finish to generate the final report.
    
    Args:
        api_key: Validated API key from request
        
    Returns:
        Session ID and first question
    """
    # Clean up expired sessions periodically
    cleanup_expired_sessions()
    
    # Generate unique session ID
    session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    # Initialize session
    sessions[session_id] = {
        "answers": {},  # {question_id: answer}
        "next_question_id": 0,  # Track which question should be answered next
        "created_at": time.time(),
    }
    
    # Return first question
    return StartSessionResponse(
        session_id=session_id,
        question=DIAGNOSTIC_QUESTIONS[0],
        progress=0,
        total_questions=len(DIAGNOSTIC_QUESTIONS)
    )


@router.post("/answer", response_model=AnswerResponse, status_code=status.HTTP_200_OK)
@handle_api_errors
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def submit_answer(
    request: Request,
    answer_request: AnswerRequest,
    api_key: str = Depends(get_api_key)
) -> AnswerResponse:
    """
    Submit an answer to a question and get the next question.
    
    Args:
        answer_request: Session ID, question ID, and answer
        api_key: Validated API key from request
        
    Returns:
        Next question (if available) and progress information
    """
    session = sessions.get(answer_request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found. Please start a new session with POST /start"
        )
    
    # Validate question ID is in valid range
    if answer_request.question_id < 0 or answer_request.question_id >= len(DIAGNOSTIC_QUESTIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid question_id. Must be between 0 and {len(DIAGNOSTIC_QUESTIONS) - 1}"
        )
    
    # Enforce sequential answering - must answer the expected question next
    expected_question_id = session.get("next_question_id", 0)
    if answer_request.question_id != expected_question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Questions must be answered sequentially. Expected question_id: {expected_question_id}, but received: {answer_request.question_id}"
        )
    
    # Check if this question was already answered
    if answer_request.question_id in session["answers"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {answer_request.question_id} has already been answered"
        )
    
    # Store answer
    session["answers"][answer_request.question_id] = answer_request.answer
    
    # Update next question ID
    session["next_question_id"] = answer_request.question_id + 1
    
    # Check if all questions are answered
    num_answered = len(session["answers"])
    total_questions = len(DIAGNOSTIC_QUESTIONS)
    next_question_id = session["next_question_id"]
    
    if next_question_id >= total_questions:
        # All questions answered
        return AnswerResponse(
            next_question=None,
            progress=num_answered,
            total_questions=total_questions,
            is_complete=True
        )
    
    # Return next question
    return AnswerResponse(
        next_question=DIAGNOSTIC_QUESTIONS[next_question_id],
        progress=num_answered,
        total_questions=total_questions,
        is_complete=False
    )


@router.post("/finish", response_model=DiagnosticResultResponse, status_code=status.HTTP_200_OK)
@handle_api_errors
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def finish_diagnostic_session(
    request: Request,
    finish_request: FinishRequest,
    api_key: str = Depends(get_api_key)
) -> DiagnosticResultResponse:
    """
    Finish a diagnostic session and generate the final AI-powered analysis.
    
    This endpoint should be called after all questions have been answered
    (when POST /answer returns is_complete: true).
    
    Args:
        finish_request: Session ID to finish
        api_key: Validated API key from request
        
    Returns:
        Diagnostic result with AI analysis
    """
    session = sessions.get(finish_request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found. Please start a new session with POST /start"
        )
    
    # Check if all questions are answered
    answers = session["answers"]
    if len(answers) < len(DIAGNOSTIC_QUESTIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not all questions answered. {len(answers)}/{len(DIAGNOSTIC_QUESTIONS)} questions answered."
        )
    
    # Convert session answers to the format expected by AI service
    sorted_question_ids = sorted(answers.keys())
    questions = []
    answer_texts = []
    
    for qid in sorted_question_ids:
        if qid < len(DIAGNOSTIC_QUESTIONS):
            questions.append(DIAGNOSTIC_QUESTIONS[qid]["question"])
            answer_texts.append(answers[qid])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid question_id {qid} in session answers"
            )
    
    # Validate OpenAI API key is configured
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured. Please configure OPENAI_API_KEY in environment variables."
        )
    
    # Analyze answers using AI
    try:
        if len(questions) != len(answer_texts):
            raise ValueError(f"Mismatch: {len(questions)} questions but {len(answer_texts)} answers")
        
        analysis_result = await AIService.analyze_diagnostic_answers(questions, answer_texts)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        error_message = str(e)
        print(f"❌ AI analysis failed: {error_message}")
        print(f"   Full error traceback:\n{error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {error_message}"
        )
    
    # Create test ID
    test_id = f"test_{int(time.time())}"
    
    # Build response
    result = DiagnosticResult(
        score=analysis_result["score"],
        level=analysis_result["level"],
        analysis=analysis_result["analysis"],
        advice=analysis_result["advice"],
        next_steps=analysis_result["next_steps"],
        strengths=analysis_result["strengths"],
        concerns=analysis_result["concerns"],
        is_ai_generated=True,
    )
    
    # Clean up session
    del sessions[finish_request.session_id]
    
    return DiagnosticResultResponse(result=result, test_id=test_id)

