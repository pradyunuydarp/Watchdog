# Watcher Service

Minimal Go HTTP service for Watchdog ingestion.

## Endpoints

- `GET /api/v1/health`
- `POST /api/v1/ingest`

## Request Shape

`POST /api/v1/ingest` accepts either log or metric data.

Example log:

```json
{
  "source": "payments",
  "kind": "LOG",
  "message": "payment timeout while charging card"
}
```

Example metric:

```json
{
  "source": "payments",
  "kind": "METRIC",
  "metric_name": "payment_latency_ms",
  "metric_value": 245.8
}
```

## Run

```bash
go run ./cmd/watcher-service
```

## Build

```bash
go build ./cmd/watcher-service
```

