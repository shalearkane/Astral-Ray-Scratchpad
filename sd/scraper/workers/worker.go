package workers

import (
	"log/slog"
	"sync"
)

func (worker *Worker) CheckForNewData() {
	worker.PradanClient.ClassTimeStart = "2021-11-11 00:00:00"
	worker.PradanClient.ClassTimeEnd = "2022-11-11 00:00:00"
	worker.PradanClient.XSMTimeStart = "2021-11-11 00:00:00"
	worker.PradanClient.XSMTimeEnd = "2022-11-11 00:00:00"
	worker.PradanClient.AutoUpdate() // IMP - It updates all its internal states

	var wg sync.WaitGroup
	classChannel := make(chan []string)
	// xsmChannel := make(chan []string)

	go worker.PradanClient.GetCLASSDataList(classChannel)
	// go worker.PradanClient.GetXSMDataList(xsmChannel)

	wg.Add(1)
	go worker.WriteStreamToQueue(classChannel, &wg)
	// go worker.WriteStreamToQueue(xsmChannel, &wg)
	wg.Wait()
}

func (worker *Worker) WriteStreamToQueue(channel chan []string, wg *sync.WaitGroup) {
	defer wg.Done()
	// As soon we get any IDs trigger the download workflow
	for ids := range channel {
		for _, id := range ids {
			if err := (*worker.DownloadIdsQueue).Publish(id); err != nil {
				slog.Error("failed to publish: %s", err)
			}
		}
	}
}
