// Package model defines the request, response, and normalized event types used by the watcher service.
package model

import "time"

// Kind identifies the coarse-grained shape of an ingest request or normalized event.
type Kind string

const (
	// KindLog marks an unstructured log event.
	KindLog Kind = "LOG"
	// KindMetric marks a metric observation.
	KindMetric Kind = "METRIC"
)

// IngestRequest is the public HTTP payload accepted by the watcher service.
//
// The service keeps the request shape intentionally small so external producers can
// send either logs or metrics without learning the internal Kafka envelope.
type IngestRequest struct {
	Source      string     `json:"source"`
	Kind        Kind       `json:"kind,omitempty"`
	Message     string     `json:"message,omitempty"`
	MetricName  string     `json:"metric_name,omitempty"`
	MetricValue *float64   `json:"metric_value,omitempty"`
	Timestamp   *time.Time `json:"timestamp,omitempty"`
}

// IngestResponse is returned after a request is normalized and accepted for publishing.
type IngestResponse struct {
	Status      string    `json:"status"`
	Kind        Kind      `json:"kind"`
	Source      string    `json:"source"`
	AcceptedAt  time.Time `json:"accepted_at"`
	Queued      bool      `json:"queued"`
	Description string    `json:"description,omitempty"`
}

// HealthResponse is returned from the service health endpoint.
type HealthResponse struct {
	Status    string    `json:"status"`
	Service   string    `json:"service"`
	Timestamp time.Time `json:"timestamp"`
}

// EventPayload is the normalized payload that is published to Kafka.
//
// The structure deliberately keeps the field names close to the public ingest contract
// so the conversion step remains easy to inspect and extend later.
type EventPayload struct {
	Message     string            `json:"message,omitempty"`
	MetricName  string            `json:"metric_name,omitempty"`
	MetricValue *float64          `json:"metric_value,omitempty"`
	Attributes  map[string]string `json:"attributes,omitempty"`
}

// NormalizedEvent is the canonical event envelope produced by the watcher service.
//
// Prototype C uses pointer events and enrichment events later in the pipeline, but the
// watcher keeps the local published shape generic so the service can evolve without
// rewriting the HTTP ingress path.
type NormalizedEvent struct {
	EventID       string            `json:"event_id"`
	Source        string            `json:"source"`
	Kind          Kind              `json:"kind"`
	CorrelationID string            `json:"correlation_id"`
	ReceivedAt    time.Time         `json:"received_at"`
	OccurredAt    time.Time         `json:"occurred_at"`
	Payload       EventPayload      `json:"payload"`
	Metadata      map[string]string `json:"metadata,omitempty"`
}
