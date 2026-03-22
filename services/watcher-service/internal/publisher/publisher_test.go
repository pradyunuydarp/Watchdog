package publisher

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
)

// TestKafkaPublisherBuildsRecord verifies the watcher emits a Kafka-shaped record with headers and JSON payload.
func TestKafkaPublisherBuildsRecord(t *testing.T) {
	recorder := &RecorderWriter{}
	pub := NewKafkaPublisher("watchdog.pointer-events.v1", []string{"kafka:9092"}, recorder)
	pub.now = func() time.Time { return time.Date(2026, time.March, 21, 10, 0, 0, 0, time.UTC) }

	event := model.NormalizedEvent{
		EventID:       "evt_123",
		Source:        "payments",
		Kind:          model.KindLog,
		CorrelationID: "evt_123",
		ReceivedAt:    time.Date(2026, time.March, 21, 9, 59, 59, 0, time.UTC),
		OccurredAt:    time.Date(2026, time.March, 21, 9, 59, 58, 0, time.UTC),
		Payload: model.EventPayload{
			Message: "timeout",
		},
	}

	if err := pub.Publish(context.Background(), event); err != nil {
		t.Fatalf("publish returned error: %v", err)
	}
	if len(recorder.Records) != 1 {
		t.Fatalf("expected 1 record, got %d", len(recorder.Records))
	}

	record := recorder.Records[0]
	if record.Topic != "watchdog.pointer-events.v1" {
		t.Fatalf("unexpected topic %q", record.Topic)
	}
	if record.Key != "evt_123" {
		t.Fatalf("unexpected key %q", record.Key)
	}
	if record.Headers["watchdog_brokers"] != "kafka:9092" {
		t.Fatalf("unexpected broker header %q", record.Headers["watchdog_brokers"])
	}

	var decoded model.NormalizedEvent
	if err := json.Unmarshal(record.Value, &decoded); err != nil {
		t.Fatalf("record payload is not valid json: %v", err)
	}
	if decoded.EventID != event.EventID || decoded.Payload.Message != event.Payload.Message {
		t.Fatalf("unexpected decoded payload: %+v", decoded)
	}
}
