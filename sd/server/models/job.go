package models

import "go.mongodb.org/mongo-driver/bson/primitive"

type Job struct {
	ID       primitive.ObjectID `bson:"_id" json:"_id"`
	Path     string             `bson:"path" json:"path"`
	ClientID string             `bson:"clientId" json:"clientId"`

	Step1ChecksJobPayload       *Step1ChecksJobPayload           `bson:"step1ChecksJobPayload" json:"step1ChecksJobPayload"`
	Step2XRFIntensityJobPayload *Step2XRFLineIntensityJobPayload `bson:"step2XRFIntensityJobPayload" json:"step2XRFIntensityJobPayload"`
	Step3PredictionJobPayload   *Step3PredictionJobPayload       `bson:"step3PredictionJobPayload" json:"step3PredictionJobPayload"`
	Step4X2AbundJobPayload      *Step4X2AbundJobPayload          `bson:"step4X2AbundJobPayload" json:"step4X2AbundJobPayload"`
	Step5SRJobPayload           *Step5SRJobPayload               `bson:"step5SRJobPayload" bson:"step5SRJobPayload"`
}

type CreateJob struct {
	ClientID string `json:"clientId"`
}
