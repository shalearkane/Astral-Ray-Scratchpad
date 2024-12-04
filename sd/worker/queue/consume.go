package queue

import (
	"context"
	"log"
	"log/slog"
	"strings"
	"worker/model"

	"github.com/rabbitmq/amqp091-go"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

func (q *QueueManager) Consume() error {
	msgs, err := q.Channel.Consume(
		"delayed_queue", // Queue name
		"",              // Consumer tag
		false,           // Auto-ack
		false,           // Exclusive
		false,           // No-local
		false,           // No-wait
		nil,
	)

	if err != nil {
		return err
	}

	log.Println("Waiting for messages. Press CTRL+C to exit.")

	for msg := range msgs {
		body := string(msg.Body)
		if strings.Contains(body, "FITS:") {
			go q.UpdateFitsProcessingState(strings.ReplaceAll(body, "FITS:", ""), &msg)
		} else {
			go q.UpdateProcessingState(body, &msg)
		}
	}

	return nil
}

func (q *QueueManager) UpdateProcessingState(filename string, delivery *amqp091.Delivery) {
	result, err := q.MongoClient.Database(model.DB).Collection(model.COLLECTION).UpdateOne(context.Background(), bson.M{
		"filename":        filename,
		"processingState": model.PROCESSING_STATE_PROCESSING,
	}, bson.M{
		"$set": bson.M{
			"processingState": model.PROCESSING_STATE_NOT_DONE,
		},
	})

	if err != nil {
		slog.Error(err.Error())
		return
	}

	if result.MatchedCount > 0 {
		slog.Warn("File not processed on time - " + filename)
	}

	delivery.Ack(false)
}

func (q *QueueManager) UpdateFitsProcessingState(id string, delivery *amqp091.Delivery) {
	objId, _ := primitive.ObjectIDFromHex(id)
	result, err := q.MongoClient.Database(model.DB).Collection(model.FITS_COLLECTION).UpdateOne(context.Background(), bson.M{
		"_id":             objId,
		"processingState": model.PROCESSING_STATE_PROCESSING,
	}, bson.M{
		"$set": bson.M{
			"processingState": model.PROCESSING_STATE_NOT_DONE,
		},
	})

	if err != nil {
		slog.Error(err.Error())
		return
	}

	if result.MatchedCount > 0 {
		slog.Warn("File not processed on time - " + id)
	}

	delivery.Ack(false)
}
