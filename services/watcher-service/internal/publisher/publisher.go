package publisher

import (
	"context"

	"github.com/pradyundevarakonda/watchdog/watcher-service/internal/model"
)

type Publisher interface {
	Publish(ctx context.Context, event model.IngestRequest) error
}

type NoopPublisher struct{}

func (NoopPublisher) Publish(context.Context, model.IngestRequest) error {
	return nil
}

