package consumer

import (
	"context"
	"log/slog"
	"sync"
	"time"
)

func (consumer *Consumer) ListenForMessages() {
	var wg sync.WaitGroup

	wg.Add(1)
	go consumer.ListenForStep1ChecksJobMessages(&wg)
	go consumer.ListenForStep2XRFIntensityJobMessages(&wg)
	go consumer.ListenForStep3PredictionJobMessages(&wg)
	go consumer.ListenForStep4X2AbundJobMessages(&wg)
	go consumer.ListenForStep5SRJobMessages(&wg)
	wg.Wait()
}

func (consumer *Consumer) ListenForStep1ChecksJobMessages(wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		job, err := consumer.Step1CheckJobQueue.Lease(context.Background(), consumer.Redis, true, 0, 20*time.Second)
		if err != nil {
			slog.Error(err.Error())
		}
		go consumer.ProcessStep1Checks(job)
	}
}

func (consumer *Consumer) ListenForStep2XRFIntensityJobMessages(wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		job, err := consumer.Step2XRFIntensityJobQueue.Lease(context.Background(), consumer.Redis, true, 0, 20*time.Second)
		if err != nil {
			slog.Error(err.Error())
		}
		go consumer.ProcessStep2XRFIntensity(job)
	}
}

func (consumer *Consumer) ListenForStep3PredictionJobMessages(wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		job, err := consumer.Step3PredictionJobQueue.Lease(context.Background(), consumer.Redis, true, 0, 20*time.Second)
		if err != nil {
			slog.Error(err.Error())
		}
		go consumer.ProcessStep3Prediction(job)
	}
}

func (consumer *Consumer) ListenForStep4X2AbundJobMessages(wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		job, err := consumer.Step4X2AbundJobQueue.Lease(context.Background(), consumer.Redis, true, 0, 20*time.Second)
		if err != nil {
			slog.Error(err.Error())
		}
		go consumer.ProcessStep4X2Abund(job)
	}
}

func (consumer *Consumer) ListenForStep5SRJobMessages(wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		job, err := consumer.Step5SRJobQueue.Lease(context.Background(), consumer.Redis, true, 0, 20*time.Second)
		if err != nil {
			slog.Error(err.Error())
		}
		go consumer.ProcessStep5SR(job)
	}
}
