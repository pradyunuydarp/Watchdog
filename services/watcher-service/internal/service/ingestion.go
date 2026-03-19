package service

import (
	"context"
	"errors"
	"strings"
	"time"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/publisher"
)

var ErrInvalidRequest = errors.New("invalid ingestion request")

type IngestionService struct {
	publisher publisher.Publisher
}

func NewIngestionService(pub publisher.Publisher) *IngestionService {
	if pub == nil {
		pub = publisher.NoopPublisher{}
	}

	return &IngestionService{publisher: pub}
}

func (s *IngestionService) Health(serviceName string) model.HealthResponse {
	return model.HealthResponse{
		Status:    "ok",
		Service:   serviceName,
		Timestamp: time.Now().UTC(),
	}
}

func (s *IngestionService) Ingest(ctx context.Context, req model.IngestRequest) (model.IngestResponse, error) {
	classifiedKind, err := classify(req)
	if err != nil {
		return model.IngestResponse{}, err
	}

	if err := s.publisher.Publish(ctx, req); err != nil {
		return model.IngestResponse{}, err
	}

	return model.IngestResponse{
		Status:      "accepted",
		Kind:        classifiedKind,
		Source:      req.Source,
		AcceptedAt:  time.Now().UTC(),
		Queued:      true,
		Description: "event accepted by watcher-service",
	}, nil
}

func classify(req model.IngestRequest) (model.Kind, error) {
	if strings.TrimSpace(req.Source) == "" {
		return "", ErrInvalidRequest
	}

	switch model.Kind(strings.ToUpper(string(req.Kind))) {
	case model.KindLog, model.KindMetric:
		return model.Kind(strings.ToUpper(string(req.Kind))), nil
	case "":
		if req.MetricName != "" || req.MetricValue != nil {
			return model.KindMetric, nil
		}
		if req.Message != "" {
			return model.KindLog, nil
		}
	}

	return "", ErrInvalidRequest
}
