package models

type PlotCell struct {
	ChannelNumber int     `json:"channelNumber" bson:"channelNumber"`
	Count         float64 `json:"count" bson:"count"`
}

type ElementPlottings struct {
	Mg *[]PlotCell `json:"mg" bson:"mg"`
	Al *[]PlotCell `json:"al" bson:"al"`
	Si *[]PlotCell `json:"si" bson:"si"`
	Ca *[]PlotCell `json:"ca" bson:"ca"`
	Ti *[]PlotCell `json:"ti" bson:"ti"`
	Fe *[]PlotCell `json:"fe" bson:"fe"`
}

type Step1ChecksJobPayload struct {
	ClientID    string           `json:"clientId" bson:"clientId"`
	PhotonCount float64          `json:"photonCount" bson:"photonCount"`
	Geotail     bool             `json:"geotail" bson:"geotail"`
	Peaks       ElementPlottings `json:"peaks" bson:"peaks"`
	FitsPlot    []PlotCell       `json:"fitsPlot" bson:"fitsPlot"`
}
