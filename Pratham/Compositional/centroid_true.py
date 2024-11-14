import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


atomic_weights = {
    'Si': 28.0855,
    'Fe': 55.845,
    'Mg': 24.305,
    'Al': 26.9815,
}

# Define theoretical centroids for each mineral
centroids = {
    'Plagioclase Feldspar': {'Fe_Si': 0.0, 'Mg_Si': 0.0, 'Al_Si': 0.8},
    'Pyroxene': {'Fe_Si': 1.98, 'Mg_Si': 0.86, 'Al_Si': 0},
    'Olivine': {'Fe_Si': 1.98, 'Mg_Si': 0.865, 'Al_Si': 0},
}


def calculate_element_si_ratios(df, atomic_weights):
    """
    Calculate Fe/Si, Mg/Si, and Al/Si ratios for each sample in the DataFrame.

    Parameters:
    - df (DataFrame): DataFrame containing 'al', 'fe', 'mg', 'si' columns with weight percentages.
    - atomic_weights (dict): Dictionary with atomic weights for elements.

    Returns:
    - DataFrame: Original DataFrame with additional 'Fe_Si', 'Mg_Si', 'Al_Si' columns.
    """
    # Calculate moles for each element
    df['Moles_Si'] = df['si'] 
    df['Moles_Fe'] = df['fe'] 
    df['Moles_Mg'] = df['mg'] 
    df['Moles_Al'] = df['al'] 
    
    # Avoid division by zero by replacing zero Si moles with NaN
    df['Moles_Si'].replace(0, np.nan, inplace=True)
    
    # Calculate ratios
    df['Fe_Si'] = df['Moles_Fe'] / df['Moles_Si']
    df['Mg_Si'] = df['Moles_Mg'] / df['Moles_Si']
    df['Al_Si'] = df['Moles_Al'] / df['Moles_Si']
    
    # Replace infinities and NaNs with a large number to signify unclassifiable
    df[['Fe_Si', 'Mg_Si', 'Al_Si']] = df[['Fe_Si', 'Mg_Si', 'Al_Si']].replace([np.inf, -np.inf], np.nan)
    df[['Fe_Si', 'Mg_Si', 'Al_Si']] = df[['Fe_Si', 'Mg_Si', 'Al_Si']].fillna(0)
    
    return df


def compute_distances(df, centroids):
    """
    Compute Euclidean distances from each sample to each mineral centroid.

    Parameters:
    - df (DataFrame): DataFrame with 'Fe_Si', 'Mg_Si', 'Al_Si' columns.
    - centroids (dict): Dictionary of centroids for each mineral.

    Returns:
    - DataFrame: DataFrame with additional columns for distances to each centroid.
    """
    for mineral, ratio in centroids.items():
        distance = np.sqrt(
            (df['Fe_Si'] - ratio['Fe_Si'])**2 +
            (df['Mg_Si'] - ratio['Mg_Si'])**2 +
            (df['Al_Si'] - ratio['Al_Si'])**2
        )
        df[f'Distance_{mineral}'] = distance
    return df

def classify_minerals(df, centroids, threshold=.7):
    """
    Classify each sample based on the closest mineral centroid within a threshold.

    Parameters:
    - df (DataFrame): DataFrame with distance columns.
    - centroids (dict): Dictionary of centroids for each mineral.
    - threshold (float): Maximum allowable distance for classification.

    Returns:
    - Series: Mineral classification for each sample.
    """
    # List of distance column names in the same order as centroids
    distance_columns = [f'Distance_{mineral}' for mineral in centroids.keys()]
    
    # Find the mineral with the minimum distance for each sample
    df['Min_Distance'] = df[distance_columns].min(axis=1)
    df['Closest_Mineral'] = df[distance_columns].idxmin(axis=1).replace('Distance_', '')
    
    # Assign mineral if within threshold, else 'Unclassified'
    df['Mineral'] = np.where(df['Min_Distance'] <= threshold, df['Closest_Mineral'], 'Unclassified')
    
    return df['Mineral']

def classify_lunar_samples(df, atomic_weights, centroids, threshold=.9):
    """
    Classify lunar samples into minerals based on elemental abundances.

    Parameters:
    - df (DataFrame): DataFrame with 'al', 'fe', 'mg', 'si' columns.
    - atomic_weights (dict): Atomic weights for elements.
    - centroids (dict): Theoretical centroids for minerals.
    - threshold (float): Distance threshold for classification.

    Returns:
    - DataFrame: Original DataFrame with additional classification columns.
    """
    # Step 1: Calculate element/Si ratios
    df = calculate_element_si_ratios(df, atomic_weights)
    
    # Step 2: Compute distances to centroids
    df = compute_distances(df, centroids)
    
    # Step 3: Classify minerals based on distances and threshold
    df['Mineral'] = classify_minerals(df, centroids, threshold)
    
    # Optional: Drop intermediate columns if desired
    # df.drop(['Moles_Si', 'Moles_Fe', 'Moles_Mg', 'Moles_Al', 'Min_Distance', 'Closest_Mineral'], axis=1, inplace=True)
    
    return df



# Classify samples
df_classified = classify_lunar_samples(df_samples.copy(), atomic_weights, centroids, threshold=0.9)

# Display classified samples
print("\nClassified Samples:")
print(df_classified[['al', 'fe', 'mg', 'si', 'Fe_Si', 'Mg_Si', 'Al_Si', 'Mineral']])



def plot_classification(df):
    """
    Plot the classified samples in a 3D scatter plot.

    Parameters:
    - df (DataFrame): DataFrame with 'Fe_Si', 'Mg_Si', 'Al_Si', 'Mineral' columns.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Define colors for each mineral
    color_map = {
        'Distance_Plagioclase Feldspar': 'blue',
        'Distance_Pyroxene': 'red',
        'Distance_Olivine': 'green',
        'Unclassified': 'gray'
    }

    # Plot each mineral group
    for mineral, color in color_map.items():
        subset = df[df['Closest_Mineral'] == mineral]
        ax.scatter(subset['Fe_Si'], subset['Mg_Si'], subset['Al_Si'],
                   c=color, label=mineral, s=50, alpha=0.6, edgecolors='w')

    ax.set_xlabel('Fe/Si')
    ax.set_ylabel('Mg/Si')
    ax.set_zlabel('Al/Si')
    ax.set_title('Lunar Sample Classification')
    ax.legend()
    plt.show()

# Plot the classified samples
plot_classification(df_classified)
