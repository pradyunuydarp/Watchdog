import type { DashboardSnapshot } from "../models/dashboard";
import { HttpDashboardApiClient } from "./httpDashboardApi";
import { MockDashboardApiClient } from "./mockDashboardApi";

/**
 * Describes the dashboard data contract.
 *
 * The UI depends on this interface instead of a concrete transport so the
 * implementation can move from mock data to HTTP or another backend without
 * rewriting components.
 */
export interface DashboardApiClient {
  fetchSnapshot(): Promise<DashboardSnapshot>;
}

export type DashboardApiMode = "mock" | "http";

export interface DashboardApiConfig {
  mode: DashboardApiMode;
  baseUrl?: string;
}

/**
 * Creates the concrete API client used by the app.
 */
export function createDashboardApiClient(config: DashboardApiConfig): DashboardApiClient {
  if (config.mode === "http") {
    return new HttpDashboardApiClient(config.baseUrl ?? "");
  }

  return new MockDashboardApiClient();
}
