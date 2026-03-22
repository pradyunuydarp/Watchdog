import type { ReactNode } from "react";

export interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

/**
 * Shows a simple fallback for loading or error states.
 */
export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}

