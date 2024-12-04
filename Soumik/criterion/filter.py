import pandas as pd

df = pd.read_csv("photon_count-1-31.csv")

df = df[df["flare_class"] == "M"]

df.to_csv("photon_count-1-31-filtered.csv", index=False)