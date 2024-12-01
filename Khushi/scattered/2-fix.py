import pandas as pd
from pandas import DataFrame


def preprocess_and_remove_duplicates(df: DataFrame, key_column: str) -> DataFrame:
    """
    Sorts the dataframe by the key column, interpolates NaN values,
    and removes duplicates by averaging.

    Parameters:
        df (DataFrame): The input dataframe.
        key_column (str): The column used as the key to sort and identify duplicates.

    Returns:
        DataFrame: A dataframe with NaN values interpolated, duplicates removed, and values averaged.
    """
    if key_column not in df.columns:
        raise ValueError(f"Column '{key_column}' not found in the dataframe.")

    # Sort the dataframe based on the key column
    df = df.sort_values(by=key_column).reset_index(drop=True)

    # Interpolate NaN values for numeric columns
    df = df.interpolate(method="linear", axis=0, limit_direction="both")

    # Group by the key column and calculate the mean for each group
    averaged_df = df.groupby(key_column, as_index=False).mean()

    return averaged_df


if __name__ == "__main__":
    # # Sample dataframe with NaN values
    # data = {"Key": ["C", "B", "A", "A", "B"], "Value1": [10, None, 30, 50, 40], "Value2": [None, 15, 25, None, 45]}
    # df: DataFrame = pd.DataFrame(data)
    # print("Original DataFrame:")
    # print(df)

    # # Preprocess and remove duplicates
    # result: DataFrame = preprocess_and_remove_duplicates(df, key_column="Key")
    # print("\nProcessed DataFrame:")
    # print(result)

    solar_model = pd.read_csv("/Users/apple/Desktop/inter iit astro/model.2.txt", sep="\\s+", names=["energy", "error", "flux"])
    solar_model = preprocess_and_remove_duplicates(solar_model, "energy")
    solar_model.to_csv("/Users/apple/Desktop/inter iit astro/model.2.processed.txt", sep=" ", index=False, header=False)

    theoretical_spectrum_df = pd.read_csv("/Users/apple/Desktop/inter iit astro/theoretical_spectrum_interpolated.csv")
    processed_theoretical_spectrum =  preprocess_and_remove_duplicates(solar_model, "energy")
    
    output_file = "theoretical_spectrum_processed.csv"
    processed_theoretical_spectrum.to_csv(output_file, index=False)
#    print(f"Processed spectrum saved to: {output_file}")

