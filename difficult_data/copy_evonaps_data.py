import os
import shutil

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("dna_data.tsv", sep = "\t")
df = df[df["BL_MIN"] > 0.000001]
df = df[df["PYTHIA_SCORE"] > 0.6]
print(len(df))
assert(False)
plt.hist(df["PYTHIA_SCORE"], bins = 20)
plt.savefig("PYTHIA_SCORE.png")
plt.clf()

_, bins = np.histogram(df["BL_MIN"], bins = 20)
logbins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), len(bins))
plt.hist(df["BL_MIN"], bins = logbins)
plt.xscale('log')
plt.savefig("BL_MIN.png")
plt.clf()


src_super_dir = "/hits/fast/cme/reden/evonaps/dna_alignments"

id_dict = {}
for src_name in os.listdir(src_super_dir):
    src_dir = os.path.join(src_super_dir, src_name)
    for fn in os.listdir(src_dir):
        ali_id = ".".join(fn.split(".")[:-1])
        id_dict[ali_id] = src_name


path_dict = {} 
for ali_id in df["ALI_ID"]:
    if not ali_id in id_dict:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ali_id)
        continue
    path_dict[ali_id] = os.path.join(src_super_dir, id_dict[ali_id], ali_id + ".fasta")

dest_dir = "evonaps_difficult/msa"
if not os.path.isdir(dest_dir):
    os.makedirs(dest_dir)

for ali_id in df["ALI_ID"]:
    src_path = path_dict[ali_id]
    dest_path = os.path.join(dest_dir, ali_id + ".fasta")
    shutil.copy(src_path, dest_path)
    print(ali_id)

