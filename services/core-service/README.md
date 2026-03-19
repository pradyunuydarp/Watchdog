# Watchdog Core Service

Spring Boot 3 starter for the Watchdog orchestration layer.

## What is included

- `com.watchdog.core` application bootstrap
- `GET /api/v1/health` health endpoint without authentication
- ticket create/list/get API skeleton
- placeholder JWT security filter
- in-memory repository adapter for local development
- PostgreSQL profile stubs for the future JDBC-backed implementation

## Run locally

```bash
mvn spring-boot:run
```

The default profile is `local`, which keeps the service bootable without a database.

## Placeholder auth

Protected endpoints expect `Authorization: Bearer dev-placeholder-token` in the starter configuration.
Replace the filter with real JWT validation, key rotation, issuer checks, and claim mapping before wiring the service into the gateway.

## Profiles

- `local`: boot without database auto-configuration
- `postgres`: datasource and JPA properties for PostgreSQL

## Container build

```bash
docker build -t watchdog-core-service .
```
