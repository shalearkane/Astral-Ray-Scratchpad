package handler

import (
	"context"
	"log/slog"
	"strings"
	"time"
	"worker/model"

	"github.com/gofiber/fiber/v2"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
)

func (handler *Handler) HandleStartFitsJob(c *fiber.Ctx) error {
	var file model.FitsModel

	flareAlphabet := c.Get("fa", "M")

	// Find not processed file
	handler.Mutex.Lock()
	result := handler.Qm.MongoClient.Database(model.DB).Collection(model.FITS_COLLECTION).FindOneAndUpdate(context.TODO(), bson.M{
		"processingState": model.PROCESSING_STATE_NOT_DONE,
		"flareAlphabet":   flareAlphabet,
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
	handler.Qm.Publish("FITS:"+file.Id.Hex(), int32((30 * time.Second).Milliseconds()))

	filenameSplits := strings.Split(file.Path, "/")

	c.Set("filename", filenameSplits[len(filenameSplits)-1])
	c.Set("id", file.Id.Hex())
	c.Attachment(filenameSplits[len(filenameSplits)-1])
	return c.SendFile(file.Path)
}

func (handler *Handler) HandleFitsDoneJob(c *fiber.Ctx) error {
	var request model.JobDoneInterface
	c.BodyParser(&request)
	id, _ := primitive.ObjectIDFromHex(request.Id)

	fitsModelUpdate := model.FitsModel{
		Lat:             request.Lat,
		Lon:             request.Lon,
		ProcessingState: model.PROCESSING_STATE_DONE,
		Wt:              request.Wt,
		Error:           request.Error,
		PhotonCount:     request.PhotonCount,
	}
	handler.Qm.MongoClient.Database(model.DB).Collection(model.FITS_COLLECTION).FindOneAndUpdate(context.TODO(), bson.M{
		"_id": id,
	}, bson.M{
		"$set": fitsModelUpdate, // It has the abundance data
	}).Decode(request)

	return c.Status(200).JSON(fiber.Map{
		"success": true,
		"data":    request,
	})
}
