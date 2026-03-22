# Watchdog Architecture

## Architecture & Design Docs (LaTeX)

- `docs/latex/watchdog-architecture.tex`: feature list + architecture prototypes + diagrams
- `docs/latex/watchdog-design.tex`: service-level design (prototype-friendly)
- Diagrams: `docs/diagrams/puml/` (sources) and `docs/diagrams/images/` (rendered PNGs)

## Development-stage Decisions (Current)

- Broker: Kafka
- DB + Auth: Supabase (local dockerized for development)

## Service Boundaries

### Core Service

- Stack: Spring Boot
- Role: system orchestration, ticket lifecycle, RBAC, persistence
- Primary store: PostgreSQL
- Public surface: authenticated management APIs plus health checks

### Watcher Service

- Stack: Go
- Role: high-throughput ingestion for logs and metrics
- Primary responsibilities: classify event shape, validate payloads, forward for downstream processing
- Public surface: ingestion and health APIs

### NLP Service

- Stack: FastAPI
- Role: classify unstructured text into severity, category, and extracted entities
- Current mode: heuristic stub
- Future mode: model-backed inference

## Integration Direction

1. External producers call the watcher service.
2. Watcher service publishes sanitized events for downstream handling.
3. Core service stores and manages tickets.
4. Core service calls NLP service for enrichment when reactive log payloads require analysis.

## Near-Term Follow-Ups

- Add API gateway once service APIs stabilize.
- Add dashboard app after core ticket endpoints are usable.
- Introduce message broker and observability services into local compose.
