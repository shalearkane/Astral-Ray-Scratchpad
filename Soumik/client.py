import requests
import multiprocessing
import os
import time

from model.model_generic import process_abundance

# Configuration
SERVER_URL = "http://localhost:5000/request_fits"
RETURN_URL = "http://localhost:5000/return_results"
NUM_PROCESSES = 16
DOWNLOAD_DIR = "/tmp"


def process_fits(class_l1: str):
    background = "data/reference/background_allevents.fits"
    solar = "data/reference/modelop_20210827T210316000_20210827T210332000.txt"
    scatter_atable = "data/reference/tbmodel_20210827T210316000_20210827T210332000.fits"

    if not os.path.isfile(class_l1):
        print("Error error")
        return

    try:
        process_abundance(class_l1, background, solar, scatter_atable, 2048)
    except Exception as e:
        raise RuntimeError(f"Error processing FITS file {class_l1}: {e}")


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

            file_path = os.path.join(DOWNLOAD_DIR, f"worker_{worker_id}.fits")
            with open(file_path, "wb") as file:
                file.write(response.content)

            result = process_fits(file_path)

            return_response = requests.post(RETURN_URL, json={"worker_id": worker_id, "result": result}, timeout=10)
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
            proc.terminate()
        print("All workers terminated.")


if __name__ == "__main__":
    monitor_workers()
