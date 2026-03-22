export interface SummaryStatCardProps {
  label: string;
  value: string;
  hint: string;
}

/**
 * Displays a single dashboard summary statistic.
 */
export function SummaryStatCard({ label, value, hint }: SummaryStatCardProps) {
  return (
    <article className="summary-card">
      <p className="summary-card__label">{label}</p>
      <p className="summary-card__value">{value}</p>
      <p className="summary-card__hint">{hint}</p>
    </article>
  );
}

