import pandas as pd

df = pd.read_csv("solar_flares.csv")

df['class_alphabet'] = df['class'].str[0]
df['class_scale'] = df['class'].str[1:]

df.to_csv("solar_flares_processed.csv", index=False)
