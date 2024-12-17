package models

type ElementIntensities struct {
	Mg *float64 `json:"mg" bson:"mg"`
	Al *float64 `json:"al" bson:"al"`
	Si *float64 `json:"si" bson:"si"`
	Ca *float64 `json:"ca" bson:"ca"`
	Ti *float64 `json:"ti" bson:"ti"`
	Fe *float64 `json:"fe" bson:"fe"`
}

type Step2XRFLineIntensityJobPayload struct {
	ClientID  string             `json:"clientId" bson:"clientId"`
	Intensity ElementIntensities `json:"intensity" bson:"intensity"`
	Fitting   ElementPlottings   `json:"fitting" bson:"fitting"`
	ChiSquare ElementIntensities `json:"chi_2" bson:"chi_2"`
	DoF       ElementIntensities `json:"dof" json:"dof"`
}
