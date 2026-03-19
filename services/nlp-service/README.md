# Watchdog NLP Service

FastAPI-based skeleton for Watchdog's NLP and triage layer.

## Endpoints

- `GET /api/v1/health`
- `POST /api/internal/nlp/analyze`

## Request

```json
{
  "text": "Database timeout while processing payment request"
}
```

## Response

```json
{
  "category": "database",
  "severity": "high",
  "confidence": 0.86,
  "entities": ["database", "timeout", "payment"]
}
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
python -m unittest discover -s tests -p "test_*.py"
```

