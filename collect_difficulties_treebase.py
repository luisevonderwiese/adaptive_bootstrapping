import os
import pandas as pd

path = "/hits/basement/cme/schmidja/difficulty_training_data/TreeBase_results/all_data.parquet"
df = pd.read_parquet(path)
res = []
for i, row in df.iterrows():
    ds = row["verbose_name"].split(".")[0]
    res.append([ds, row["difficult"]])

df = pd.DataFrame(res, columns = ["dataset", "difficulty"])
df.to_csv("data/treebase/difficulty_labels.csv")


