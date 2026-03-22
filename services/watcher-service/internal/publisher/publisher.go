// Package publisher defines the watcher service event publishing abstraction.
package publisher

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"strings"
	"sync"
	"time"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
)

var (
	// ErrWriterRequired is returned when a Kafka publisher is created without a backing writer.
	ErrWriterRequired = errors.New("publisher writer is required")
)

// Publisher accepts normalized watcher events and sends them to the next stage in the pipeline.
type Publisher interface {
	Publish(ctx context.Context, event model.NormalizedEvent) error
}

// NoopPublisher intentionally drops every event.
//
// It keeps local development simple when Kafka is not configured or when the service
// is being exercised through tests that only need the HTTP and normalization layers.
type NoopPublisher struct{}

// Publish implements Publisher by doing nothing.
func (NoopPublisher) Publish(context.Context, model.NormalizedEvent) error {
	return nil
}

// Record is the transport-agnostic representation of a Kafka message.
//
// The watcher service does not depend on a Kafka client yet. Instead, the publisher
// builds a record that can be handed to a future client adapter or a recorder in tests.
type Record struct {
	Topic     string
	Key       string
	Value     []byte
	Headers   map[string]string
	Timestamp time.Time
}

// Writer is the narrow sink interface used by the Kafka publisher scaffold.
//
// The interface intentionally mirrors the minimum information the watcher needs to
// hand to a future Kafka client adapter.
type Writer interface {
	Write(ctx context.Context, record Record) error
}

// KafkaPublisher converts normalized events into Kafka-shaped records.
type KafkaPublisher struct {
	topic   string
	brokers []string
	writer  Writer
	now     func() time.Time
}

// NewKafkaPublisher creates a KafkaPublisher with the supplied topic, brokers, and writer.
//
// The broker list is kept on the publisher so it can be emitted in record metadata and
// later passed into a real Kafka client without changing the public service contract.
func NewKafkaPublisher(topic string, brokers []string, writer Writer) *KafkaPublisher {
	if strings.TrimSpace(topic) == "" {
		topic = "watchdog.pointer-events.v1"
	}

	if writer == nil {
		writer = DiscardWriter{}
	}

	return &KafkaPublisher{
		topic:   topic,
		brokers: append([]string(nil), brokers...),
		writer:  writer,
		now:     time.Now,
	}
}

// Publish marshals the normalized event and forwards the record to the configured writer.
func (p *KafkaPublisher) Publish(ctx context.Context, event model.NormalizedEvent) error {
	if p == nil {
		return ErrWriterRequired
	}

	payload, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("marshal normalized event: %w", err)
	}

	record := Record{
		Topic:     p.topic,
		Key:       event.EventID,
		Value:     payload,
		Headers:   buildHeaders(event, p.topic, p.brokers),
		Timestamp: p.now().UTC(),
	}

	if err := p.writer.Write(ctx, record); err != nil {
		return fmt.Errorf("write kafka record: %w", err)
	}

	return nil
}

// DiscardWriter accepts a record and intentionally drops it.
//
// This is useful for local development when the service should stay runnable even
// before a real Kafka adapter is wired in.
type DiscardWriter struct{}

// Write implements Writer.
func (DiscardWriter) Write(context.Context, Record) error {
	return nil
}

// RecorderWriter stores every record it receives in memory.
//
// Tests use this writer to assert that event normalization produces the right Kafka-shaped
// payload without needing a broker.
type RecorderWriter struct {
	mu      sync.Mutex
	Records []Record
}

// Write implements Writer and appends the record to the recorder's slice.
func (r *RecorderWriter) Write(_ context.Context, record Record) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.Records = append(r.Records, record)
	return nil
}

// DebugWriter logs each record instead of publishing it.
//
// The watcher service uses this for now as a visible placeholder that can be swapped
// with a real Kafka client adapter later.
type DebugWriter struct {
	logger *log.Logger
}

// NewDebugWriter creates a record logger backed by the provided logger.
func NewDebugWriter(logger *log.Logger) *DebugWriter {
	if logger == nil {
		logger = log.Default()
	}

	return &DebugWriter{logger: logger}
}

// Write implements Writer by logging a concise summary of the Kafka record.
func (w *DebugWriter) Write(_ context.Context, record Record) error {
	w.logger.Printf(
		"prepared kafka record topic=%s key=%s timestamp=%s bytes=%d",
		record.Topic,
		record.Key,
		record.Timestamp.Format(time.RFC3339Nano),
		len(record.Value),
	)

	return nil
}

func buildHeaders(event model.NormalizedEvent, topic string, brokers []string) map[string]string {
	headers := map[string]string{
		"event_id":       event.EventID,
		"source":         event.Source,
		"kind":           string(event.Kind),
		"correlation_id": event.CorrelationID,
		"received_at":    event.ReceivedAt.Format(time.RFC3339Nano),
		"occurred_at":    event.OccurredAt.Format(time.RFC3339Nano),
		"watchdog_topic": topic,
	}

	if len(brokers) > 0 {
		headers["watchdog_brokers"] = strings.Join(brokers, ",")
	}

	return headers
}
