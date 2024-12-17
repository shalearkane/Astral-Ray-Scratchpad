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

func (consumer *Consumer) ProcessStep3Prediction(jobItem *workqueue.Item) {
	jobId, _ := primitive.ObjectIDFromHex(jobItem.ID)

	var step3PredictionJobPayload models.Step3PredictionJobPayload
	json.Unmarshal(jobItem.Data, &step3PredictionJobPayload)

	// Update the DB
	consumer.Handler.MongoClient.Database(constants.DB).Collection(constants.COLLECTION).FindOneAndUpdate(context.Background(), bson.M{
		"_id": jobId,
	}, bson.M{
		"$set": bson.M{
			"step3PredictionJobPayload": step3PredictionJobPayload,
		},
	})

	// Update to the peer connection
	(*consumer.Handler.ChannelMap)[step3PredictionJobPayload.ClientID] <- handler.Message{
		Type:                      handler.STEP3_PREDICTION_JOB,
		JobID:                     jobId.Hex(),
		ClientID:                  step3PredictionJobPayload.ClientID,
		Step3PredictionJobPayload: &step3PredictionJobPayload,
	}

	// Finish the job
	_, err := consumer.Step3PredictionJobQueue.Complete(context.Background(), consumer.Redis, jobItem)
	if err != nil {
		slog.Error(err.Error())
	}
}
