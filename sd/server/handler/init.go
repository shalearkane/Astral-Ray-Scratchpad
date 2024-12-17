package handler

import (
	"context"
	"net/http"
	"os"
	"server/constants"
	"server/models"
	"sync"

	"github.com/gorilla/websocket"
	workqueue "github.com/mevitae/redis-work-queue/go"
	"github.com/redis/go-redis/v9"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Handler struct {
	Step1ChecksJobQueue *workqueue.WorkQueue
	CreateJobQueue      *workqueue.WorkQueue
	Mutex               *sync.Mutex
	Redis               *redis.Client
	MongoClient         *mongo.Client
	ChannelMap          *map[string](chan Message)
}

var Upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true },
	Error:           func(w http.ResponseWriter, r *http.Request, status int, reason error) { return },
}

func NewHandler() *Handler {
	// REDIS QUEUE
	redisClient := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})

	checkQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.STEP1_CHECKS_JOB_QUEUE))
	jobQueue := workqueue.NewWorkQueue(workqueue.KeyPrefix(constants.CREATE_JOB_QUEUE))

	uri := os.Getenv("MONGODB_URI")
	client, err := mongo.Connect(context.TODO(), options.Client().
		ApplyURI(uri))
	if err != nil {
		panic(err)
	}

	var mutex sync.Mutex
	channelMap := make(map[string](chan Message))
	return &Handler{
		Step1ChecksJobQueue: &checkQueue,
		CreateJobQueue:      &jobQueue,
		Mutex:               &mutex,
		Redis:               redisClient,
		MongoClient:         client,
		ChannelMap:          &channelMap,
	}
}

type InitialMessage struct {
	ClientID string `json:"clientId"`
}

type ClientSideMessageType string

const (
	FITS_UPLOAD  ClientSideMessageType = "FITS_UPLOAD"
	CHECK_STATUS ClientSideMessageType = "CHECK_STATUS"
)

/*
Payload will be
- JobID in case of CHECK_STATUS
- Base64 string in case of FITS_UPLOAD
*/
type ClientSideMessage struct {
	Type    ClientSideMessageType `json:"type"`
	Payload string                `json:"payload"`
}

type MessageType string

const (
	CHECK_STATUS_JOB        MessageType = "CHECK_STATUS_JOB"
	CREATE_JOB              MessageType = "CREATE_JOB"
	STEP1_CHECKS_JOB        MessageType = "STEP1_CHECK_JOB"
	STEP2_XRF_INTENSITY_JOB MessageType = "STEP2_XRF_INTENSITY_JOB"
	STEP3_PREDICTION_JOB    MessageType = "STEP3_PREDICTION_JOB"
	STEP4_X2_ABUND_JOB      MessageType = "STEP4_X2_ABUND_JOB"
	STEP5_SR_JOB            MessageType = "STEP5_SR_JOB"
)

type Message struct {
	Type                        MessageType                             `json:"type"`
	ClientID                    string                                  `json:"clientId"`
	JobID                       string                                  `json:"jobId"`
	Step1ChecksJobPayload       *models.Step1ChecksJobPayload           `json:"step1ChecksJobPayload"`
	Step2XRFIntensityJobPayload *models.Step2XRFLineIntensityJobPayload `json:"step2XRFIntensityJobPayload"`
	Step3PredictionJobPayload   *models.Step3PredictionJobPayload       `json:"step3PredictionJobPayload"`
	Step4X2AbundJobPayload      *models.Step4X2AbundJobPayload          `json:"step4X2AbundJobPayload"`
	Step5SRJobPayload           *models.Step5SRJobPayload               `json:"step5SRJobPayload"`
}
