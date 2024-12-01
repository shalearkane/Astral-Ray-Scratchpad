import requests
from os.path import isfile
from constants.misc import FILE_SERVER


def download_file_from_file_server(doc: dict, collection: str, download_location_prefix: str) -> bool:
    if "_id" not in doc.keys() or "path" not in doc.keys():
        raise Exception("pass doc with _id and path. project if necessary")

    try:
        on_disk_path = f"{download_location_prefix}/{doc["path"].split("/")[-1]}"
        if isfile(on_disk_path):
            return True

        response = requests.get(f"{FILE_SERVER}/{collection}/{doc["_id"]}")
        response.raise_for_status()

        with open(on_disk_path, "wb") as f:
            f.write(response.content)

    except Exception:
        import traceback

        print(traceback.format_exc())
        print(f"could not download file: {doc["_id"]}")
        return False
    else:
        return True
