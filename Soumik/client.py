from os import makedirs
from typing import Optional
import requests
import multiprocessing
from os.path import isfile, join
from time import sleep
from model.model_generic import process_abundance_x2
from json import dump

# Configuration
SERVER_URL = "http://34.131.28.6:8082/new"
RETURN_URL = "http://34.131.28.6:8082/done"
NUM_PROCESSES = 8
DOWNLOAD_DIR = "/tmp"


def process_fits(class_l1: str) -> Optional[dict]:
    background = "model/data/reference/background_allevents.fits"
    solar = "data-generated/client/some.txt"
    scatter_atable = "data-generated/client/some.fits"

    if not isfile(class_l1):
        print("Class L1 not found on path")
        return None

    try:
        abundance = process_abundance_x2(class_l1, background, solar, scatter_atable)
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

            file_path = join(DOWNLOAD_DIR, f"worker_{worker_id}_{filename}.fits")
            with open(file_path, "wb") as file:
                file.write(response.content)

            abundance = process_fits(file_path)
            if abundance is not None:
                abundance["filename"] = filename

            # local persistence
            makedirs("data-generated/abundance_jsons", exist_ok=True)
            with open(f"data-generated/abundance_jsons/{filename[:-5]}.json", "w") as f:
                dump(abundance, f)

            return_response = requests.post(RETURN_URL, json=abundance, timeout=10)
            return_response.raise_for_status()

            print(f"Worker {worker_id}: Successfully processed and returned results.")

        except Exception as e:
            import traceback

            print(f"Worker {worker_id}: Encountered an error:\n{traceback.format_exc()}")
            break


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

            sleep(10)
            # Check worker statuses

    except KeyboardInterrupt:
        print("Shutting down server...")
        for proc in workers.values():
            proc.kill()
        print("All workers terminated.")


if __name__ == "__main__":
    monitor_workers()
