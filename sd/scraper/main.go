package main

import (
	"context"
	"log/slog"
	"os"
	"scraper/pradan"
	"scraper/workers"

	"github.com/joho/godotenv"
	"github.com/redis/go-redis/v9"
	"github.com/robfig/cron"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func main() {
	// Load the .env file
	godotenv.Load()

	// REDIS QUEUE
	redisClient := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})

	// MONGODB
	uri := os.Getenv("MONGODB_URI")
	client, err := mongo.Connect(context.TODO(), options.Client().
		ApplyURI(uri))
	if err != nil {
		panic(err)
	}

	pradanClient, err := pradan.NewPradanClient(redisClient)
	if err != nil {
		slog.Error("Can't LOGIN to pradan", err)
		return
	}

	worker := workers.NewWorker(client, redisClient, pradanClient)

	// CRON to keep logged in -> DOES every 4 mins
	// CRON to fetch new data -> DOES every 4 days
	cron := cron.New()
	cron.AddFunc("@every 4m", pradanClient.AutoUpdate)
	cron.AddFunc("@every 4d", worker.CheckForNewData)
	cron.Start()

	go worker.CheckForNewData() // -> Triggered once during startup
	worker.StartConsuming()
}
