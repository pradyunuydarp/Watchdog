package service

import (
	"context"
	"testing"
	"time"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
)

// recordingPublisher captures the normalized event passed to the publisher so tests can inspect it.
type recordingPublisher struct {
	event model.NormalizedEvent
	calls int
}

// Publish implements the publisher contract for test assertions.
func (r *recordingPublisher) Publish(_ context.Context, event model.NormalizedEvent) error {
	r.event = event
	r.calls++
	return nil
}

// TestIngestNormalizesLogEvents checks that a log request becomes a Kafka-ready envelope.
func TestIngestNormalizesLogEvents(t *testing.T) {
	recorder := &recordingPublisher{}
	svc := NewIngestionService(recorder)
	fixedClock := time.Date(2026, time.March, 21, 10, 0, 0, 0, time.UTC)
	svc.clock = func() time.Time { return fixedClock }

	resp, err := svc.Ingest(context.Background(), model.IngestRequest{
		Source:  "payments",
		Message: "database timeout while charging card",
	})
	if err != nil {
		t.Fatalf("ingest returned error: %v", err)
	}
	if resp.Kind != model.KindLog {
		t.Fatalf("expected log kind, got %s", resp.Kind)
	}
	if recorder.calls != 1 {
		t.Fatalf("expected one publish call, got %d", recorder.calls)
	}
	if recorder.event.Source != "payments" {
		t.Fatalf("unexpected source %q", recorder.event.Source)
	}
	if recorder.event.Payload.Message != "database timeout while charging card" {
		t.Fatalf("unexpected payload message %q", recorder.event.Payload.Message)
	}
	if recorder.event.EventID == "" {
		t.Fatalf("expected event id to be populated")
	}
	if recorder.event.ReceivedAt.IsZero() {
		t.Fatalf("expected received timestamp to be populated")
	}
}

// TestIngestNormalizesMetrics verifies metric requests are converted into metric envelopes.
func TestIngestNormalizesMetrics(t *testing.T) {
	value := 245.8
	recorder := &recordingPublisher{}
	svc := NewIngestionService(recorder)
	svc.clock = func() time.Time { return time.Date(2026, time.March, 21, 10, 0, 0, 0, time.UTC) }

	resp, err := svc.Ingest(context.Background(), model.IngestRequest{
		Source:      "payments",
		MetricName:  "payment_latency_ms",
		MetricValue: &value,
	})
	if err != nil {
		t.Fatalf("ingest returned error: %v", err)
	}
	if resp.Kind != model.KindMetric {
		t.Fatalf("expected metric kind, got %s", resp.Kind)
	}
	if recorder.event.Payload.MetricName != "payment_latency_ms" {
		t.Fatalf("unexpected metric name %q", recorder.event.Payload.MetricName)
	}
	if recorder.event.Payload.MetricValue == nil || *recorder.event.Payload.MetricValue != value {
		t.Fatalf("unexpected metric value %#v", recorder.event.Payload.MetricValue)
	}
}

// TestIngestRejectsInvalidPayload ensures the service protects the Kafka path from malformed requests.
func TestIngestRejectsInvalidPayload(t *testing.T) {
	recorder := &recordingPublisher{}
	svc := NewIngestionService(recorder)

	if _, err := svc.Ingest(context.Background(), model.IngestRequest{Source: "payments"}); err == nil {
		t.Fatalf("expected validation failure")
	}
	if recorder.calls != 0 {
		t.Fatalf("publisher should not be called for invalid input")
	}
}
