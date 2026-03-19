package http

import (
	"encoding/json"
	"errors"
	"net/http"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/service"
)

type Handler struct {
	serviceName string
	ingestion   *service.IngestionService
	mux         *http.ServeMux
}

func NewHandler(serviceName string, ingestion *service.IngestionService) *Handler {
	h := &Handler{
		serviceName: serviceName,
		ingestion:   ingestion,
		mux:         http.NewServeMux(),
	}

	h.routes()
	return h
}

func (h *Handler) Routes() http.Handler {
	return h.mux
}

func (h *Handler) routes() {
	h.mux.HandleFunc("GET /api/v1/health", h.health)
	h.mux.HandleFunc("POST /api/v1/ingest", h.ingest)
}

func (h *Handler) health(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, h.ingestion.Health(h.serviceName))
}

func (h *Handler) ingest(w http.ResponseWriter, r *http.Request) {
	var req model.IngestRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
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

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, status int, err error) {
	writeJSON(w, status, map[string]string{
		"status":  "error",
		"message": err.Error(),
	})
}

