package pradan

import (
	"log/slog"
	"sync"

	"github.com/adjust/rmq/v5"
	workqueue "github.com/mevitae/redis-work-queue/go"
	"github.com/redis/go-redis/v9"
)

type PradanClient struct {
	Cookies               string
	ClassViewState        string
	XSMViewState          string
	ClassTimeStart        string
	ClassTimeEnd          string
	XSMTimeStart          string
	XSMTimeEnd            string
	RedisClient           *redis.Client
	DownloadIdsQueue      *rmq.Queue
	DownloadCompleteQueue *workqueue.WorkQueue
	FilePathToUnzipQueue  *workqueue.WorkQueue
}

func NewPradanClient(redisClient *redis.Client) (*PradanClient, error) {
	// Internal Message Transfer
	errChan := make(chan error, 10)
	connection, err := rmq.OpenConnectionWithRedisClient("queue", redisClient, errChan)
	if err != nil {
		slog.Error("%v", err)
	}
	idsToDownloadQueue, err := connection.OpenQueue(CH2_IDS_TO_DOWNLOAD)
	if err != nil {
		slog.Error("%v", err)
	}

	// External message Transfer
	filePathToUnzipQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(FILE_PATH_TO_UNZIP))
	downloadCompleteQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(DOWNLOAD_COMPLETE))

	cookies, err := Login()
	if err != nil {
		return nil, err
	}

	pradanClient := PradanClient{
		Cookies:               *cookies,
		RedisClient:           redisClient,
		DownloadIdsQueue:      &idsToDownloadQueue,
		DownloadCompleteQueue: &downloadCompleteQueue,
		FilePathToUnzipQueue:  &filePathToUnzipQueue,
	}

	return &pradanClient, nil
}

func (pradan *PradanClient) AutoUpdate() {
	cookies, err := Login()
	if err != nil {
		slog.Error("Unable to AUTO-UPDATE pradanClient", err)
		return
	}

	pradan.Cookies = *cookies
	pradan.updateViewStates()
	slog.Info("AUTO-UPDATED pradanClient")

}

func (pradan *PradanClient) updateViewStates() {
	var wg sync.WaitGroup
	classViewState := ""
	xsmViewState := ""
	wg.Add(2)
	go pradan.GetClassViewState(&classViewState, &wg)
	go pradan.GetXSMViewState(&xsmViewState, &wg)
	wg.Wait()

	pradan.ClassViewState = classViewState
	pradan.XSMViewState = xsmViewState
}
