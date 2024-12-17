package handler

import (
	"log"
	"net/http"

	"github.com/gorilla/websocket"
	"github.com/k0kubun/pp/v3"
)

func (handler *Handler) HandleWebsocketConn(w http.ResponseWriter, r *http.Request) {
	conn, err := Upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}

	var initialMessage InitialMessage
	conn.ReadJSON(&initialMessage)
	pp.Println(initialMessage.ClientID)

	channel := make(chan Message, 1)

	(*handler).Mutex.Lock()
	(*handler.ChannelMap)[initialMessage.ClientID] = channel
	(*handler).Mutex.Unlock()

	// Consume all the updates from other servers and send info to client
	go ConsumeUpdates(conn, &channel)

	// Listen for more messages from client -> Maybe the client has uploaded more fits files
	// Note that this is only for reading messages and no writing should be done
	for {
		var clientMessage ClientSideMessage
		err := conn.ReadJSON(&clientMessage)

		if err != nil {
			conn.Close()
			return
		}

		// pp.Println(err)
		if clientMessage.Type == FITS_UPLOAD {
			go handler.HandleCreateJob(initialMessage.ClientID, clientMessage.Payload)
		}
		if clientMessage.Type == CHECK_STATUS {
			go handler.GetStatusById(initialMessage.ClientID, clientMessage.Payload)
		}
	}

}

func ConsumeUpdates(conn *websocket.Conn, channel *chan Message) {
	for message := range *channel {
		pp.Println(message)
		conn.WriteJSON(message)
	}
}
