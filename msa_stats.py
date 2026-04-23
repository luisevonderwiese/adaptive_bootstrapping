import os
from Bio import AlignIO
import pandas as pd

def get_stats(msa_path):
    ending = msa_path.split(".")[-1]
    if ending == "fasta":
        f = "fasta"
    elif ending == "phy" or ending == "phylip":
        f = "phylip-relaxed"
    else:
        print(ending, "not supported")
        return None
    try:
        align = AlignIO.read(msa_path, f)
    except:
        return None
    
    seq_map = {}
    lengths = []
    
    for record in align:
        seq_str = str(record.seq)
        if not seq_str in seq_map:
            seq_map[seq_str] = 0
        seq_map[seq_str] += 1

        allowed_set = set(['A', 'C', 'G', 'T'])
        seq_str = ''.join([c for c in seq_str if c in allowed_set])
        lengths.append(len(seq_str))

    exp_zero_branches = sum([max(0, cnt - 2) for _, cnt in seq_map.items()])
    avg_length = sum(lengths) / len(lengths)

    return [exp_zero_branches, avg_length]



        
data_dir = "data/treebase/msa"
stats = []
for ds in os.listdir(data_dir):
    msa_path = os.path.join(data_dir, ds)
    if not os.path.isfile(msa_path):
        print("Skipping", ds)
        continue
    print(ds)
    ds_stats = get_stats(msa_path)
    if ds_stats is None:
        continue
    stats.append([ds.split(".")[0]] + ds_stats)
df = pd.DataFrame(stats, columns=["dataset", "exp_zero_branches", "avg_seq_len"])
df.to_csv("data/treebase/msa_stats.csv")

data_dir = "data/sim/msa"
stats = []
for ds in os.listdir(data_dir):
    msa_path = os.path.join(data_dir, ds, "gtr_g_sim_msa.fasta")
    if not os.path.isfile(msa_path):
        print("Skipping", ds)
        continue
    print(ds)
    ds_stats = get_stats(msa_path)
    if ds_stats is None:
        continue
    stats.append([ds.split(".")[0]] + ds_stats)
df = pd.DataFrame(stats, columns=["dataset", "exp_zero_branches", "avg_seq_len"])
df.to_csv("data/sim/msa_stats.csv")

