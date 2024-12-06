import pandas as pd

def divide_csv(file_path, parts):
    df = pd.read_csv(file_path)
    if parts <= 0 or parts > len(df):
        return []
    chunk_size = len(df) // parts
    remainder = len(df) % parts
    start_index = 0
    divided_csvs = []

    for i in range(parts):
        rows_to_take = chunk_size + (1 if i < remainder else 0)
        end_index = start_index + rows_to_take
        chunk = df[start_index:end_index]
        chunk.to_csv(f"part_{i + 1}.csv", index=False)
        divided_csvs.append(chunk)
        start_index = end_index

    return divided_csvs

divided_csvs = divide_csv("/home/av/Downloads/data.csv", 3)
for i, part in enumerate(divided_csvs):
    print(f"Part {i + 1}:\n", part)