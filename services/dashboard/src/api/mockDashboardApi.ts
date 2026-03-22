import type { DashboardApiClient } from "./dashboardApi";
import { buildMockDashboardSnapshot } from "../data/mockDashboardData";
import type { DashboardSnapshot } from "../models/dashboard";

/**
 * Mock implementation of the dashboard API client.
 *
 * The client simulates a network delay so loading and refresh states are easy
 * to observe in development before the real backend services are available.
 */
export class MockDashboardApiClient implements DashboardApiClient {
  constructor(private readonly latencyMs = 320) {}

  /**
   * Returns a mock snapshot with a small artificial delay.
   */
  async fetchSnapshot(): Promise<DashboardSnapshot> {
    await new Promise<void>((resolve) => {
      globalThis.setTimeout(() => resolve(), this.latencyMs);
    });

    return buildMockDashboardSnapshot();
  }
}
