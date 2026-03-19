package model

import "time"

type Kind string

const (
	KindLog    Kind = "LOG"
	KindMetric Kind = "METRIC"
)

type IngestRequest struct {
	Source      string     `json:"source"`
	Kind        Kind       `json:"kind,omitempty"`
	Message     string     `json:"message,omitempty"`
	MetricName  string     `json:"metric_name,omitempty"`
	MetricValue *float64   `json:"metric_value,omitempty"`
	Timestamp   *time.Time `json:"timestamp,omitempty"`
}

type IngestResponse struct {
	Status      string    `json:"status"`
	Kind        Kind      `json:"kind"`
	Source      string    `json:"source"`
	AcceptedAt  time.Time `json:"accepted_at"`
	Queued      bool      `json:"queued"`
	Description string    `json:"description,omitempty"`
}

type HealthResponse struct {
	Status    string    `json:"status"`
	Service   string    `json:"service"`
	Timestamp time.Time `json:"timestamp"`
}

