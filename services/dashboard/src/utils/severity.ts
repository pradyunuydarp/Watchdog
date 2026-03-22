import type { TicketSeverity } from "../models/dashboard";

/**
 * Severity ranking used to sort tickets and highlight high-priority items.
 */
export const severityRank: Record<TicketSeverity, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
};

/**
 * Converts a severity level into a label suitable for display badges.
 */
export function formatSeverity(severity: TicketSeverity): string {
  return severity.charAt(0).toUpperCase() + severity.slice(1);
}

