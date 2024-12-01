package main

import (
	"context"
	"fmt"
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

func main() {
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
		docs = append(docs, bson.M{
			"filename":        filename,
			"processingState": model.PROCESSING_STATE_NOT_DONE,
		})
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
