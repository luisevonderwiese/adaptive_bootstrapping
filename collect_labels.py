import os
import pandas as pd


label_dir = "data/sim/difficulty_labels/"

res = []
for ds in os.listdir(label_dir):
    res_file = os.path.join(label_dir, ds, "labelGen.csv")
    if not os.path.isfile(res_file):
        continue
    difficult = pd.read_csv(res_file)["difficulty"].iloc[0]
    res.append([ds, difficult])

df = pd.DataFrame(res, columns = ["dataset", "difficulty"])
df.to_csv("data/sim/difficulty_labels.csv")


