package handler

import (
	"context"
	"log/slog"
	"time"
	"worker/model"

	"github.com/gofiber/fiber/v2"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

func (handler *Handler) HandleStartJob(c *fiber.Ctx) error {
	var file model.FileModel

	// Find not processed file
	handler.Mutex.Lock()
	result := handler.Qm.MongoClient.Database(model.DB).Collection(model.COLLECTION).FindOneAndUpdate(context.TODO(), bson.M{
		"processingState": model.PROCESSING_STATE_NOT_DONE,
	}, bson.M{
		"$set": bson.M{
			"processingState": model.PROCESSING_STATE_PROCESSING,
		},
	})
	handler.Mutex.Unlock()

	err := result.Decode(&file)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			slog.Warn("No documents found")
		} else {
			slog.Error(err.Error())
		}
		c.Status(400).JSON(fiber.Map{
			"error": "No file remaining",
		})
		return nil
	}

	// Publish to the queue
	handler.Qm.Publish(file.Filename, int32((5 * time.Minute).Milliseconds()))

	c.Set("filename", file.Filename)
	c.Attachment(file.Filename)
	return c.SendFile("./files/" + file.Filename)
}

func (handler *Handler) HandleDoneJob(c *fiber.Ctx) error {
	var request model.FileModel
	c.BodyParser(&request)

	request.ProcessingState = model.PROCESSING_STATE_DONE
	handler.Qm.MongoClient.Database(model.DB).Collection(model.COLLECTION).FindOneAndUpdate(context.TODO(), bson.M{
		"filename": request.Filename,
	}, bson.M{
		"$set": request, // It has the abundance data
	}).Decode(request)

	return c.Status(200).JSON(fiber.Map{
		"success": true,
		"data":    request,
	})
}
