package model

import (
	"go.mongodb.org/mongo-driver/bson/primitive"
)

type FitsModel struct {
	Id              primitive.ObjectID `json:"id" bson:"_id"`
	StartTime       primitive.DateTime `json:"start_time" bson:"start_time"`
	EndTime         primitive.DateTime `json:"end_time" bson:"end_time"`
	ProcessingState ProcessingState    `json:"processingState" bson:"processingState"`
	Path            string             `json:"path"`
	FlareAlphabet   string             `json:"flare_alphabet" bson:"flareAlphabet"`
	FlareScale      float64            `json:"flare_scale" bson:"flareScale"`
	V0LAT           float64            `json:"V0_LAT"`
	V1LAT           float64            `json:"V1_LAT"`
	V2LAT           float64            `json:"V2_LAT"`
	V3LAT           float64            `json:"V3_LAT"`
	V0LON           float64            `json:"V0_LON"`
	V1LON           float64            `json:"V1_LON"`
	V2LON           float64            `json:"V2_LON"`
	V3LON           float64            `json:"V3_LON"`
	SOLARANG        float64            `json:"SOLARANG"`
	EMISNANG        float64            `json:"EMISNANG"`
	PhotonCount     int                `bson:"photonCount" json:"photonCount"`

	// Coordinate
	Lat *float64 `bson:"lat" json:"lat"`
	Lon *float64 `bson:"lon" json:"lon"`

	// Abundance
	Wt    *Element `bson:"wt" json:"wt"`
	Error *Element `bson:"error" json:"error"`
}
