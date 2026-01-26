import os
import pandas as pd

label_dir = "data/sim/difficulty_labels/"
#label_dir = "data/sim_difficult/difficulty_labels/"

res = []
for ds in os.listdir(label_dir):
    res_file = os.path.join(label_dir, ds, "labelGen.csv")
    if not os.path.isfile(res_file):
        continue
    #difficult = pd.read_csv(res_file)["difficulty"].iloc[0]
    difficult = pd.read_csv(res_file)["num_patterns/num_taxa"].iloc[0]
    res.append([ds, difficult])

df = pd.DataFrame(res, columns = ["dataset", "patterns_over_taxa"])
#df = pd.DataFrame(res, columns = ["dataset", "difficulty"])
df.to_csv("data/sim/patterns_over_taxa.csv")
#df.to_csv("data/sim_difficult/difficulty_labels.csv")

