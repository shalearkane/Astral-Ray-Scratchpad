import pandas as pd


def preprocess_and_remove_duplicates(df: pd.DataFrame, key_column: str) -> pd.DataFrame:

    if key_column not in df.columns:
        raise ValueError(f"Column '{key_column}' not found in the dataframe.")

    # Sort the dataframe based on the key column
    df = df.sort_values(by=key_column).reset_index(drop=True)

    # Interpolate NaN values for numeric columns
    df = df.interpolate(method="linear", axis=0, limit_direction="both")

    # Group by the key column and calculate the mean for each group
    averaged_df = df.groupby(key_column, as_index=False).mean()

    return averaged_df
