package worker

import (
	"context"
	"encoding/json"
	"log/slog"
	"math"
	"sr/geo"
	"sr/resolution"
	"time"

	"github.com/golang/geo/s2"
	"github.com/k0kubun/pp/v3"
	workqueue "github.com/mevitae/redis-work-queue/go"
)

type Abundance struct {
	Lat float64     `json:"lat"`
	Lon float64     `json:"lon"`
	Wt  geo.Element `json:"wt"`
}

type ListenToStruct struct {
	ClientID string      `json:"clientId"`
	Patch    []Abundance `json:"patch"`
	Box      geo.Box     `json:"box"`
}

func (worker *Worker) Listen() {
	for {
		job, err := worker.ListenQueue.Lease(context.Background(), worker.Redis, true, 0, 20*time.Minute)
		if err != nil {
			slog.Error(err.Error())
		}
		go worker.ProcessSR(job)
	}
}

func (worker *Worker) ProcessSR(jobItem *workqueue.Item) {
	slog.Info("RECEIVED SR PACKET")

	var listenToStruct ListenToStruct
	json.Unmarshal(jobItem.Data, &listenToStruct)

	var latlons []*resolution.LatLonWt
	for _, abund := range listenToStruct.Patch {
		latlons = append(latlons, &resolution.LatLonWt{
			LatLngs: s2.LatLngFromDegrees(abund.Lat, abund.Lon),
			Wt:      abund.Wt,
		})
	}

	updateChannel := make(chan *resolution.PointResolutionManager, 1)

	config := resolution.PointResolutionManagerConfig{
		JobID:         jobItem.ID,
		ClientID:      listenToStruct.ClientID,
		UpdateChannel: updateChannel,
		LatLngs:       latlons,
		Radius:        1.0,
		SubPixelLen:   12.5 * 1e-5 * 180 / (math.Pi),
		Box:           listenToStruct.Box,
	}
	resManager := resolution.NewPointResolutionManager(config)
	originalData := *resManager.PointPixels
	go worker.PublishChange(jobItem.ID, Step5SRJobPayload{
		ClientID:       listenToStruct.ClientID,
		OriginalPixels: originalData,
		Finished:       false,
	})
	go ProcessPatch(resManager, updateChannel)

	for event := range updateChannel {
		worker.PublishChange(jobItem.ID, Step5SRJobPayload{
			ClientID:       listenToStruct.ClientID,
			SR:             *event.PointPixels,
			OriginalPixels: originalData,
			Finished:       event.Finished,
		})
		if event.Finished == true {
			break
		}
		slog.Info("DONE SR")
	}

	_, err := worker.ListenQueue.Complete(context.Background(), worker.Redis, jobItem)
	if err != nil {
		slog.Error(err.Error())
	}
}

func ProcessPatch(rm *resolution.PointResolutionManager, updateChannel chan *resolution.PointResolutionManager) {
	rm.SaveCSV("./output.csv")
	pp.Println(len(*rm.PointPixels))
	rm.Fill()
	pp.Println(len(*rm.PointPixels))

	rm.EnhancePixels()
	rm.SaveCSV("./output.csv")
	rm.Finished = true
	updateChannel <- rm
}
