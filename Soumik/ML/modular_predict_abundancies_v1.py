from typing import Any, Dict, List
import pandas as pd
import pickle
import os
import json

MODEL_PATHS = {
    "model_mg": "ML/Trained_model/true_wt_mg_model_final_new.pkl",
    "model_al": "ML/Trained_model/true_wt_al_model_final_new.pkl",
    "model_si": "ML/Trained_model/true_wt_si_model_final_new.pkl",
    "model_fe": "ML/Trained_model/true_wt_fe_model_final_new.pkl",
}

# Define the feature sets for each model
FEATURES = {
    "model_al": [
        "wt_al",
        "wt_si",
        "photon_counts",
        "solar_zenith_angle",
        "emission_angle",
        "altitude",
        "exposure",
        "peak_si_c",
        "peak_mg_c",
        "peak_al_c",
        "peak_ti_c",
        "peak_fe_c",
        "peak_ca_c",
        "latitude",
        "longitude",
        "Region_Highlands - Craters",
        "Region_Highlands - Mountain Ranges",
        "Region_Maria - Basaltic Plains",
        "Region_Maria - Lunar Domes",
        "Region_Maria - Rilles",
    ],
    "model_fe": [
        "wt_mg",
        "wt_al",
        "wt_si",
        "wt_fe",
        "photon_counts",
        "solar_zenith_angle",
        "emission_angle",
        "altitude",
        "exposure",
        "peak_si_c",
        "peak_mg_c",
        "peak_al_c",
        "peak_ti_c",
        "peak_fe_c",
        "peak_ca_c",
        "latitude",
        "longitude",
        "Region_Highlands - Craters",
        "Region_Highlands - Mountain Ranges",
        "Region_Maria - Basaltic Plains",
        "Region_Maria - Lunar Domes",
        "Region_Maria - Rilles",
    ],
    "model_mg": [
        "wt_mg",
        "wt_al",
        "wt_si",
        "photon_counts",
        "solar_zenith_angle",
        "emission_angle",
        "altitude",
        "exposure",
        "peak_si_c",
        "peak_mg_c",
        "peak_al_c",
        "peak_ti_c",
        "peak_fe_c",
        "peak_ca_c",
        "latitude",
        "longitude",
        "Region_Highlands - Craters",
        "Region_Highlands - Mountain Ranges",
        "Region_Maria - Basaltic Plains",
        "Region_Maria - Lunar Domes",
        "Region_Maria - Rilles",
    ],
    "model_si": [
        "wt_si",
        "photon_counts",
        "solar_zenith_angle",
        "emission_angle",
        "altitude",
        "exposure",
        "peak_si_c",
        "peak_mg_c",
        "peak_al_c",
        "peak_ti_c",
        "peak_fe_c",
        "peak_ca_c",
        "latitude",
        "longitude",
        "Region_Highlands - Craters",
        "Region_Highlands - Mountain Ranges",
        "Region_Maria - Basaltic Plains",
        "Region_Maria - Lunar Domes",
        "Region_Maria - Rilles",
        "Region_Highlands - Valleys",
    ],
}


def classify_lunar_feature(latitude: float, longitude: float):
    # Primary classification: Highlands vs. Maria
    if (40 <= latitude <= 90 or -90 <= latitude <= -40) and -180 <= longitude <= 180:
        primary_class = "Highlands"
    elif -20 <= latitude <= 40 and -60 <= longitude <= 60:
        primary_class = "Maria"
    else:
        return "Highlands - General"

    if primary_class == "Highlands":
        if 40 <= latitude <= 60 and -40 <= longitude <= 10:
            return "Highlands - Mountain Ranges"
        elif 60 <= latitude <= 90 or -90 <= latitude <= -60:
            return "Highlands - Craters"
        elif 50 <= latitude <= 60 and -30 <= longitude <= -10:
            return "Highlands - Valleys"
        else:
            return "Highlands - General"
    elif primary_class == "Maria":
        if -10 <= latitude <= 40 and -60 <= longitude <= -20:
            return "Maria - Lunar Domes"
        elif -10 <= latitude <= 30 and -40 <= longitude <= 10:
            return "Maria - Rilles"
        else:
            return "Maria - Basaltic Plains"


def red_chi_2(element: str, df: pd.DataFrame):
    df[f"red_chi_2_{element}"] = df[f"chi_2_{element}"] / (df[f"dof_{element}"])
    return df


