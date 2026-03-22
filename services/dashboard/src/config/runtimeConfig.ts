import type { DashboardApiMode } from "../api";

/**
 * Runtime configuration resolved from Vite env variables.
 *
 * This keeps API selection in one place and avoids scattering `import.meta.env`
 * checks through the UI.
 */
export interface RuntimeConfig {
  apiMode: DashboardApiMode;
  apiBaseUrl?: string;
  refreshMs: number;
}

/**
 * Reads runtime configuration for the dashboard.
 */
export function readRuntimeConfig(): RuntimeConfig {
  const parsedRefreshMs = Number(import.meta.env.VITE_DASHBOARD_REFRESH_MS ?? 10000);
  const apiMode = import.meta.env.VITE_DASHBOARD_API_MODE;

  return {
    apiMode: apiMode === "http" ? "http" : "mock",
    apiBaseUrl: import.meta.env.VITE_DASHBOARD_API_BASE_URL,
    refreshMs: Number.isFinite(parsedRefreshMs) && parsedRefreshMs > 0 ? parsedRefreshMs : 10000,
  };
}
