package models

type Step4X2AbundJobPayload struct {
	ClientID string              `json:"clientId" bson:"clientId"`
	Wt       *ElementIntensities `json:"wt" bson:"wt"`
	Error    *ElementIntensities `json:"error" bson:"error"`
}
