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

rax = pathlib.Path("./snakemake_new/bin/raxml-ng")
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

#data_dir = "data_new/treebase"
#data_dir = "difficult_data/evonaps_difficult"
#msa_dir = os.path.join(data_dir, "msa_nodup")
#difficulties = []
#for ds in os.listdir(msa_dir):
#    msa_path = os.path.join(msa_dir, ds)#, "msa.fasta")
#    if not os.path.isfile(msa_path):
#        print("Skipping", ds)
#        continue
#    try:
#        difficulties.append([ds.split(".")[0], predict(msa_path, rax)])
#    except Exception as e:
#        print(e)
#        continue
#df = pd.DataFrame(difficulties, columns=["dataset", "difficulty_prediction"])
#df.to_csv(os.path.join(data_dir, "difficulty_prediction_nodup.csv"))


#data_dir = "difficult_data/evonaps_difficult"
data_dir = "difficult_data/alisim2"
msa_dir = os.path.join(data_dir, "msa")
difficulties = []
for ds in os.listdir(msa_dir):
    msa_path = os.path.join(msa_dir, ds)
    if not os.path.isfile(msa_path):
        print("Skipping", ds)
        continue
    try:
        difficulties.append([ds.split(".")[0], predict(msa_path, rax)])
    except Exception as e:
        print(e)
        continue
df = pd.DataFrame(difficulties, columns=["dataset", "difficulty_prediction"])
df.to_csv(os.path.join(data_dir, "difficulty_prediction.csv"))

