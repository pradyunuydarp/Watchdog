// Package http exposes the watcher service HTTP transport.
package http

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/service"
)

const maxRequestBodyBytes = 1 << 20

// Handler owns the watcher service HTTP routes and delegates business logic to the service layer.
type Handler struct {
	serviceName string
	ingestion   *service.IngestionService
	mux         *http.ServeMux
}

// NewHandler creates a ready-to-serve HTTP handler with all watcher routes registered.
func NewHandler(serviceName string, ingestion *service.IngestionService) *Handler {
	h := &Handler{
		serviceName: serviceName,
		ingestion:   ingestion,
		mux:         http.NewServeMux(),
	}

	h.routes()
	return h
}

// Routes returns the underlying HTTP handler tree.
func (h *Handler) Routes() http.Handler {
	return h.mux
}

// routes registers the service endpoints on the internal mux.
func (h *Handler) routes() {
	h.mux.HandleFunc("GET /api/v1/health", h.health)
	h.mux.HandleFunc("POST /api/v1/ingest", h.ingest)
}

// health writes the current service status in JSON.
func (h *Handler) health(w http.ResponseWriter, r *http.Request) {
	_ = r
	writeJSON(w, http.StatusOK, h.ingestion.Health(h.serviceName))
}

// ingest decodes a request, forwards it to the service layer, and returns the normalized response.
func (h *Handler) ingest(w http.ResponseWriter, r *http.Request) {
	body := http.MaxBytesReader(w, r.Body, maxRequestBodyBytes)
	defer func() {
		_, _ = io.Copy(io.Discard, body)
		_ = body.Close()
	}()

	decoder := json.NewDecoder(body)
	decoder.DisallowUnknownFields()

	var req model.IngestRequest
	if err := decoder.Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, err)
		return
	}

	resp, err := h.ingestion.Ingest(r.Context(), req)
	if err != nil {
		status := http.StatusBadRequest
		if !errors.Is(err, service.ErrInvalidRequest) {
			status = http.StatusInternalServerError
		}
		writeError(w, status, err)
		return
	}

	writeJSON(w, http.StatusAccepted, resp)
}

// writeJSON writes a JSON payload with the requested status code.
func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

// writeError emits a stable error envelope for HTTP clients.
func writeError(w http.ResponseWriter, status int, err error) {
	writeJSON(w, status, map[string]string{
		"status":  "error",
		"message": err.Error(),
	})
}