def expand_dict_column(df: pd.DataFrame, column_name: str, prefix: str):
    """
    Expand a dictionary column in a DataFrame into individual columns with a specified prefix.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        column_name (str): The name of the column containing dictionaries.
        prefix (str): The prefix to use for the new columns.

    Returns:
        pd.DataFrame: The DataFrame with new columns added.
    """
    # Ensure the column exists and contains dictionaries
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    # Check if the first non-null element is a dictionary
    first_non_null = df[column_name].dropna().iloc[0]
    if not isinstance(first_non_null, dict):
        raise ValueError(f"Column '{column_name}' does not contain dictionaries.")

    # Loop over the keys of the first dictionary
    for key in first_non_null.keys():
        new_column_name = f"{prefix}{key}"
        df[new_column_name] = df[column_name].apply(lambda x: x.get(key) if pd.notnull(x) else None)

    return df


def one_hot_encode_region(df: pd.DataFrame, column_name: str):
    """
    One-hot encodes the specified column in a DataFrame for the given regions.
    If the column is not present, raises an error.
    If the column contains values not in the predefined list, ignores them.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column_name (str): The column to one-hot encode.

    Returns:
        pd.DataFrame: DataFrame with one-hot encoded columns added.
    """
    # Predefined categories for one-hot encoding
    allowed_categories = [
        "Highlands - Craters",
        "Highlands - Mountain Ranges",
        "Maria - Basaltic Plains",
        "Maria - Lunar Domes",
        "Maria - Rilles",
        "Highlands - Valleys",
    ]

    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"The column '{column_name}' does not exist in the DataFrame.")

    # One-hot encoding logic
    for category in allowed_categories:
        encoded_column = f"Region_{category}"
        df[encoded_column] = (df[column_name] == category).astype(int)

    return df


def abundance_prediction_for_a_list_of_xrf_lines(xrf_lines: List[Dict[str, Any]]):
    df = pd.DataFrame(xrf_lines)

    df = expand_dict_column(df, "wt", "wt_")
    df = expand_dict_column(df, "dof", "dof_")
    df = expand_dict_column(df, "chi_2", "chi_2_")
    df = df = expand_dict_column(df, "computed_metadata", "")
    # print(df.columns)
    df["Region"] = df.apply(lambda row: classify_lunar_feature(row["latitude"], row["longitude"]), axis=1)  # type: ignore

    df = red_chi_2("mg", df)
    df = red_chi_2("al", df)
    df = red_chi_2("si", df)
    df = red_chi_2("fe", df)
    df = red_chi_2("ti", df)
    df = red_chi_2("ca", df)

    data = one_hot_encode_region(df, "Region")

    data["emission_angle"] = 90 - data["emission_angle"]
    data["solar_zenith_angle"] = 90 - data["solar_zenith_angle"]

    data["lat"] = data["latitude"]
    data["long"] = data["longitude"]
    # data=data.drop(columns=['Region','Region_Highlands - General'])
    # print(data.columns)
    # print(data.head())
    predictions = {}

    for model_name, model_path in MODEL_PATHS.items():
        # Check if the model file exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file for {model_name} not found at path: {model_path}")

        # Load the model using pickle
        with open(model_path, "rb") as file:
            model = pickle.load(file)

        # Retrieve the feature set for the current model
        feature_set = FEATURES[model_name]

        # Check if all required features are present in the data
        missing_features = [feature for feature in feature_set if feature not in data.columns]
        if missing_features:
            raise ValueError(f"Missing features for {model_name}: {missing_features}")

        # Prepare the input data for prediction
        model_input = data[feature_set]

        # Make predictions
        preds = model.predict(model_input)

        # Store the predictions with a descriptive column name
        prediction_column = f"{model_name}_prediction"
        predictions[prediction_column] = preds

    predictions_df = pd.DataFrame(predictions)
    combined_df = pd.concat([data[["latitude", "longitude", "wt_fe", "wt_al", "wt_mg", "wt_si"]], predictions_df], axis=1)
    # print(combined_df.columns)
    combined_df_json = combined_df.to_json(orient="records")
    return combined_df_json
    # combined_df.to_csv(output_path)


if __name__ == "__main__":
    with open("../one.json") as f:
        xrf_lines = json.load(f)

        print(abundance_prediction_for_a_list_of_xrf_lines([xrf_lines]))
