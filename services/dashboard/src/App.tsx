import { useEffect } from "react";
import { createDashboardApiClient } from "./api";
import { AppShell } from "./components/AppShell";
import { EmptyState } from "./components/EmptyState";
import { EventStreamPanel } from "./components/EventStreamPanel";
import { HealthStatusPanel } from "./components/HealthStatusPanel";
import { SummaryStatCard } from "./components/SummaryStatCard";
import { TicketListPanel } from "./components/TicketListPanel";
import { readRuntimeConfig } from "./config/runtimeConfig";
import { useDashboardSnapshot } from "./hooks/useDashboardSnapshot";
import type { DashboardSummaryMetric } from "./models/dashboard";

const runtimeConfig = readRuntimeConfig();
const dashboardApiClient = createDashboardApiClient({
  mode: runtimeConfig.apiMode,
  baseUrl: runtimeConfig.apiBaseUrl,
});

/**
 * Main application component.
 *
 * The component wires configuration, data loading, and presentational panels
 * together without mixing transport concerns into the panel code.
 */
export default function App() {
  const { snapshot, isLoading, error, refresh } = useDashboardSnapshot(dashboardApiClient, {
    refreshIntervalMs: runtimeConfig.refreshMs,
  });

  useEffect(() => {
    document.title = "Watchdog Dashboard";
  }, []);

  const summaryMetrics: DashboardSummaryMetric[] = snapshot
    ? [
        {
          label: "Active tickets",
          value: snapshot.activeTickets.toString(),
          hint: "Incidents awaiting operator action",
        },
        {
          label: "Queue depth",
          value: snapshot.queueDepth.toString(),
          hint: "Kafka pointer backlog across the pipeline",
        },
        {
          label: "Avg latency",
          value: `${snapshot.averageLatencyMs} ms`,
          hint: "Snapshot-wide mean processing time",
        },
        {
          label: "Alerts last hour",
          value: snapshot.alertsInLastHour.toString(),
          hint: "Total alerts promoted into triage",
        },
      ]
    : [
        {
          label: "Active tickets",
          value: isLoading ? "Loading" : "--",
          hint: "Awaiting the first snapshot",
        },
        {
          label: "Queue depth",
          value: isLoading ? "Loading" : "--",
          hint: "Kafka pointer backlog across the pipeline",
        },
        {
          label: "Avg latency",
          value: isLoading ? "Loading" : "--",
          hint: "Snapshot-wide mean processing time",
        },
        {
          label: "Alerts last hour",
          value: isLoading ? "Loading" : "--",
          hint: "Total alerts promoted into triage",
        },
      ];

  return (
    <AppShell
      title="Watchdog"
      subtitle="Prototype C dashboard for incident triage, event stream scanning, and service health monitoring."
      statusTag="Kafka + Supabase + gRPC-ready"
    >
      <section className="summary-grid" aria-label="Dashboard summary metrics">
        {summaryMetrics.map((metric) => (
          <SummaryStatCard key={metric.label} {...metric} />
        ))}
      </section>

      <div className="toolbar">
        <div className="toolbar__status">
          <span className={`connection-dot ${error ? "connection-dot--error" : "connection-dot--ok"}`} />
          <span>{isLoading ? "Refreshing snapshot" : error ? "Snapshot error" : "Snapshot healthy"}</span>
        </div>
        <button type="button" className="refresh-button" onClick={() => void refresh()}>
          Refresh data
        </button>
      </div>

      {snapshot ? (
        <div className="dashboard-grid">
          <TicketListPanel tickets={snapshot.tickets} />
          <EventStreamPanel events={snapshot.events} />
          <HealthStatusPanel
            health={snapshot.health}
            queueDepth={snapshot.queueDepth}
            generatedAt={snapshot.generatedAt}
          />
        </div>
      ) : (
        <EmptyState
          title={error ? "Dashboard snapshot unavailable" : "Loading Watchdog dashboard"}
          description={
            error
              ? error
              : "The app is booting the operator console and preparing the initial snapshot."
          }
          action={
            error ? (
              <button type="button" className="refresh-button" onClick={() => void refresh()}>
                Retry snapshot
              </button>
            ) : null
          }
        />
      )}
    </AppShell>
  );
}
