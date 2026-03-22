import type { DashboardApiClient } from "./dashboardApi";
import type { DashboardSnapshot } from "../models/dashboard";

/**
 * HTTP implementation of the dashboard API client.
 *
 * This is intentionally small: it establishes the transport contract the
 * frontend expects when the backend is ready, while the mock client keeps the
 * app usable today.
 */
export class HttpDashboardApiClient implements DashboardApiClient {
  constructor(private readonly baseUrl: string) {}

  /**
   * Fetches the full dashboard snapshot from the backend.
   */
  async fetchSnapshot(): Promise<DashboardSnapshot> {
    const normalizedBaseUrl = this.baseUrl.replace(/\/$/, "");
    const response = await fetch(`${normalizedBaseUrl}/api/v1/dashboard/snapshot`, {
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Dashboard snapshot request failed with ${response.status}`);
    }

    return (await response.json()) as DashboardSnapshot;
  }
}
