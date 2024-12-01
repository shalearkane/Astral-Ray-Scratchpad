package pradan

import (
	"context"
	"log/slog"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/go-resty/resty/v2"
	workqueue "github.com/mevitae/redis-work-queue/go"
)

func (pradam *PradanClient) Download(id string, wg *sync.WaitGroup) {
	defer wg.Done()
	client := resty.New()
	id_split := strings.Split(id, "?")
	filePath := "../data/raw" + id_split[0]
	if strings.Contains(filePath, ".zip") {
		filePathParts := strings.Split(filePath, "/")
		filePath = "../data/zips/" + filePathParts[len(filePathParts)-1]
	}

	res, err := client.SetTimeout(5*time.Minute).SetRetryCount(20).R().EnableTrace().SetHeader("Cookie", pradam.Cookies).Get("https://pradan.issdc.gov.in" + id)
	if err != nil {
		// Add the ID back the the queue
		slog.Error(err.Error())
		if err := (*pradam.DownloadIdsQueue).Publish(id); err != nil {
			slog.Error("failed to publish: %s", err)
		}
		return
	}
	err = os.WriteFile(filePath, res.Body(), 0777)
	if err != nil {
		// Add the ID back the the queue
		slog.Error(err.Error())
		if err := (*pradam.DownloadIdsQueue).Publish(id); err != nil {
			slog.Error("failed to WRITE: %s", err)
		}
		return
	}

	// Publish the the external queues
	filePathParts := strings.Split(filePath, ".")
	switch filePathParts[len(filePathParts)-1] { // Checking extension for if it needs to be directly processed or uncompressed first
	case "zip":
		pradam.FilePathToUnzipQueue.AddItem(context.TODO(), pradam.RedisClient, workqueue.NewItem([]byte(filePath)))
		return
	default:
		pradam.DownloadCompleteQueue.AddItem(context.TODO(), pradam.RedisClient, workqueue.NewItem([]byte(filePath)))
	}
}

func (pradan *PradanClient) DownloadAll(ids []string) {
	var wg sync.WaitGroup
	for _, id := range ids {
		wg.Add(1)
		go pradan.Download(id, &wg)
	}
	wg.Wait()
}
