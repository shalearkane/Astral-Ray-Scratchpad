package worker

import (
	"sr/constants"

	workqueue "github.com/mevitae/redis-work-queue/go"
	"github.com/redis/go-redis/v9"
)

type Worker struct {
	Redis          *redis.Client
	ListenQueue    *workqueue.WorkQueue
	FinishJobQueue *workqueue.WorkQueue
}

func NewWorker() *Worker {
	redisClient := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})

	finishJobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.STEP5_SR_JOB_QUEUE))
	listenJobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.RECEIVE_JOB_QUEUE))
	return &Worker{
		Redis:          redisClient,
		ListenQueue:    &listenJobQueue,
		FinishJobQueue: &finishJobQueue,
	}
}
