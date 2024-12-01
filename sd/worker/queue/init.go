package queue

import (
	"context"

	"github.com/rabbitmq/amqp091-go"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type QueueManager struct {
	Conn        *amqp091.Connection
	Channel     *amqp091.Channel
	MongoClient *mongo.Client
}

func New() (*QueueManager, error) {
	// Connect to RabbitMQ
	conn, err := amqp091.Dial("amqp://guest:guest@localhost:5672/")
	if err != nil {
		return nil, err
	}

	ch, err := conn.Channel()
	if err != nil {
		return nil, err
	}

	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI("mongodb://localhost:27017/ISRO").SetServerAPIOptions(serverAPI)
	// Create a new client and connect to the server
	client, err := mongo.Connect(context.TODO(), opts)
	if err != nil {
		panic(err)
	}

	return &QueueManager{
		Conn:        conn,
		Channel:     ch,
		MongoClient: client,
	}, nil
}

func (q *QueueManager) SetupDelayedQueue() error {
	err := q.Channel.ExchangeDeclare(
		"delayed_exchange",  // Exchange name
		"x-delayed-message", // Exchange type
		true,                // Durable
		false,               // Auto-delete
		false,               // Internal
		false,               // No-wait
		amqp091.Table{"x-delayed-type": "direct"}, // Delayed Exchange-specific argument
	)

	if err != nil {
		return err
	}

	_, err = q.Channel.QueueDeclare(
		"delayed_queue", // Queue name
		true,            // Durable
		false,           // Delete when unused
		false,           // Exclusive
		false,           // No-wait
		nil,
	)

	if err != nil {
		return err
	}

	err = q.Channel.QueueBind(
		"delayed_queue",    // Queue name
		"delayed_routing",  // Routing key
		"delayed_exchange", // Exchange name
		false,
		nil,
	)

	return err
}
