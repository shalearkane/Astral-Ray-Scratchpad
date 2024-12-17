package handler

import (
	"context"
	"encoding/json"
	"server/constants"
	"server/fs"
	"server/models"

	"github.com/google/uuid"
	workqueue "github.com/mevitae/redis-work-queue/go"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

func (handler *Handler) HandleCreateJob(clientId, base64File string) {
	// Each file should have a new filename
	filePath := "../tmp/" + uuid.NewString() + ".fits"
	fs.WriteBase64(base64File, filePath)

	objId := primitive.NewObjectID()
	objIdString := objId.Hex()
	handler.MongoClient.Database(constants.DB).Collection(constants.COLLECTION).InsertOne(context.Background(), models.Job{
		ID:       objId,
		ClientID: clientId,
		Path:     filePath,
	})

	createJobInterface := models.CreateJob{
		ClientID: clientId,
	}

	createJobBytes, _ := json.Marshal(createJobInterface)

	handler.CreateJobQueue.AddItem(context.Background(), handler.Redis, workqueue.Item{
		ID:   objIdString,
		Data: createJobBytes,
	})

	(*handler.ChannelMap)[clientId] <- Message{
		Type:     CREATE_JOB,
		JobID:    objIdString,
		ClientID: clientId,
	}
}
