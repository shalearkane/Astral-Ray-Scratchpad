import json
import pandas as pd

json_file_path = "/home/av/Downloads/ISRO.fibnacci_lat_lon.json"  # Path to the JSON file containing the list of structures

with open(json_file_path, 'r') as file:
    data_list = json.load(file)

records = []

for data in data_list:
    record = {
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "solar_zenith_angle": data["computed_metadata"]["solar_zenith_angle"],
        "emission_angle": data["computed_metadata"]["emission_angle"],
        "solar_zenith_angle_cosec": data["computed_metadata"]["solar_zenith_angle_cosec"],
        "emission_angle_cosec": data["computed_metadata"]["emission_angle_cosec"],
        "altitude": data["computed_metadata"]["altitude"],
        "exposure": data["computed_metadata"]["exposure"],
        "mid_utc": data["computed_metadata"]["mid_utc"],
        "photon_count": data["photon_count"],
    }

    # for element, wt in data["true_wt"].items():
    #     record[f"true_wt_{element}"] = wt

    for element, wt in data["wt"].items():
        record[f"wt_{element}"] = wt

    for element, chi in data["chi_2"].items():
        record[f"chi_2_{element}"] = chi

    for element, dof in data["dof"].items():
        record[f"dof_{element}"] = dof

    for element in ["na", "mg", "al", "si", "ca", "ti", "fe"]:
        record[f"peak_{element}_h"] = data["computed_metadata"].get(f"peak_{element}_h", 0)
        record[f"peak_{element}_c"] = data["computed_metadata"].get(f"peak_{element}_c", 0)
    
    records.append(record)

df = pd.DataFrame(records)
print(df.head())
output_csv = "/home/av/Documents/Visual Shit/combined_data_final.csv"
df.to_csv(output_csv, index=False)
