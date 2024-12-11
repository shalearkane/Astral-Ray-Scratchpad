import pandas as pd
from typing import List, Dict, Any
from json import dump

df = pd.read_csv("predictions.csv")
df = df[["latitude", "longitude", "model_al_prediction", "model_fe_prediction", "model_mg_prediction", "model_si_prediction"]]
print(df.head())

listicle: List[Dict[str, Any]] = list()

for idx, row in df.iterrows():
    rowj = {
        "lat": row["latitude"],
        "lon": row["longitude"],
        "wt": {
            "mg": row["model_mg_prediction"],
            "al": row["model_al_prediction"],
            "si": row["model_si_prediction"],
            "fe": row["model_fe_prediction"],
        },
    }

    listicle.append(rowj)

with open("toplot.json", "w") as f:
    dump(listicle, f)
