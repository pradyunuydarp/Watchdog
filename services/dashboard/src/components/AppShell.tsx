import type { ReactNode } from "react";

export interface AppShellProps {
  title: string;
  subtitle: string;
  statusTag: string;
  children: ReactNode;
}

/**
 * App shell that frames the operator dashboard.
 *
 * The shell owns the top-level visual language, while the panels remain focused
 * on their own content and data rendering.
 */
export function AppShell({ title, subtitle, statusTag, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <div className="app-shell__noise" aria-hidden="true" />
      <header className="app-header">
        <div>
          <p className="eyebrow">Watchdog operator console</p>
          <h1>{title}</h1>
          <p className="app-header__subtitle">{subtitle}</p>
        </div>
        <div className="app-header__status">
          <span className="status-tag">{statusTag}</span>
          <p>Local development build with mock data and backend-ready contracts.</p>
        </div>
      </header>
      <main className="app-content">{children}</main>
    </div>
  );
}

