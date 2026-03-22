# Contracts

This directory is reserved for shared contracts between services.

Planned contents:

- OpenAPI specs for external APIs
- gRPC proto definitions for internal service APIs
- Event schema definitions for queue-based integration

The initial scaffold includes an event envelope example under `events/ingestion-event.json`.

## gRPC (Internal APIs)

Proto files live under `contracts/grpc/`:

- `contracts/grpc/watchdog/common/v1/event.proto`: shared message types (event envelope, pointer payload, enrichment)
- `contracts/grpc/watchdog/nlp/v1/analyzer.proto`: NLP enrichment service
- `contracts/grpc/watchdog/core/v1/event_ingestor.proto`: optional direct ingestion service (fallback/backfill)
