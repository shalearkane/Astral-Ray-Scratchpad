package workers

import (
	"log"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/adjust/rmq/v5"
)

func (worker *Worker) Consume(batch rmq.Deliveries) {
	worker.PradanClient.DownloadAll(batch.Payloads())
	errors := batch.Ack()
	if len(errors) != 0 {
		slog.Error("Can't ACK %v", errors)
		return
	}
}

func (worker *Worker) StartConsuming() {
	errChan := make(chan error, 10)
	go logErrors(errChan)

	slog.Info("Starting to CONSUME")

	if err := (*worker.DownloadIdsQueue).StartConsuming(PREFETCH_LIMIT, POLL_DURATION); err != nil {
		slog.Error("Can't START CONSUMING to queue", err)
		return
	}

	if _, err := (*worker.DownloadIdsQueue).AddBatchConsumer(CH2_IDS_TO_DOWNLOAD, PREFETCH_LIMIT, POLL_DURATION, worker); err != nil {
		panic(err)
	}

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT)
	defer signal.Stop(signals)

	<-signals // wait for signal
	go func() {
		<-signals // hard exit on second signal (in case shutdown gets stuck)
		os.Exit(1)
	}()

	<-(*worker.DownloadIdsQueue).StopConsuming() // wait for all Consume() calls to finish
}

func logErrors(errChan <-chan error) {
	for err := range errChan {
		switch err := err.(type) {
		case *rmq.HeartbeatError:
			if err.Count == rmq.HeartbeatErrorLimit {
				log.Print("heartbeat error (limit): ", err)
			} else {
				log.Print("heartbeat error: ", err)
			}
		case *rmq.ConsumeError:
			log.Print("consume error: ", err)
		case *rmq.DeliveryError:
			log.Print("delivery error: ", err.Delivery, err)
		default:
			log.Print("other error: ", err)
		}
	}
}
