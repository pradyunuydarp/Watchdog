# Watchdog

Watchdog is a service-oriented monitoring and incident triage platform. The target architecture follows the design in [`highlevel_TODO.md`](./highlevel_TODO.md) and [`Watchdog-SRS.md`](./Watchdog-SRS.md): a Spring Boot core service orchestrates incident state, a Go watcher service ingests events, and a Python NLP service enriches logs.

The `landon-hotel` directory is intentionally excluded from this implementation path. It remains a separate learning project.

## Monorepo Layout

```text
.
├── contracts/              # Shared API and event contracts
├── docs/                   # Architecture and onboarding notes
├── infra/                  # Local infrastructure bootstrap files
├── services/
│   ├── core-service/       # Spring Boot orchestration service
│   ├── dashboard/          # React/TypeScript operator dashboard
│   ├── watcher-service/    # Go ingestion service
│   └── nlp-service/        # FastAPI NLP enrichment service
└── docker-compose.yml      # Local multi-service development stack
```

## Current Scope

- `core-service`: starter ticket-management service with security and PostgreSQL stubs.
- `watcher-service`: ingestion API with normalized-event publishing scaffolding for Kafka.
- `nlp-service`: heuristic analyzer service with service-layer and gRPC-prep abstractions.
- `dashboard`: operator dashboard scaffold with mock/live API adapters.
- Root infrastructure: Kafka + Supabase-oriented environment wiring and local compose scaffolding.

## Quick Start

1. Copy `.env.example` to `.env` and adjust values if needed.
2. Start infrastructure and services with `docker compose up --build`.
3. Use the service READMEs under `services/` for local runs outside Docker.

## Roadmap Alignment

- Phase 1: monorepo skeleton and service boilerplates
- Phase 2: wire watcher publishing into core ingestion paths
- Phase 3: replace heuristic NLP with trained models and connect enrichment flow
- Phase 4: add dashboard, gateway, and observability stack

## Notes

- Existing helper scripts under `bin/` are preserved.
- Existing learning material under `landon-hotel/` and `learning/` is untouched.
