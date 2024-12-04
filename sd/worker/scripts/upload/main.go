package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"os"
	"sort"
	"strconv"
	"strings"
	"worker/model"

	"github.com/k0kubun/pp/v3"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

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
	abundances, err := getAlreadyDoneAbundanceData()
	if err != nil {
		slog.Error(err.Error())
	}

	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI("mongodb://localhost:27017/ISRO").SetServerAPIOptions(serverAPI)
	// Create a new client and connect to the server
	client, err := mongo.Connect(context.TODO(), opts)
	if err != nil {
		panic(err)
	}

	files, err := os.ReadDir("./files")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	entryMap := make(map[int]map[int]string)
	latEntries := make(map[int][]int)

	var lats []int

	for _, entry := range files {
		coords := strings.Split(strings.ReplaceAll(entry.Name(), ".fits", ""), "_")
		if len(coords) < 2 {
			continue
		}
		lat, err := strconv.Atoi(strings.ReplaceAll(coords[0], ".", ""))
		if err != nil {
			continue
		}
		lon, err := strconv.Atoi(strings.ReplaceAll(coords[1], ".", ""))
		if err != nil {
			continue
		}
		if entryMap[lat] == nil {
			entryMap[lat] = make(map[int]string)
			latEntries[lat] = []int{}
			lats = append(lats, lat)
		}

		entryMap[lat][lon] = entry.Name()
		latEntries[lat] = append(latEntries[lat], lon)
	}

	sort.Slice(lats, func(i, j int) bool {
		return lats[i] < lats[j]
	})

	var fileNames []string
	latIdx := 0

	for latIdx < len(lats) {
		lat := lats[latIdx]
		sort.Slice(latEntries[lat], func(i, j int) bool {
			return latEntries[lat][i] < latEntries[lat][j]
		})

		for lonIdx := 0; lonIdx < len(latEntries[lat]); lonIdx = lonIdx + 3 {
			fileNames = append(fileNames, entryMap[lat][latEntries[lat][lonIdx]])
		}

		latIdx = latIdx + 3
	}

	var docs []interface{}
	for _, filename := range fileNames {
		if (*abundances)[filename] == nil {
			docs = append(docs, bson.M{
				"filename":        filename,
				"processingState": model.PROCESSING_STATE_NOT_DONE,
			})
		} else {
			docs = append(docs, (*abundances)[filename])
		}

	}

	result, err := client.Database(model.DB).Collection(model.COLLECTION).InsertMany(context.Background(), docs)

	if err != nil {
		panic(err)
	}

	pp.Println("Inserted docs count: %d", len(result.InsertedIDs))

	for _, id := range result.InsertedIDs {
		pp.Println(id.(primitive.ObjectID).Hex())
	}
}
