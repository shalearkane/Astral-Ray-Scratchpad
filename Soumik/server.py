from flask import Flask, request, jsonify
from model.model_handcrafted import process_abundance_h
from Soumik.helpers.visual_peak import generate_visible_peaks
from criterion.photon_count import photon_count_from_hdul
from helpers.utilities import to_datetime_t
from criterion.geotail import check_if_not_in_geotail
from astropy.io import fits
from io import BytesIO


app = Flask(__name__)

# Simulated data storage for testing purposes
received_results = []


@app.route("/check", methods=["POST"])
def request_fits():
    """
    Endpoint to provide a simulated FITS file.
    """
    fits_bytes = request.data

    with fits.open(BytesIO(fits_bytes)) as hdul:
        metadata = hdul[1].header  # type: ignore
        start_time = to_datetime_t(metadata["STARTIME"])
        end_time = to_datetime_t(metadata["ENDTIME"])

        not_in_geotail = check_if_not_in_geotail(start_time) and check_if_not_in_geotail(end_time)
        photon_count = photon_count_from_hdul(hdul)
        si_visible_peak = "Si" in generate_visible_peaks(hdul).keys()

        if not not_in_geotail:
            return {"accepted": False, "fail": "geotail"}

        if photon_count < 3000:
            return {"accepted": False, "fail": "photon_count"}

        if not si_visible_peak:
            return {"accepted": False, "fail": "si_peak"}

    return {"accepted": True}


@app.route("/return_results", methods=["POST"])
def return_results():
    """
    Endpoint to receive and store processing results from the workers.
    """
    fits_bytes = request.data
    filename: str = request.headers.get("filename", "")

    with fits.open(BytesIO(fits_bytes)) as hdul:
        hdul.writeto(f"/tmp/{filename}")

    abundance_json = process_abundance_h(filename)

    return abundance_json


@app.route("/results", methods=["GET"])
def get_results():
    """
    Endpoint to fetch all received results (for debugging/testing purposes).
    """
    return jsonify(received_results), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
