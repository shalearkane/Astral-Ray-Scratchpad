from flask import Flask, request
from pymongo import MongoClient
from ML.modular_predict_abundancies_v1 import abundance_prediction
from constants.mongo import COLLECTION_FIBONACCI_LAT_LON_V2, DATABASE_ISRO, MONGO_URI
from typing import Dict, Any
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)


collection = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_FIBONACCI_LAT_LON_V2]


@cross_origin()
@app.route("/", methods=["GET"])
def request_fits():
    """
    Endpoint to provide a simulated FITS file.
    """
    lat = float(request.headers.get("lat", 0))
    lon = float(request.headers.get("lon", 0))

    nearest_res: Dict[str, Any] = collection.find_one({"location": {"$near": {"type": "Point", "coordinates": [lon, lat]}}})  # type: ignore

    if nearest_res.get("photon_count", -1) == -1:
        return {"not_mapped": True}

    nearest_res["latitude"] = nearest_res["lat"]
    nearest_res["longitude"] = nearest_res["lon"]

    prediction_output = abundance_prediction(nearest_res)
    print(f"prediction output: {prediction_output}")

    return prediction_output


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
