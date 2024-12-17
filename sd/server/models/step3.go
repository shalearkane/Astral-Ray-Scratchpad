package models

type Step3PredictionJobPayload struct {
	ClientID string              `json:"clientId" bson:"clientId"`
	Wt       *ElementIntensities `json:"wt" bson:"wt"`
}
