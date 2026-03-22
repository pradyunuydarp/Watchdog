# Watchdog NLP Service

FastAPI-based skeleton for Watchdog's NLP and triage layer.

## Endpoints

- `GET /api/v1/health`
- `POST /api/internal/nlp/analyze`

## gRPC (Planned / Target)

The target architecture replaces internal REST service-to-service calls with gRPC.
Proto definitions live under `contracts/grpc/watchdog/nlp/v1/analyzer.proto`.

## Analyzer Backends

- `heuristic`: default deterministic rules engine
- `model`: loads a trained local artifact and uses the model-backed analyzer
- `gru`: directly requests the GRU-backed analyzer from the configured artifact
- `lstm`: directly requests the LSTM-backed analyzer from the configured artifact
- `attention`: reserved scaffold for future attention-based models
- `transformer`: reserved scaffold for future transformer models

Set `ANALYZER_BACKEND=model` and point `MODEL_ARTIFACT_PATH` to a trained artifact to enable model inference.

## Training Pipeline

The service now includes a lightweight supervised training scaffold under `app/ml/`:

- deterministic `train/validate/test` splitting
- compact hyperparameter search
- persisted model artifacts
- separate category and severity classifiers
- implemented families: `naive_bayes`, `gru`, `lstm`
- scaffold-only families: `attention`, `transformer`

Train locally:

```bash
python -m app.ml.train
```

The sample dataset lives at `data/training/incidents.jsonl`.

## Future Model Scaffolding

The codebase now reserves explicit backend slots for attention and transformer families.

- config/env wiring already exists for encoder name, tokenizer name, and transformer model name
- artifact metadata can represent `attention` and `transformer` families
- runtime analyzers exist as placeholders and intentionally raise `NotImplementedError` if forced on before implementation
- training pipeline rejects these families with a clear message instead of silently misbehaving

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
