/**
 * Human-readable time formatting helpers.
 *
 * Keep time formatting in one place so every card and stream item reads the
 * same way and the UI can be adjusted without hunting through components.
 */

const timeFormatter = new Intl.DateTimeFormat("en", {
  hour: "numeric",
  minute: "2-digit",
  second: "2-digit",
});

/**
 * Formats an ISO timestamp as a compact local time string.
 */
export function formatLocalTime(isoTimestamp: string): string {
  return timeFormatter.format(new Date(isoTimestamp));
}

/**
 * Formats an ISO timestamp into a relative offset like "12m ago".
 */
export function formatRelativeTime(isoTimestamp: string, referenceTime = Date.now()): string {
  const timestamp = new Date(isoTimestamp).getTime();
  const deltaSeconds = Math.max(0, Math.round((referenceTime - timestamp) / 1000));

  if (deltaSeconds < 60) {
    return `${deltaSeconds}s ago`;
  }

  const deltaMinutes = Math.floor(deltaSeconds / 60);
  if (deltaMinutes < 60) {
    return `${deltaMinutes}m ago`;
  }

  const deltaHours = Math.floor(deltaMinutes / 60);
  return `${deltaHours}h ago`;
}

/**
 * Formats a latency value for display in the health panel.
 */
export function formatLatency(latencyMs: number): string {
  return `${latencyMs.toFixed(0)} ms`;
}

