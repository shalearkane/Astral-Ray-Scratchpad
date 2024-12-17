package consumer

import (
	"server/constants"
	"server/handler"

	"github.com/redis/go-redis/v9"

	workqueue "github.com/mevitae/redis-work-queue/go"
)

type Consumer struct {
	Redis                     *redis.Client
	Step1CheckJobQueue        *workqueue.WorkQueue
	Step2XRFIntensityJobQueue *workqueue.WorkQueue
	Step3PredictionJobQueue   *workqueue.WorkQueue
	Step4X2AbundJobQueue      *workqueue.WorkQueue
	Step5SRJobQueue           *workqueue.WorkQueue
	Handler                   *handler.Handler
}

func NewConsumer(handler *handler.Handler) *Consumer {
	// REDIS QUEUE
	redisClient := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})

	step1ChecksJobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.STEP1_CHECKS_JOB_QUEUE))
	step2XRFIntensityJobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.STEP2_XRF_LINE_INTENSITY_JOB_QUEUE))
	step3PredictionJobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.STEP3_PREDICTION_JOB_QUEUE))
	step4X2AbundJobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.STEP4_X2_ABUND_JOB_QUEUE))
	step5STJobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.STEP5_SR_JOB_QUEUE))
	return &Consumer{
		Step1CheckJobQueue:        &step1ChecksJobQueue,
		Step2XRFIntensityJobQueue: &step2XRFIntensityJobQueue,
		Step3PredictionJobQueue:   &step3PredictionJobQueue,
		Step4X2AbundJobQueue:      &step4X2AbundJobQueue,
		Step5SRJobQueue:           &step5STJobQueue,
		Redis:                     redisClient,
		Handler:                   handler,
	}
}
