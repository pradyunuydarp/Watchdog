package config

import "testing"

// TestLoadUsesDefaults verifies the service stays bootable with no environment configured.
func TestLoadUsesDefaults(t *testing.T) {
	t.Setenv("SERVICE_NAME", "")
	t.Setenv("PORT", "")
	t.Setenv("READ_TIMEOUT", "")
	t.Setenv("WRITE_TIMEOUT", "")
	t.Setenv("IDLE_TIMEOUT", "")
	t.Setenv("PUBLISH_MODE", "")
	t.Setenv("KAFKA_BROKERS", "")
	t.Setenv("KAFKA_TOPIC", "")

	cfg := Load()

	if cfg.ServiceName != "watcher-service" {
		t.Fatalf("expected default service name, got %q", cfg.ServiceName)
	}
	if cfg.Port != "8081" {
		t.Fatalf("expected default port, got %q", cfg.Port)
	}
	if !cfg.UseKafka() {
		t.Fatalf("expected kafka scaffold to be enabled by default")
	}
}

// TestLoadSplitsKafkaBrokers confirms the broker list is parsed from a comma-separated environment value.
func TestLoadSplitsKafkaBrokers(t *testing.T) {
	t.Setenv("KAFKA_BROKERS", "kafka-1:9092, kafka-2:9092 ,")
	t.Setenv("KAFKA_TOPIC", "watchdog.test-topic")

	cfg := Load()

	if got := len(cfg.Kafka.Brokers); got != 2 {
		t.Fatalf("expected 2 brokers, got %d", got)
	}
	if cfg.Kafka.Topic != "watchdog.test-topic" {
		t.Fatalf("unexpected topic %q", cfg.Kafka.Topic)
	}
}
