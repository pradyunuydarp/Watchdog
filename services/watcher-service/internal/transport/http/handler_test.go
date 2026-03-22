package http

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/publisher"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/service"
)

// TestHealthEndpoint ensures the watcher exposes a simple unauthenticated health check.
func TestHealthEndpoint(t *testing.T) {
	recorder := &publisher.RecorderWriter{}
	kafkaPublisher := publisher.NewKafkaPublisher("watchdog.pointer-events.v1", []string{"kafka:9092"}, recorder)
	svc := service.NewIngestionService(kafkaPublisher)

	handler := NewHandler("watcher-service", svc)
	request := httptest.NewRequest(http.MethodGet, "/api/v1/health", nil)
	response := httptest.NewRecorder()

	handler.Routes().ServeHTTP(response, request)

	if response.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", response.Code)
	}

	var payload model.HealthResponse
	if err := json.NewDecoder(response.Body).Decode(&payload); err != nil {
		t.Fatalf("health response is not json: %v", err)
	}
	if payload.Service != "watcher-service" || payload.Status != "ok" {
		t.Fatalf("unexpected payload: %+v", payload)
	}
}

// TestIngestEndpoint accepts a valid request and returns an accepted response.
func TestIngestEndpoint(t *testing.T) {
	recorder := &publisher.RecorderWriter{}
	kafkaPublisher := publisher.NewKafkaPublisher("watchdog.pointer-events.v1", []string{"kafka:9092"}, recorder)
	svc := service.NewIngestionService(kafkaPublisher)

	handler := NewHandler("watcher-service", svc)
	request := httptest.NewRequest(http.MethodPost, "/api/v1/ingest", strings.NewReader(`{"source":"payments","message":"timeout"}`))
	response := httptest.NewRecorder()

	handler.Routes().ServeHTTP(response, request)

	if response.Code != http.StatusAccepted {
		t.Fatalf("expected 202, got %d", response.Code)
	}
	if len(recorder.Records) != 1 {
		t.Fatalf("expected one published record, got %d", len(recorder.Records))
	}
}

// TestIngestEndpointRejectsBadJSON checks that malformed input fails fast before the service layer runs.
func TestIngestEndpointRejectsBadJSON(t *testing.T) {
	handler := NewHandler("watcher-service", service.NewIngestionService(publisher.NoopPublisher{}))
	request := httptest.NewRequest(http.MethodPost, "/api/v1/ingest", strings.NewReader(`{"source":`))
	response := httptest.NewRecorder()

	handler.Routes().ServeHTTP(response, request)

	if response.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d", response.Code)
	}
}
