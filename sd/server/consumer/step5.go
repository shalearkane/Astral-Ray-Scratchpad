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

func (consumer *Consumer) ProcessStep5SR(jobItem *workqueue.Item) {
	jobId, _ := primitive.ObjectIDFromHex(jobItem.ID)

	var step5SRJobPayload models.Step5SRJobPayload
	json.Unmarshal(jobItem.Data, &step5SRJobPayload)

	// Update the DB
	consumer.Handler.MongoClient.Database(constants.DB).Collection(constants.COLLECTION).FindOneAndUpdate(context.Background(), bson.M{
		"_id": jobId,
	}, bson.M{
		"$set": bson.M{
			"step5SRJobPayload": step5SRJobPayload,
		},
	})

	// Update to the peer connection
	(*consumer.Handler.ChannelMap)[step5SRJobPayload.ClientID] <- handler.Message{
		Type:              handler.STEP5_SR_JOB,
		JobID:             jobId.Hex(),
		ClientID:          step5SRJobPayload.ClientID,
		Step5SRJobPayload: &step5SRJobPayload,
	}

	// Finish the job
	_, err := consumer.Step5SRJobQueue.Complete(context.Background(), consumer.Redis, jobItem)
	if err != nil {
		slog.Error(err.Error())
	}
}
