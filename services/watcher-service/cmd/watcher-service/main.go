// Command watcher-service starts the Watchdog ingestion service.
package main

import (
	"log"
	"net/http"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/config"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/publisher"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/service"
	watcherhttp "github.com/pradyundevarakonda/watchdog/watcher-service/internal/transport/http"
)

func main() {
	cfg := config.Load()

	ingestionPublisher := buildPublisher(cfg)
	ingestionService := service.NewIngestionService(ingestionPublisher)
	handler := watcherhttp.NewHandler(cfg.ServiceName, ingestionService)

	server := &http.Server{
		Addr:         cfg.ListenAddr(),
		Handler:      handler.Routes(),
		ReadTimeout:  cfg.ReadTimeout,
		WriteTimeout: cfg.WriteTimeout,
		IdleTimeout:  cfg.IdleTimeout,
	}

	log.Printf("%s listening on %s", cfg.ServiceName, server.Addr)
	if cfg.UseKafka() {
		log.Printf("%s kafka scaffold enabled brokers=%v topic=%s", cfg.ServiceName, cfg.Kafka.Brokers, cfg.Kafka.Topic)
	}

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("server failed: %v", err)
	}
}

// buildPublisher selects the Kafka scaffold when Kafka is configured and otherwise falls back to a no-op publisher.
func buildPublisher(cfg config.Config) publisher.Publisher {
	if !cfg.UseKafka() {
		return publisher.NoopPublisher{}
	}

	return publisher.NewKafkaPublisher(
		cfg.Kafka.Topic,
		cfg.Kafka.Brokers,
		publisher.NewDebugWriter(log.Default()),
	)
}
