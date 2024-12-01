from flask import Flask, request, jsonify, send_file
import io
import random
import numpy as np

app = Flask(__name__)

# Simulated data storage for testing purposes
received_results = []


@app.route("/request_fits", methods=["GET"])
def request_fits():
    """
    Endpoint to provide a simulated FITS file.
    """

    class_l1_path = (
        "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/combined-fits/30.1_80.1.fits"
    )
    try:
        return send_file(class_l1_path, download_name="dummy.fits", mimetype="application/fits", as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Failed to generate FITS file: {e}"}), 500


@app.route("/return_results", methods=["POST"])
def return_results():
    """
    Endpoint to receive and store processing results from the workers.
    """
    try:
        data = request.get_json()
        if not data or "worker_id" not in data or "result" not in data:
            return jsonify({"error": "Invalid data format"}), 400

        received_results.append(data)
        print(f"Received results from worker {data['worker_id']}: {data['result']}")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to handle results: {e}"}), 500


@app.route("/results", methods=["GET"])
def get_results():
    """
    Endpoint to fetch all received results (for debugging/testing purposes).
    """
    return jsonify(received_results), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
