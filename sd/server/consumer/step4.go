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

func (consumer *Consumer) ProcessStep4X2Abund(jobItem *workqueue.Item) {
	jobId, _ := primitive.ObjectIDFromHex(jobItem.ID)

	var step4X2AbundJobPayload models.Step4X2AbundJobPayload
	json.Unmarshal(jobItem.Data, &step4X2AbundJobPayload)

	// Update the DB
	consumer.Handler.MongoClient.Database(constants.DB).Collection(constants.COLLECTION).FindOneAndUpdate(context.Background(), bson.M{
		"_id": jobId,
	}, bson.M{
		"$set": bson.M{
			"step4X2AbundJobPayload": step4X2AbundJobPayload,
		},
	})

	// Update to the peer connection
	(*consumer.Handler.ChannelMap)[step4X2AbundJobPayload.ClientID] <- handler.Message{
		Type:                   handler.STEP4_X2_ABUND_JOB,
		JobID:                  jobId.Hex(),
		ClientID:               step4X2AbundJobPayload.ClientID,
		Step4X2AbundJobPayload: &step4X2AbundJobPayload,
	}

	// Finish the job
	_, err := consumer.Step4X2AbundJobQueue.Complete(context.Background(), consumer.Redis, jobItem)
	if err != nil {
		slog.Error(err.Error())
	}
}
