import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
/**
 * Vite configuration for the Watchdog dashboard.
 *
 * The app is intentionally small and self-contained, so the config keeps the
 * default build behavior and only sets a predictable development port.
 */
export default defineConfig({
    plugins: [react()],
    server: {
        host: "0.0.0.0",
        port: 5173,
    },
    preview: {
        host: "0.0.0.0",
        port: 4173,
    },
});
