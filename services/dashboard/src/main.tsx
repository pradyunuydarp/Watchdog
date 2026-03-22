import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

/**
 * Application entry point.
 *
 * The entry file only mounts React and imports the shared stylesheet so the
 * runtime shape stays easy to follow.
 */
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

