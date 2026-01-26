import os
import pandas as pd

path = "/hits/basement/cme/schmidja/difficulty_training_data/TreeBase_results/all_data.parquet"
df = pd.read_parquet(path)
print(df)
res = []
for i, row in df.iterrows():
    ds = row["verbose_name"].split(".")[0]
    #res.append([ds, row["difficult"]])
    res.append([ds, row["num_patterns/num_taxa"]])

#df = pd.DataFrame(res, columns = ["dataset", "difficulty"])
#df.to_csv("data/treebase/difficulty_labels.csv")

df = pd.DataFrame(res, columns = ["dataset", "patterns_over_taxa"])
df.to_csv("data/treebase/patterns_over_taxa.csv")

