# Watcher Service

Go HTTP ingestion service for Watchdog.

This implementation keeps the current development stage lightweight:

- HTTP ingest and health endpoints are live
- incoming requests are normalized into a canonical event envelope
- Kafka publishing is scaffolded behind a narrow writer interface
- local runs stay functional even when a Kafka client is not wired in yet

## Endpoints

- `GET /api/v1/health`
- `POST /api/v1/ingest`

## Environment

- `PUBLISH_MODE=kafka` enables the Kafka scaffold
- `KAFKA_BROKERS` sets the target broker list
- `KAFKA_TOPIC` sets the publish topic

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
