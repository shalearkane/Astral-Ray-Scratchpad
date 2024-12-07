import os
import uuid
from flask import Flask, request, send_file, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"  # Folder to store uploaded files
MONGO_URI = "mongodb://localhost:27017/"  # Your MongoDB connection string
DATABASE_NAME = "ISRO"
COLLECTION_NAME = "test_files_temp"

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# API for file upload
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"})

    if file:
        # Generate unique filename
        filename = str(uuid.uuid4()) + "_" + file.filename  # type: ignore

        # Save the file to the upload folder
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Store file information in MongoDB
        file_data = {"filename": filename, "filepath": filepath, "original_filename": file.filename}  # original file name
        result = collection.insert_one(file_data)

        return jsonify({"message": "File uploaded successfully", "file_id": str(result.inserted_id)})

    return {}


# API for file download
@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        file_id_obj = ObjectId(file_id)
    except Exception:
        return jsonify({"error": "Invalid file ID format"}), 400

    file_data = collection.find_one({"_id": file_id_obj})

    if file_data:
        filepath = file_data["filepath"]
        original_filename = file_data["original_filename"]
        if os.path.exists(filepath):
            response = send_file(filepath, as_attachment=True, download_name=original_filename)
            response.headers["filename"] = "yes"
            return response
        else:
            return jsonify({"error": "File not found on server"}), 404
    else:
        return jsonify({"error": "File not found in database"}), 404


@app.route("/job/<file_id>", methods=["GET"])
def job_details(file_id):
    try:
        file_id_obj = ObjectId(file_id)
    except Exception:
        return jsonify({"error": "Invalid file ID format"})

    file_data = collection.find_one({"_id": file_id_obj})
    if file_data is not None:
        resp = {"_id": str(file_data["_id"]), "wt": file_data["wt"]}
        return jsonify(resp)
    else:
        return jsonify({"error": "File not found in database"})


if __name__ == "__main__":
    app.run(debug=True)
