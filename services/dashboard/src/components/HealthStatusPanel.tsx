import type { DashboardServiceHealth } from "../models/dashboard";
import { formatLatency, formatLocalTime } from "../utils/time";

export interface HealthStatusPanelProps {
  health: DashboardServiceHealth[];
  queueDepth: number;
  generatedAt: string;
}

/**
 * Presents service health and platform status for the current snapshot.
 */
export function HealthStatusPanel({ health, queueDepth, generatedAt }: HealthStatusPanelProps) {
  return (
    <section className="panel panel--health">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Infrastructure</p>
          <h2>Health and status</h2>
        </div>
        <span className="panel__count">Queue depth {queueDepth}</span>
      </div>
      <div className="panel__body">
        <div className="health-grid">
          {health.map((service) => (
            <article key={service.serviceName} className="health-card">
              <div className="health-card__header">
                <h3>{service.serviceName}</h3>
                <span className={`health-pill health-pill--${service.status}`}>{service.status}</span>
              </div>
              <div className="health-card__metrics">
                <div>
                  <span className="health-card__metric-label">Latency</span>
                  <span className="health-card__metric-value">{formatLatency(service.latencyMs)}</span>
                </div>
                <div>
                  <span className="health-card__metric-label">Uptime</span>
                  <span className="health-card__metric-value">{service.uptime}</span>
                </div>
              </div>
              <p>{service.notes}</p>
              <footer>Checked {formatLocalTime(service.lastCheckedAt)}</footer>
            </article>
          ))}
        </div>
        <p className="health-footer">
          Snapshot generated {formatLocalTime(generatedAt)}. Kafka backs the event flow and Supabase
          backs the operator state for the local development environment.
        </p>
      </div>
    </section>
  );
}

