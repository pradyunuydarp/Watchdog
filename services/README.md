# Services

Each subdirectory contains an independently deployable service.

- `core-service`: Spring Boot orchestration and ticket management
- `watcher-service`: Go ingestion and event normalization
- `nlp-service`: FastAPI classification and enrichment

The services are intentionally decoupled so they can evolve into separate deployables later.
