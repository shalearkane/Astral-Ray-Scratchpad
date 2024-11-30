import pandas as pd


def fix_spectrum_from_unsorted_or_duplicated_values(theoritical_spectrum_df: pd.DataFrame) -> pd.DataFrame:
    # Interpolate missing values in the "Total Scattered Spectrum" column
    theoretical_spectrum_df["Total Scattered Spectrum"] = theoretical_spectrum_df["Total Scattered Spectrum"].interpolate()

    duplicates = theoretical_spectrum_df[theoretical_spectrum_df.duplicated(subset=["Energy"], keep=False)]
    averaged_duplicates = duplicates.groupby("Energy", as_index=False).mean()
    unique_rows = theoretical_spectrum_df.drop_duplicates(subset=["Energy"], keep=False)
    combined_df = pd.concat([unique_rows, averaged_duplicates], ignore_index=True)
    combined_df = combined_df.sort_values(by="Energy").reset_index(drop=True)

    return combined_df


if __name__ == "__main__":
    theoretical_spectrum_df = pd.read_csv("total_scattered_spectrum.csv")
