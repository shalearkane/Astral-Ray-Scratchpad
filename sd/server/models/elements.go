package models

type Element struct {
	Ti *float64 `bson:"ti" json:"ti"`
	Si *float64 `bson:"si" json:"si"`
	Fe *float64 `bson:"fe" json:"fe"`
	Al *float64 `bson:"al" json:"al"`
	Mg *float64 `bson:"mg" json:"mg"`
	Ca *float64 `bson:"ca" json:"ca"`
}
