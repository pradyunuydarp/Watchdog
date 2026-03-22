// Package config loads runtime settings for the watcher service from environment variables.
package config

import (
	"os"
	"strings"
	"time"
)

// Config groups the watcher service settings that affect HTTP serving and event publishing.
type Config struct {
	ServiceName  string
	Port         string
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration
	PublishMode  string
	Kafka        KafkaConfig
}

// KafkaConfig stores the broker and topic settings used by the Kafka publisher scaffold.
type KafkaConfig struct {
	Brokers []string
	Topic   string
}

// Load reads the watcher configuration from environment variables and applies safe defaults.
func Load() Config {
	return Config{
		ServiceName:  stringOrDefault("SERVICE_NAME", "watcher-service"),
		Port:         stringOrDefault("PORT", "8081"),
		ReadTimeout:  durationOrDefault("READ_TIMEOUT", 5*time.Second),
		WriteTimeout: durationOrDefault("WRITE_TIMEOUT", 10*time.Second),
		IdleTimeout:  durationOrDefault("IDLE_TIMEOUT", 60*time.Second),
		PublishMode:  strings.ToLower(stringOrDefault("PUBLISH_MODE", "kafka")),
		Kafka: KafkaConfig{
			Brokers: splitCSV(stringOrDefault("KAFKA_BROKERS", "kafka:9092")),
			Topic:   stringOrDefault("KAFKA_TOPIC", "watchdog.pointer-events.v1"),
		},
	}
}

// ListenAddr returns the TCP bind address used by net/http.
func (c Config) ListenAddr() string {
	return ":" + c.Port
}

// UseKafka reports whether the service should publish normalized events through the Kafka scaffold.
func (c Config) UseKafka() bool {
	return c.PublishMode == "kafka" && len(c.Kafka.Brokers) > 0
}

func stringOrDefault(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}

	return fallback
}

func durationOrDefault(key string, fallback time.Duration) time.Duration {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}

	parsed, err := time.ParseDuration(value)
	if err != nil {
		return fallback
	}

	return parsed
}

func splitCSV(value string) []string {
	parts := strings.Split(value, ",")
	brokers := make([]string, 0, len(parts))

	for _, part := range parts {
		trimmed := strings.TrimSpace(part)
		if trimmed != "" {
			brokers = append(brokers, trimmed)
		}
	}

	return brokers
}
