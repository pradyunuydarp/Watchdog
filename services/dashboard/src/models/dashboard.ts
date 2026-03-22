/**
 * Shared dashboard data models.
 *
 * These types are used by the mock data generator, the API client layer, and
 * the React components so the frontend can stay consistent once live data is
 * wired in.
 */

export type TicketSeverity = "critical" | "high" | "medium" | "low";
export type TicketStatus = "open" | "investigating" | "resolved";
export type EventKind = "log" | "metric" | "enrichment";
export type ServiceHealthState = "healthy" | "degraded" | "down" | "unknown";

export interface DashboardTicket {
  id: string;
  source: string;
  summary: string;
  severity: TicketSeverity;
  status: TicketStatus;
  assignee: string;
  createdAt: string;
  updatedAt: string;
  correlationId: string;
}

export interface DashboardEvent {
  id: string;
  kind: EventKind;
  source: string;
  summary: string;
  details: string;
  level: TicketSeverity;
  receivedAt: string;
  correlationId: string;
}

export interface DashboardServiceHealth {
  serviceName: string;
  status: ServiceHealthState;
  latencyMs: number;
  uptime: string;
  lastCheckedAt: string;
  notes: string;
}

export interface DashboardSummaryMetric {
  label: string;
  value: string;
  hint: string;
}

export interface DashboardSnapshot {
  generatedAt: string;
  activeTickets: number;
  queueDepth: number;
  averageLatencyMs: number;
  alertsInLastHour: number;
  tickets: DashboardTicket[];
  events: DashboardEvent[];
  health: DashboardServiceHealth[];
}

