package queue

import "github.com/rabbitmq/amqp091-go"

func (q *QueueManager) Publish(message string, delay int32) error {
	return q.Channel.Publish(
		"delayed_exchange", // Exchange name
		"delayed_routing",  // Routing key
		false,              // Mandatory
		false,              // Immediate
		amqp091.Publishing{
			ContentType: "text/plain",
			Body:        []byte(message),
			Headers: amqp091.Table{
				"x-delay": delay, // Delay in milliseconds
			},
		},
	)
}
