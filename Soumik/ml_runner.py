from ML.modular_predict_abundancies_v1 import abundance_prediction_for_a_list_of_xrf_lines
import json

if __name__ == "__main__":
    with open("one.json") as f:
        xrf_lines = json.load(f)

        print(abundance_prediction_for_a_list_of_xrf_lines([xrf_lines]))