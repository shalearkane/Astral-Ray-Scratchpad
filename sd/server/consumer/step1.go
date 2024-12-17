package consumer

import (
	"context"
	"encoding/json"
	"log/slog"
	"server/constants"
	"server/handler"
	"server/models"

	workqueue "github.com/mevitae/redis-work-queue/go"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

func (consumer *Consumer) ProcessStep1Checks(jobItem *workqueue.Item) {
	jobId, _ := primitive.ObjectIDFromHex(jobItem.ID)

	var step1CheckJobPayload models.Step1ChecksJobPayload
	json.Unmarshal(jobItem.Data, &step1CheckJobPayload)

	// Update the DB
	consumer.Handler.MongoClient.Database(constants.DB).Collection(constants.COLLECTION).FindOneAndUpdate(context.Background(), bson.M{
		"_id": jobId,
	}, bson.M{
		"$set": bson.M{
			"step1ChecksJobPayload": step1CheckJobPayload,
		},
	})

	// Update to the peer connection
	(*consumer.Handler.ChannelMap)[step1CheckJobPayload.ClientID] <- handler.Message{
		Type:                  handler.STEP1_CHECKS_JOB,
		JobID:                 jobId.Hex(),
		Step1ChecksJobPayload: &step1CheckJobPayload,
	}

	// Finish the job
	_, err := consumer.Step1CheckJobQueue.Complete(context.Background(), consumer.Redis, jobItem)
	if err != nil {
		slog.Error(err.Error())
	}
}
