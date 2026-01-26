import os
import pandas as pd
import matplotlib.pyplot as plt


data_dir = "data/treebase/msa"
lengths = []
for ds in os.listdir(data_dir):
    msa_path = os.path.join(data_dir, ds)
    if not os.path.isfile(msa_path):
        print("Skipping", ds)
        continue
    with open(msa_path, "r") as msa_file:
        line = msa_file.readlines()[0]
        length = int(line.split(" ")[2])
        lengths.append([ds.split(".")[0], length])
df = pd.DataFrame(lengths, columns=["dataset", "size"])
df.to_csv("data/treebase/sizes.csv")

#data_dir = "data/sim/msa"
data_dir = "data/sim_difficult/msa"
lengths = []
for ds in os.listdir(data_dir):
    msa_path = os.path.join(data_dir, ds, "gtr_g_sim_msa.fasta")
    if not os.path.isfile(msa_path):
        print("Skipping", ds)
        continue
    with open(msa_path, "r") as msa_file:
        content = msa_file.read()
        length = content.count(">")
        lengths.append([ds.split(".")[0], length])
df = pd.DataFrame(lengths, columns=["dataset", "size"])
#df.to_csv("data/sim/sizes.csv")
df.to_csv("data/sim_difficult/sizes.csv")
