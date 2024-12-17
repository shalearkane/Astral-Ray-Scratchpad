package worker

import (
	"context"
	"encoding/json"
	"sr/geo"

	workqueue "github.com/mevitae/redis-work-queue/go"
)

type Step5SRJobPayload struct {
	ClientID       string            `json:"clientId" bson:"clientId"`
	OriginalPixels []*geo.PointPixel `json:"originalPixels" bson:"originalPixels"`
	SR             []*geo.PointPixel `json:"sr" bson:"sr"`
	Finished       bool              `json:"finished" bson:"finished"`
}

func (worker *Worker) PublishChange(jobId string, publishStruct Step5SRJobPayload) {
	publishStructBytes, _ := json.Marshal(publishStruct)

	worker.FinishJobQueue.AddItem(context.Background(), worker.Redis, workqueue.Item{
		ID:   jobId,
		Data: publishStructBytes,
	})
}
