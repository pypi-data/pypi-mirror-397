# AI Startup Diagnosis

AI-powered startup readiness diagnosis API. Analyzes entrepreneurs' answers to diagnostic questions and provides comprehensive, AI-generated feedback using OpenAI GPT-4o-mini.

## Features

- AI-powered analysis with personalized feedback
- API key authentication
- Rate limiting per API key
- Comprehensive analysis (score, level, advice, next steps, strengths, concerns)
- FastAPI with automatic API documentation

## Installation

```bash
pip install ai-startup-diagnosis
```

## Quick Start

### 1. Configure Environment

Create a `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
API_KEYS=your_api_key_1,your_api_key_2
```

Optional settings:
```bash
RATE_LIMIT_PER_HOUR=100      # Default: 100
RATE_LIMIT_PER_MINUTE=10     # Default: 10
DEBUG=false                   # Default: false
CORS_ORIGINS=*                # Default: *
```

### 2. Start Server

```bash
uvicorn ai_startup_diagnosis.main:app --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

## API Usage

The API uses a sequential question-answer flow:

1. Start a session → Get first question
2. Answer each question → Get next question (repeat until all answered)
3. Finish session → Get AI analysis

Flow:
```
POST /start → Get question 0
POST /answer (question_id: 0) → Get question 1
POST /answer (question_id: 1) → Get question 2
...
POST /answer (question_id: 9) → is_complete: true
POST /finish → Get final analysis
```

### Endpoints

#### POST /api/diagnostic/start

Start a new session and get the first question.

Request:
```http
POST /api/diagnostic/start
X-API-Key: your_api_key
```

Response:
```json
{
  "session_id": "session_1234567890_abc123",
  "question": {
    "id": 0,
    "question": "Let's start with the basics - what's your startup idea or the problem you want to solve?",
    "analysis": "Understanding your core concept and problem-solution fit"
  },
  "progress": 0,
  "total_questions": 10
}
```

#### POST /api/diagnostic/answer

Submit an answer and get the next question. Repeat this endpoint for each question until `is_complete: true`.

Important: Questions must be answered sequentially. The `question_id` you provide must match the expected question:
- First call: `question_id: 0` (from `/start` response)
- Subsequent calls: `question_id` must match `next_question.id` from the previous response

Request:
```http
POST /api/diagnostic/answer
X-API-Key: your_api_key
Content-Type: application/json

{
  "session_id": "session_1234567890_abc123",
  "question_id": 0,
  "answer": "I want to build a platform that connects freelancers with clients..."
}
```

Response (more questions):
```json
{
  "next_question": {
    "id": 1,
    "question": "Interesting! How much time can you realistically commit to this per week?",
    "analysis": "Assessing time commitment and resource availability"
  },
  "progress": 1,
  "total_questions": 10,
  "is_complete": false
}
```

Response (all answered):
```json
{
  "next_question": null,
  "progress": 10,
  "total_questions": 10,
  "is_complete": true
}
```

#### POST /api/diagnostic/finish

Generate final AI analysis after all questions are answered.

Request:
```http
POST /api/diagnostic/finish
X-API-Key: your_api_key
Content-Type: application/json

{
  "session_id": "session_1234567890_abc123"
}
```

Response:
```json
{
  "result": {
    "score": 145,
    "level": "Ready to Start",
    "analysis": "Your idea shows strong potential...",
    "advice": ["Start with customer validation...", "Build an MVP..."],
    "next_steps": ["Create a landing page...", "Reach out to 5 customers..."],
    "strengths": ["Clear problem identification", "Strong technical background"],
    "concerns": ["Limited time - Solution: Start with 5 hours/week..."],
    "is_ai_generated": true
  },
  "test_id": "test_1234567890"
}
```

## Authentication

Provide your API key via header:

- `X-API-Key: your_api_key` (recommended)
- `Authorization: Bearer your_api_key`

Configure valid keys in `API_KEYS` environment variable (comma-separated).

## Rate Limiting

Default limits: 100 requests/hour, 10 requests/minute per API key.

Configure via `RATE_LIMIT_PER_HOUR` and `RATE_LIMIT_PER_MINUTE`.

## Example Usage

### Python

```python
import httpx

API_KEY = "your_api_key"
BASE_URL = "http://localhost:8000"

# 1. Start session
response = httpx.post(
    f"{BASE_URL}/api/diagnostic/start",
    headers={"X-API-Key": API_KEY}
)
data = response.json()
session_id = data["session_id"]
question = data["question"]

# 2. Answer questions sequentially
while True:
    answer = input(f"{question['question']}\nAnswer: ")
    
    response = httpx.post(
        f"{BASE_URL}/api/diagnostic/answer",
        headers={"X-API-Key": API_KEY},
        json={
            "session_id": session_id,
            "question_id": question["id"],
            "answer": answer
        }
    )
    data = response.json()
    
    if data["is_complete"]:
        break
    
    question = data["next_question"]
    print(f"Progress: {data['progress']}/{data['total_questions']}")

# 3. Get final report
response = httpx.post(
    f"{BASE_URL}/api/diagnostic/finish",
    headers={"X-API-Key": API_KEY},
    json={"session_id": session_id}
)
result = response.json()

print(f"Score: {result['result']['score']}/200")
print(f"Level: {result['result']['level']}")
```

### cURL

```bash
API_KEY="your_api_key"
BASE_URL="http://localhost:8000"

# Start session
SESSION=$(curl -s -X POST "${BASE_URL}/api/diagnostic/start" \
  -H "X-API-Key: ${API_KEY}")
SESSION_ID=$(echo $SESSION | jq -r '.session_id')
Q_ID=$(echo $SESSION | jq -r '.question.id')

# Submit answer
curl -X POST "${BASE_URL}/api/diagnostic/answer" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"${SESSION_ID}\",
    \"question_id\": ${Q_ID},
    \"answer\": \"I want to build a SaaS platform...\"
  }"

# Finish (after all questions answered)
curl -X POST "${BASE_URL}/api/diagnostic/finish" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"${SESSION_ID}\"}"
```

## Response Format

Diagnostic Result:
- `score` (int): 0-200 readiness score
- `level` (str): "Ready to Start" | "Think More" | "Hold On"
- `analysis` (str): Detailed analysis paragraph
- `advice` (list): 4-5 personalized advice items
- `next_steps` (list): 3-4 concrete next steps
- `strengths` (list): 2-4 identified strengths
- `concerns` (list): 2-4 areas needing attention (with solutions)
- `is_ai_generated` (bool): Always `true`

## Error Handling

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Invalid request data |
| 401 | Missing or invalid API key |
| 404 | Session not found |
| 429 | Rate limit exceeded |
| 500 | Server error |

Error responses:
```json
{
  "detail": "Error message here"
}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| OPENAI_API_KEY | Yes | - | OpenAI API key |
| API_KEYS | Yes* | - | Comma-separated API keys |
| RATE_LIMIT_PER_HOUR | No | 100 | Requests per hour |
| RATE_LIMIT_PER_MINUTE | No | 10 | Requests per minute |
| DEBUG | No | false | Debug mode |
| CORS_ORIGINS | No | "*" | Allowed CORS origins |

*Required in production. In debug mode, any key accepted if not set.

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License

## Support

- GitHub Issues: https://github.com/willinghood/ai-startup-diagnosis/issues
- Documentation: http://localhost:8000/docs (when server is running)
