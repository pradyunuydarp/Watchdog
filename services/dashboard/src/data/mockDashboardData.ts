import type {
  DashboardEvent,
  DashboardServiceHealth,
  DashboardSnapshot,
  DashboardTicket,
} from "../models/dashboard";

/**
 * Returns a timestamp offset from a base date.
 *
 * This helper keeps the mock dataset readable and makes it easy to shift the
 * whole scene forward in time whenever the snapshot refreshes.
 */
function shiftMinutes(baseTime: Date, minutes: number): string {
  return new Date(baseTime.getTime() - minutes * 60_000).toISOString();
}

/**
 * Builds a realistic mock dashboard snapshot that represents the current
 * Watchdog prototype: Kafka ingestion, Supabase-backed state, and operator
 * triage activity.
 */
export function buildMockDashboardSnapshot(referenceTime = new Date()): DashboardSnapshot {
  const tickets: DashboardTicket[] = [
    {
      id: "TCK-1041",
      source: "payment-service",
      summary: "Database connection timeout during checkout",
      severity: "critical",
      status: "investigating",
      assignee: "Asha",
      createdAt: shiftMinutes(referenceTime, 18),
      updatedAt: shiftMinutes(referenceTime, 2),
      correlationId: "corr-pay-98a1",
    },
    {
      id: "TCK-1040",
      source: "auth-service",
      summary: "Spike in login failures after token refresh",
      severity: "high",
      status: "open",
      assignee: "Unassigned",
      createdAt: shiftMinutes(referenceTime, 29),
      updatedAt: shiftMinutes(referenceTime, 7),
      correlationId: "corr-auth-7c14",
    },
    {
      id: "TCK-1039",
      source: "catalog-service",
      summary: "Slow search requests from the west region",
      severity: "medium",
      status: "resolved",
      assignee: "Ravi",
      createdAt: shiftMinutes(referenceTime, 52),
      updatedAt: shiftMinutes(referenceTime, 11),
      correlationId: "corr-cat-420f",
    },
    {
      id: "TCK-1038",
      source: "billing-service",
      summary: "Noise reduction rule suppressed duplicate alerts",
      severity: "low",
      status: "resolved",
      assignee: "System",
      createdAt: shiftMinutes(referenceTime, 74),
      updatedAt: shiftMinutes(referenceTime, 68),
      correlationId: "corr-bill-1221",
    },
  ];

  const events: DashboardEvent[] = [
    {
      id: "EVT-9008",
      kind: "enrichment",
      source: "nlp-service",
      summary: "Severity upgraded to critical",
      details: "Classifier returned a high confidence match for database timeout.",
      level: "critical",
      receivedAt: shiftMinutes(referenceTime, 1),
      correlationId: "corr-pay-98a1",
    },
    {
      id: "EVT-9007",
      kind: "log",
      source: "watcher-service",
      summary: "Normalized log event from payment-service",
      details: "payment timeout while charging card",
      level: "high",
      receivedAt: shiftMinutes(referenceTime, 3),
      correlationId: "corr-pay-98a1",
    },
    {
      id: "EVT-9006",
      kind: "metric",
      source: "watcher-service",
      summary: "Checkout latency crossed warning threshold",
      details: "p95 latency reached 842 ms over the last five minutes.",
      level: "medium",
      receivedAt: shiftMinutes(referenceTime, 6),
      correlationId: "corr-pay-88c2",
    },
    {
      id: "EVT-9005",
      kind: "enrichment",
      source: "nlp-service",
      summary: "Auth event grouped with previous failure burst",
      details: "Two similar incidents merged into a single triage lane.",
      level: "high",
      receivedAt: shiftMinutes(referenceTime, 12),
      correlationId: "corr-auth-7c14",
    },
    {
      id: "EVT-9004",
      kind: "metric",
      source: "kafka",
      summary: "Pointer topic lag remains inside threshold",
      details: "Consumer lag is stable and replayable with no dropped offsets.",
      level: "low",
      receivedAt: shiftMinutes(referenceTime, 15),
      correlationId: "corr-platform-11a9",
    },
  ];

  const health: DashboardServiceHealth[] = [
    {
      serviceName: "watcher-service",
      status: "healthy",
      latencyMs: 14,
      uptime: "99.99%",
      lastCheckedAt: shiftMinutes(referenceTime, 1),
      notes: "Kafka producer queue is empty and ingest latency is steady.",
    },
    {
      serviceName: "core-service",
      status: "healthy",
      latencyMs: 43,
      uptime: "99.97%",
      lastCheckedAt: shiftMinutes(referenceTime, 1),
      notes: "Ticket writes are flowing to Supabase Postgres.",
    },
    {
      serviceName: "nlp-service",
      status: "degraded",
      latencyMs: 128,
      uptime: "99.84%",
      lastCheckedAt: shiftMinutes(referenceTime, 1),
      notes: "Inference remains online, but response times are elevated.",
    },
    {
      serviceName: "kafka",
      status: "healthy",
      latencyMs: 8,
      uptime: "99.99%",
      lastCheckedAt: shiftMinutes(referenceTime, 1),
      notes: "Pointer and enrichment topics have healthy consumer lag.",
    },
    {
      serviceName: "supabase",
      status: "healthy",
      latencyMs: 27,
      uptime: "99.98%",
      lastCheckedAt: shiftMinutes(referenceTime, 1),
      notes: "JWT auth and the Postgres tenant are available.",
    },
  ];

  return {
    generatedAt: referenceTime.toISOString(),
    activeTickets: tickets.filter((ticket) => ticket.status !== "resolved").length,
    queueDepth: 18,
    averageLatencyMs: 52,
    alertsInLastHour: 11,
    tickets,
    events,
    health,
  };
}

