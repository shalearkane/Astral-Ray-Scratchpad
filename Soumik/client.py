from typing import Optional
import requests
import multiprocessing
import os
import time

from model.model_generic import process_abundance

# Configuration
SERVER_URL = "http://172.20.59.218:8082/new"
RETURN_URL = "http://172.20.59.218:8082/done"
NUM_PROCESSES = 1
DOWNLOAD_DIR = "/tmp"


def process_fits(class_l1: str) -> Optional[dict]:
    background = "model/data/reference/background_allevents.fits"
    solar = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/flux/some.txt"
    scatter_atable = "model/data/reference/tbmodel_20210827T210316000_20210827T210332000.fits"

    if not os.path.isfile(class_l1):
        print("Error error")
        return None

    try:
        abundance = process_abundance(class_l1, background, solar, scatter_atable, 2048)
    except Exception as e:
        raise RuntimeError(f"Error processing FITS file {class_l1}: {e}")
    else:
        return abundance


def worker(worker_id: int):
    """
    Worker process that continuously requests and processes FITS files.
    Replaces itself if it encounters an exception.
    """
    print(f"Worker {worker_id} started.")
    while True:
        try:
            # Request a FITS file from the server
            response = requests.get(SERVER_URL, timeout=10)
            response.raise_for_status()

            if not response.content:
                raise ValueError("Received an empty response from the server.")

            filename = response.headers["filename"]

            file_path = os.path.join(DOWNLOAD_DIR, f"worker_{worker_id}_{filename}.fits")
            with open(file_path, "wb") as file:
                file.write(response.content)

            result = process_fits(file_path)
            if result is not None:
                result["filename"] = filename

            print(result)

            return_response = requests.post(RETURN_URL, json=result, timeout=10)
            return_response.raise_for_status()

            print(f"Worker {worker_id}: Successfully processed and returned results.")

        except Exception as e:
            import traceback

            print(f"Worker {worker_id}: Encountered an error:\n{traceback.format_exc()}")
            break  # Exit the worker on exception


def monitor_workers():
    """
    Monitor and maintain the pool of workers.
    Restarts a worker if it dies.
    """
    workers = {}
    try:
        while True:
            # Spin up workers until NUM_PROCESSES are running
            for i in range(NUM_PROCESSES):
                if i not in workers or not workers[i].is_alive():
                    # Start a new worker
                    print(f"Starting/restarting worker {i}.")
                    worker_process = multiprocessing.Process(target=worker, args=(i,))
                    worker_process.start()
                    workers[i] = worker_process

            time.sleep(10)
            # Check worker statuses

    except KeyboardInterrupt:
        print("Shutting down server...")
        for proc in workers.values():
            proc.kill()
        print("All workers terminated.")


if __name__ == "__main__":
    monitor_workers()
