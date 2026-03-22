// Package service contains the watcher service business logic for ingesting and normalizing events.
package service

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/publisher"
)

var (
	// ErrInvalidRequest is returned when the incoming HTTP payload cannot be normalized.
	ErrInvalidRequest = errors.New("invalid ingestion request")
)

// IngestionService validates incoming requests, normalizes them, and publishes the result.
type IngestionService struct {
	publisher publisher.Publisher
	clock     func() time.Time
}

// NewIngestionService constructs the ingestion service with a publisher.
//
// If no publisher is provided, the service falls back to a discard publisher so the
// HTTP API remains runnable in local development before Kafka wiring is complete.
func NewIngestionService(pub publisher.Publisher) *IngestionService {
	if pub == nil {
		pub = publisher.NoopPublisher{}
	}

	return &IngestionService{
		publisher: pub,
		clock:     time.Now,
	}
}

// Health builds the health response used by the HTTP handler.
func (s *IngestionService) Health(serviceName string) model.HealthResponse {
	return model.HealthResponse{
		Status:    "ok",
		Service:   serviceName,
		Timestamp: s.clock().UTC(),
	}
}

// Ingest validates the request, converts it into the normalized event envelope,
// and publishes the record through the configured publisher.
func (s *IngestionService) Ingest(ctx context.Context, req model.IngestRequest) (model.IngestResponse, error) {
	normalized, err := s.normalize(req)
	if err != nil {
		return model.IngestResponse{}, err
	}

	if err := s.publisher.Publish(ctx, normalized); err != nil {
		return model.IngestResponse{}, err
	}

	return model.IngestResponse{
		Status:      "accepted",
		Kind:        normalized.Kind,
		Source:      normalized.Source,
		AcceptedAt:  normalized.ReceivedAt,
		Queued:      true,
		Description: "event normalized and handed to the Kafka publisher scaffold",
	}, nil
}

// normalize converts the public ingest request into the canonical internal envelope.
func (s *IngestionService) normalize(req model.IngestRequest) (model.NormalizedEvent, error) {
	kind, err := classify(req)
	if err != nil {
		return model.NormalizedEvent{}, err
	}

	receivedAt := s.clock().UTC()
	occurredAt := receivedAt
	timestampToken := ""
	if req.Timestamp != nil && !req.Timestamp.IsZero() {
		occurredAt = req.Timestamp.UTC()
		timestampToken = occurredAt.Format(time.RFC3339Nano)
	}

	payload := model.EventPayload{
		Attributes: map[string]string{},
	}

	switch kind {
	case model.KindLog:
		payload.Message = strings.TrimSpace(req.Message)
	case model.KindMetric:
		payload.MetricName = strings.TrimSpace(req.MetricName)
		payload.MetricValue = req.MetricValue
	}

	normalizedSource := strings.TrimSpace(req.Source)
	eventID := buildEventID(kind, normalizedSource, payload, timestampToken)

	return model.NormalizedEvent{
		EventID:       eventID,
		Source:        normalizedSource,
		Kind:          kind,
		CorrelationID: eventID,
		ReceivedAt:    receivedAt,
		OccurredAt:    occurredAt,
		Payload:       payload,
		Metadata: map[string]string{
			"service": "watcher-service",
		},
	}, nil
}

// classify validates the request and infers the event kind when the client does not provide one.
func classify(req model.IngestRequest) (model.Kind, error) {
	normalizedSource := strings.TrimSpace(req.Source)
	if normalizedSource == "" {
		return "", ErrInvalidRequest
	}

	normalizedKind := model.Kind(strings.ToUpper(strings.TrimSpace(string(req.Kind))))
	switch normalizedKind {
	case model.KindLog:
		if strings.TrimSpace(req.Message) == "" {
			return "", ErrInvalidRequest
		}
		return model.KindLog, nil
	case model.KindMetric:
		if strings.TrimSpace(req.MetricName) == "" || req.MetricValue == nil {
			return "", ErrInvalidRequest
		}
		return model.KindMetric, nil
	case "":
		if strings.TrimSpace(req.MetricName) != "" || req.MetricValue != nil {
			if strings.TrimSpace(req.MetricName) == "" || req.MetricValue == nil {
				return "", ErrInvalidRequest
			}
			return model.KindMetric, nil
		}

		if strings.TrimSpace(req.Message) != "" {
			return model.KindLog, nil
		}
	}

	return "", ErrInvalidRequest
}

// buildEventID derives a stable, content-based event identifier that can support de-duplication.
func buildEventID(kind model.Kind, source string, payload model.EventPayload, timestampToken string) string {
	fingerprint := strings.Builder{}
	fingerprint.WriteString(string(kind))
	fingerprint.WriteString("|")
	fingerprint.WriteString(source)
	fingerprint.WriteString("|")
	fingerprint.WriteString(payload.Message)
	fingerprint.WriteString("|")
	fingerprint.WriteString(payload.MetricName)
	fingerprint.WriteString("|")
	if payload.MetricValue != nil {
		fingerprint.WriteString(strconv.FormatFloat(*payload.MetricValue, 'f', -1, 64))
	}
	fingerprint.WriteString("|")
	fingerprint.WriteString(timestampToken)

	sum := sha256.Sum256([]byte(fingerprint.String()))
	return "evt_" + hex.EncodeToString(sum[:12])
}

// String returns a readable summary useful for future debugging hooks.
func (s *IngestionService) String() string {
	return fmt.Sprintf("IngestionService{publisher=%T}", s.publisher)
}
