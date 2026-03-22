import { useEffect, useRef, useState } from "react";
import type { DashboardApiClient } from "../api";
import type { DashboardSnapshot } from "../models/dashboard";

export interface UseDashboardSnapshotResult {
  snapshot: DashboardSnapshot | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export interface UseDashboardSnapshotOptions {
  refreshIntervalMs: number;
}

/**
 * Manages dashboard snapshot loading and periodic refresh.
 *
 * The hook owns the loading lifecycle so the page component stays focused on
 * composition and rendering.
 */
export function useDashboardSnapshot(
  apiClient: DashboardApiClient,
  options: UseDashboardSnapshotOptions,
): UseDashboardSnapshotResult {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isMountedRef = useRef(true);

  /**
   * Performs one refresh cycle and updates local state.
   */
  async function refresh(): Promise<void> {
    setIsLoading(true);
    setError(null);

    try {
      const nextSnapshot = await apiClient.fetchSnapshot();
      if (isMountedRef.current) {
        setSnapshot(nextSnapshot);
      }
    } catch (refreshError) {
      if (isMountedRef.current) {
        setError(refreshError instanceof Error ? refreshError.message : "Unknown dashboard error");
      }
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }

  useEffect(() => {
    isMountedRef.current = true;

    void refresh();

    const intervalHandle = globalThis.setInterval(() => {
      void refresh();
    }, options.refreshIntervalMs);

    return () => {
      isMountedRef.current = false;
      globalThis.clearInterval(intervalHandle);
    };
    // The api client is intentionally stable for the current session.
  }, [apiClient, options.refreshIntervalMs]);

  return {
    snapshot,
    isLoading,
    error,
    refresh,
  };
}
