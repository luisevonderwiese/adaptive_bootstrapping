import os
from ete3 import Tree
import pandas as pd 
def collapse_branches(t, threshold):
    for node in t.iter_descendants():
        if node.is_leaf():
            continue
        if node.dist <= threshold:
            node.delete()

def check_branches(t, threshold):
    for node in t.iter_descendants():
        if node.is_leaf():
            continue
        if node.dist <= threshold:
            print(node.dist)

def seq_len_fasta(path):
    with open(path, "r") as infile:
        lines = infile.readlines()
    return len(lines[1]) - 1

msa_dir = "data/treebase/msa"
superoutdir = "data/treebase/bootstrapping"

df = pd.read_csv("data/treebase/msa_stats.csv")
for i, row in df.iterrows():
    name = row["dataset"] + ".phy"
    #msa_path = os.path.join(msa_dir, name, "gtr_g_sim_msa.fasta")
    msa_path = os.path.join(msa_dir, name)
    seq_len = seq_len_fasta(msa_path)
    threshold = max(0.5 / row["avg_seq_len"], 0.000001)
    msa_name = name.split(".")[0]
    outdir = os.path.join(superoutdir, msa_name)
    #best_tree_path = os.path.join(outdir, "bootstrap.raxml.bestTree")
    best_tree_path = os.path.join(outdir, "inference.raxml.bestTree")
    if not os.path.isfile(best_tree_path):
        print(best_tree_path)
        continue
    t = Tree(best_tree_path)
    collapse_branches(t, threshold)
    collapsed_tree_path = best_tree_path + "Collapsed3"
    print(collapsed_tree_path)
    t.write(outfile = collapsed_tree_path)

