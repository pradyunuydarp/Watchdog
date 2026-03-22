# Watchdog Dashboard

React + TypeScript operator dashboard for Watchdog.

## What this scaffold includes

- A polished app shell for operators
- Ticket, event, and health panels
- Typed mock data models
- API client abstractions for future backend wiring
- A mock client by default so the UI is usable before services are live

## Run locally

```bash
pnpm install
pnpm run dev
```

The app starts in mock mode by default. To point it at a live backend later, set
`VITE_DASHBOARD_API_MODE=http` and `VITE_DASHBOARD_API_BASE_URL=<base-url>`.

## Build

```bash
pnpm run build
```

## Layout

- `src/models`: shared TypeScript types
- `src/api`: client interfaces plus mock and HTTP implementations
- `src/components`: shell and panel components
- `src/hooks`: dashboard loading logic
- `src/data`: mock data generation
