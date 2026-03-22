/// <reference types="vite/client" />

/**
 * Vite environment variables exposed to the dashboard.
 *
 * Keep this file tiny and stable so future backend wiring can use the same
 * configuration surface without changing component code.
 */
interface ImportMetaEnv {
  readonly VITE_DASHBOARD_API_MODE?: "mock" | "http";
  readonly VITE_DASHBOARD_API_BASE_URL?: string;
  readonly VITE_DASHBOARD_REFRESH_MS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

