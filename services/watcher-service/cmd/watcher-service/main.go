package main

import (
	"log"
	"net/http"
	"os"
	"time"

	watcherhttp "github.com/pradyundevarakonda/watchdog/watcher-service/internal/transport/http"
	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/service"
)

func main() {
	addr := envOrDefault("PORT", "8081")
	serviceName := envOrDefault("SERVICE_NAME", "watcher-service")

	ingestionService := service.NewIngestionService(nil)
	handler := watcherhttp.NewHandler(serviceName, ingestionService)

	server := &http.Server{
		Addr:         ":" + addr,
		Handler:      handler.Routes(),
		ReadTimeout:  durationOrDefault("READ_TIMEOUT", 5*time.Second),
		WriteTimeout: durationOrDefault("WRITE_TIMEOUT", 10*time.Second),
		IdleTimeout:  durationOrDefault("IDLE_TIMEOUT", 60*time.Second),
	}

	log.Printf("%s listening on %s", serviceName, server.Addr)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("server failed: %v", err)
	}
}

func envOrDefault(key, fallback string) string {
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
