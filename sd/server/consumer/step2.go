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

func (consumer *Consumer) ProcessStep2XRFIntensity(jobItem *workqueue.Item) {
	jobId, _ := primitive.ObjectIDFromHex(jobItem.ID)

	var step2XRFIntensityPayload models.Step2XRFLineIntensityJobPayload
	json.Unmarshal(jobItem.Data, &step2XRFIntensityPayload)

	// Update the DB
	consumer.Handler.MongoClient.Database(constants.DB).Collection(constants.COLLECTION).FindOneAndUpdate(context.Background(), bson.M{
		"_id": jobId,
	}, bson.M{
		"$set": bson.M{
			"step2XRFIntensityJobPayload": step2XRFIntensityPayload,
		},
	})

	// Update to the peer connection
	(*consumer.Handler.ChannelMap)[step2XRFIntensityPayload.ClientID] <- handler.Message{
		Type:                        handler.STEP2_XRF_INTENSITY_JOB,
		JobID:                       jobId.Hex(),
		ClientID:                    step2XRFIntensityPayload.ClientID,
		Step2XRFIntensityJobPayload: &step2XRFIntensityPayload,
	}

	// Finish the job
	_, err := consumer.Step2XRFIntensityJobQueue.Complete(context.Background(), consumer.Redis, jobItem)
	if err != nil {
		slog.Error(err.Error())
	}
}
