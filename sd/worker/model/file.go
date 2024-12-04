package model

type ProcessingState string

const (
	PROCESSING_STATE_DONE       ProcessingState = "DONE"
	PROCESSING_STATE_NOT_DONE   ProcessingState = "NOT_DONE"
	PROCESSING_STATE_PROCESSING ProcessingState = "PROCESSING"
)

type Element struct {
	Fe   *float64 `bson:"fe" json:"Wt_Fe"`
	Al   *float64 `bson:"al" json:"Wt_Al"`
	Si   *float64 `bson:"si" json:"Wt_Si"`
	Mg   *float64 `bson:"mg" json:"Wt_Mg"`
	Na   *float64 `bson:"na" json:"Wt_Na"`
	O    *float64 `bson:"o" json:"Wt_O"`
	Ca   *float64 `bson:"ca" json:"Wt_Ca"`
	Ti   *float64 `bson:"ti" json:"Wt_Ti"`
	Norm *float64 `bson:"norm" json:"norm"`
}

type FileModel struct {
	Filename        string          `bson:"filename" json:"filename"`
	ProcessingState ProcessingState `bson:"processingState" json:"processingState"`

	// Coordinate
	Lat *float64 `bson:"lat" json:"lat"`
	Lon *float64 `bson:"lon" json:"lon"`

	// Abundance
	Wt    *Element `bson:"wt" json:"wt"`
	Error *Element `bson:"error" json:"error"`
}

type JobDoneInterface struct {
	Id       string `bson:"_id" json:"filename"`
	Filename string `bson:"filename" json:"filename"`

	// Coordinate
	Lat *float64 `bson:"lat" json:"lat"`
	Lon *float64 `bson:"lon" json:"lon"`

	// Abundance
	Wt    *Element `bson:"wt" json:"wt"`
	Error *Element `bson:"error" json:"error"`

	// Metadata
	PhotonCount int `bson:"photonCount" json:"photonCount"`
}
