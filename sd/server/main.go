package main

import (
	"net/http"
	"server/consumer"
	"server/handler"

	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()
	handler := handler.NewHandler()
	consumer := consumer.NewConsumer(handler)
	go consumer.ListenForMessages()
	http.HandleFunc("/", handler.HandleWebsocketConn)

	http.ListenAndServe("0.0.0.0:5000", nil)
}
