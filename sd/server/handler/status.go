package handler

import (
	"context"
	"server/constants"
	"server/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

func (handler *Handler) GetStatusById(clientId, jobId string) {
	var job models.Job

	objId, _ := primitive.ObjectIDFromHex(jobId)
	handler.MongoClient.Database(constants.DB).Collection(constants.COLLECTION).FindOne(context.Background(), bson.M{
		"_id": objId,
	}).Decode(&job)

	(*handler.ChannelMap)[clientId] <- Message{
		Type:                        CHECK_STATUS_JOB,
		JobID:                       jobId,
		ClientID:                    clientId,
		Step1ChecksJobPayload:       job.Step1ChecksJobPayload,
		Step2XRFIntensityJobPayload: job.Step2XRFIntensityJobPayload,
		Step4X2AbundJobPayload:      job.Step4X2AbundJobPayload,
		Step5SRJobPayload:           job.Step5SRJobPayload,
	}
}
