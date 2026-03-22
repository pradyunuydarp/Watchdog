import type { DashboardTicket } from "../models/dashboard";
import { formatLocalTime } from "../utils/time";
import { formatSeverity, severityRank } from "../utils/severity";

export interface TicketListPanelProps {
  tickets: DashboardTicket[];
}

/**
 * Renders the current incident backlog in operator-friendly order.
 *
 * The panel keeps severity and freshness visible so the operator can prioritize
 * work without cross-referencing another view.
 */
export function TicketListPanel({ tickets }: TicketListPanelProps) {
  const orderedTickets = [...tickets].sort((left, right) => {
    const severityDelta = severityRank[left.severity] - severityRank[right.severity];
    if (severityDelta !== 0) {
      return severityDelta;
    }

    return new Date(right.updatedAt).getTime() - new Date(left.updatedAt).getTime();
  });

  return (
    <section className="panel panel--tickets">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Incidents</p>
          <h2>Ticket list</h2>
        </div>
        <span className="panel__count">{orderedTickets.length} active</span>
      </div>
      <div className="panel__body">
        {orderedTickets.map((ticket) => (
          <article key={ticket.id} className="ticket-card">
            <div className="ticket-card__topline">
              <span className={`severity-pill severity-pill--${ticket.severity}`}>
                {formatSeverity(ticket.severity)}
              </span>
              <span className="ticket-card__id">{ticket.id}</span>
            </div>
            <h3>{ticket.summary}</h3>
            <p className="ticket-card__meta">
              {ticket.source} · {ticket.status} · assignee {ticket.assignee}
            </p>
            <div className="ticket-card__footer">
              <span>Updated {formatLocalTime(ticket.updatedAt)}</span>
              <span>Correlation {ticket.correlationId}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

