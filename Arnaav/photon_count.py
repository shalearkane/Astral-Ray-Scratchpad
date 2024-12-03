import os
import pandas as pd
from astropy.io import fits

def sum_counts_in_range(fits_file, start_channel=15, end_channel=800):
    """
    Sums the counts in the specified channel range for a given FITS file.
    """
    try:
        with fits.open(fits_file) as hdul:
           
            data = hdul[1].data
            channels = data['CHANNEL']
            counts = data['COUNTS']

            mask = (channels >= start_channel) & (channels <= end_channel)
            counts_in_range = counts[mask]

            return float(counts_in_range.sum())

    except Exception as e:
        print(f"An error occurred while processing {fits_file}: {e}")
        return None

def process_folder(folder_path, start_channel=15, end_channel=800, save_csv=False, output_csv="counts_summary.csv"):
    
    results = []
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".fits"):
            fits_file = os.path.join(folder_path, file_name)
            
            sum_counts = sum_counts_in_range(fits_file, start_channel, end_channel)
            
            if sum_counts is not None:
                results.append({"Class Name": file_name, "Sum of Counts in Range": sum_counts})

  
    df = pd.DataFrame(results)
    
    
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

    return df

# Example usage
folder_path = "/home/av/Documents/Code/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class"
output_csv = "counts_summary.csv"


df_results = process_folder(folder_path, output_csv=output_csv)
print(df_results)
