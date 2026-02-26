import os
import pandas as pd
import subprocess

from pypythia.prediction import predict_difficulty
from pypythia.raxmlng import RAxMLNG
import pathlib

def predict(msa_path, rax):
    print(msa_path)
    msa = pathlib.Path(msa_path)
    return predict_difficulty(msa, raxmlng = rax)

rax = pathlib.Path("./snakemake/raxml-ng")
#rax = RAxMLNG(exe_path)


#data_dir = "data/treebase/msa"
#difficulties = []
#for ds in os.listdir(data_dir):
#    msa_path = os.path.join(data_dir, ds)
#    if not os.path.isfile(msa_path):
#        print("Skipping", ds)
#        continue
#    try:
#        difficulties.append([ds.split(".")[0], predict(msa_path)])
#    except Exception as e:
#        print(e)
#        continue
#df = pd.DataFrame(difficulties, columns=["dataset", "difficulty_prediction"])
#df.to_csv("data/treebase/difficulty_prediction.csv")

data_dir = "data/sim/msa"
difficulties = []
for ds in os.listdir(data_dir):
    msa_path = os.path.join(data_dir, ds, "gtr_g_sim_msa.fasta")
    if not os.path.isfile(msa_path):
        print("Skipping", ds)
        continue
    try:
        difficulties.append([ds.split(".")[0], predict(msa_path, rax)])
    except Exception as e:
        print(e)
        continue
df = pd.DataFrame(difficulties, columns=["dataset", "difficulty_prediction"])
df.to_csv("data/sim/difficulty_prediction.csv")

