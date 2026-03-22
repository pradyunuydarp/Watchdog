import type { DashboardEvent } from "../models/dashboard";
import { formatLocalTime, formatRelativeTime } from "../utils/time";
import { formatSeverity } from "../utils/severity";

export interface EventStreamPanelProps {
  events: DashboardEvent[];
}

/**
 * Renders the most recent operational events as a compact stream.
 *
 * This panel is optimized for scanning: source, payload summary, and age stay
 * visible while the detailed text remains available in the card body.
 */
export function EventStreamPanel({ events }: EventStreamPanelProps) {
  const orderedEvents = [...events].sort(
    (left, right) => new Date(right.receivedAt).getTime() - new Date(left.receivedAt).getTime(),
  );

  return (
    <section className="panel panel--events">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Pipeline</p>
          <h2>Event stream</h2>
        </div>
        <span className="panel__count">{events.length} recent</span>
      </div>
      <div className="panel__body panel__body--stream">
        {orderedEvents.map((event) => (
          <article key={event.id} className="stream-item">
            <div className="stream-item__timeline" aria-hidden="true" />
            <div className="stream-item__content">
              <div className="stream-item__header">
                <span className={`event-kind event-kind--${event.kind}`}>{event.kind}</span>
                <span className={`severity-pill severity-pill--${event.level}`}>
                  {formatSeverity(event.level)}
                </span>
                <span className="stream-item__time">{formatRelativeTime(event.receivedAt)}</span>
              </div>
              <h3>{event.summary}</h3>
              <p>{event.details}</p>
              <div className="stream-item__footer">
                <span>{event.source}</span>
                <span>{formatLocalTime(event.receivedAt)}</span>
                <span>{event.correlationId}</span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
