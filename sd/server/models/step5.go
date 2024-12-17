package models

type LatLon struct {
	Lat float64 `json:"lat" bson:"lat"`
	Lon float64 `json:"lon" bson:"lon"`
}

type Box struct {
	BottomLeft  LatLon `json:"bottomLeft" bson:"bottomLeft"`
	BottomRight LatLon `json:"bottomRight" bson:"bottomRight"`
	TopLeft     LatLon `json:"topLeft" bson:"topLeft"`
	TopRight    LatLon `json:"topRight" bson:"topRight"`
}

type PointPixel struct {
	BoundingBox *Box     `json:"boundingBox" bson:"boundingBox"`
	Wt          *Element `json:"wt" bson:"wt"`
	ID          string   `json:"id" bson:"id"`
	Center      LatLon   `json:"latlon" bson:"latlon"`
}

type Step5SRJobPayload struct {
	ClientID       string        `json:"clientId" bson:"clientId"`
	OriginalPixels []*PointPixel `json:"originalPixels" bson:"originalPixels"`
	SR             []*PointPixel `json:"sr" bson:"sr"`
	Finished       bool          `json:"finished" bson:"finished"`
}
