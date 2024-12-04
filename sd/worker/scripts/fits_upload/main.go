package main

import (
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"os"
	"strings"
	"time"
	"worker/model"

	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Date struct {
	Date string `json:"$date"`
}

type FitsDataWithManualDate struct {
	StartTime Date `json:"start_time" bson:"start_time"`
	EndTime   Date `json:"end_time" bson:"end_time"`

	Path          string  `json:"path"`
	FlareAlphabet string  `json:"flare_alphabet"`
	FlareScale    float64 `json:"flare_scale"`
	V0LAT         float64 `json:"V0_LAT"`
	V1LAT         float64 `json:"V1_LAT"`
	V2LAT         float64 `json:"V2_LAT"`
	V3LAT         float64 `json:"V3_LAT"`
	V0LON         float64 `json:"V0_LON"`
	V1LON         float64 `json:"V1_LON"`
	V2LON         float64 `json:"V2_LON"`
	V3LON         float64 `json:"V3_LON"`
	SOLARANG      float64 `json:"SOLARANG"`
	EMISNANG      float64 `json:"EMISNANG"`
}

func (fits *FitsDataWithManualDate) ToFitsModel() model.FitsModel {
	startTime, _ := time.Parse(time.RFC3339, fits.StartTime.Date)
	endTime, _ := time.Parse(time.RFC3339, fits.EndTime.Date)

	return model.FitsModel{
		StartTime:       primitive.DateTime(startTime.Unix()),
		EndTime:         primitive.DateTime(endTime.Unix()),
		ProcessingState: model.PROCESSING_STATE_NOT_DONE,
		Path:            strings.ReplaceAll(fits.Path, "../files/", "../class_data/files/"),
		FlareAlphabet:   fits.FlareAlphabet,
		FlareScale:      fits.FlareScale,
		V0LAT:           fits.V0LAT,
		V1LAT:           fits.V1LAT,
		V2LAT:           fits.V2LAT,
		V3LAT:           fits.V3LAT,
		V0LON:           fits.V0LON,
		V1LON:           fits.V1LON,
		V2LON:           fits.V2LON,
		V3LON:           fits.V3LON,
		SOLARANG:        fits.SOLARANG,
		EMISNANG:        fits.EMISNANG,
	}
}

func getAlreadyDoneAbundanceData() (*map[string]*model.FileModel, error) {
	files, err := os.ReadDir("./abundance_jsons")
	if err != nil {
		return nil, err
	}

	abundances := make(map[string]*model.FileModel)

	for _, file := range files {
		jsonFile, err := os.Open("./abundance_jsons/" + file.Name())
		if err != nil {
			slog.Error(err.Error())
			continue
		}

		defer jsonFile.Close()

		byteValue, _ := io.ReadAll(jsonFile)

		var abundance model.FileModel
		json.Unmarshal(byteValue, &abundance)

		abundance.ProcessingState = model.PROCESSING_STATE_DONE
		abundances[abundance.Filename] = &abundance
	}

	return &abundances, nil
}

func main() {
	// abundances, err := getAlreadyDoneAbundanceData()
	// if err != nil {
	// 	slog.Error(err.Error())
	// }

	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI("mongodb://localhost:27017/ISRO").SetServerAPIOptions(serverAPI)
	// // Create a new client and connect to the server
	client, err := mongo.Connect(context.TODO(), opts)
	if err != nil {
		panic(err)
	}

	file, err := os.Open("./ISRO.class_fits_flare_classified.json")
	if err != nil {
		return
	}
	defer file.Close()

	var fitsFiles []FitsDataWithManualDate
	json.NewDecoder(file).Decode(&fitsFiles)

	var fitsInterface []interface{}
	for _, fits := range fitsFiles {
		fitsInterface = append(fitsInterface, fits.ToFitsModel())
	}

	client.Database(model.DB).Collection(model.FITS_COLLECTION).InsertMany(context.Background(), fitsInterface)
}
