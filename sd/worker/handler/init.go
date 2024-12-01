package handler

import (
	"sync"
	"worker/queue"
)

type Handler struct {
	Qm    *queue.QueueManager
	Mutex *sync.Mutex
}
