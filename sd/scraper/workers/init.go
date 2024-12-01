package workers

import (
	"log/slog"
	"scraper/pradan"

	"github.com/adjust/rmq/v5"
	"github.com/redis/go-redis/v9"
	"go.mongodb.org/mongo-driver/mongo"
)

type Worker struct {
	Mongo            *mongo.Client
	DownloadIdsQueue *rmq.Queue // Used for internal message transfer
	*pradan.PradanClient
}

func NewWorker(mongo *mongo.Client, redisClient *redis.Client, pradanClient *pradan.PradanClient) *Worker {
	errChan := make(chan error, 10)
	connection, err := rmq.OpenConnectionWithRedisClient("worker", redisClient, errChan)
	if err != nil {
		slog.Error("%v", err)
	}

	downloadIdsQueue, err := connection.OpenQueue(CH2_IDS_TO_DOWNLOAD)
	if err != nil {
		slog.Error("Can't CONNECT to queue", err)
	}

	return &Worker{Mongo: mongo, DownloadIdsQueue: &downloadIdsQueue, PradanClient: pradanClient}
}
