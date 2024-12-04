package main

import (
	"log"
	"sync"
	"worker/handler"
	"worker/queue"

	"github.com/gofiber/fiber/v2"
)

func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func main() {
	queueManager, err := queue.New()
	if err != nil {
		panic(err)
	}

	defer queueManager.Conn.Close()
	defer queueManager.Channel.Close()

	// Set up delayed queue
	err = queueManager.SetupDelayedQueue()
	if err != nil {
		panic(err)
	}

	// Start consuming messages
	go queueManager.Consume()

	// Initialize the server
	app := fiber.New(fiber.Config{
		Prefork: false,
	})

	// Initialize the handler
	var mutex sync.Mutex
	handler := handler.Handler{
		Qm:    queueManager,
		Mutex: &mutex,
	}

	app.Get("/new", handler.HandleStartJob)
	app.Post("/done", handler.HandleDoneJob)

	app.Get("/fits/new", handler.HandleStartFitsJob)
	app.Post("/fits/done", handler.HandleFitsDoneJob)

	app.Listen(":8082")
}
