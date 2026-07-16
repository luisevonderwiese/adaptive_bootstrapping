import os
from ete3 import Tree
import pandas as pd

def rf_dist(t1, t2):
    try:
        rf, max_rf, common_leaves, parts_t1, parts_t2, discard_t1, discart_t2 = t1.robinson_foulds(t2, unrooted_trees=True)
        return rf / max_rf
    except Exception as e:
        print(e)
        return float("nan")



#base_dir = "data_new/sim"
base_dir = "data_new/treebase"
msa_dir = os.path.join(base_dir, "msa")
dists = []
for dir_name in os.listdir(msa_dir):
    name = dir_name.split(".")[0]
    best_tree_collapsed_path = os.path.join(base_dir, "raxml", name, "default_inference.raxml.bestTreeCollapsedStrict")
    consensus_tree_path = os.path.join(base_dir, "raxml", name, "plausible_consensus.raxml.consensusTreeMR")
    if not os.path.isfile(best_tree_collapsed_path) or not os.path.isfile(consensus_tree_path):
        print("skip")
        continue
    t1 = Tree(best_tree_collapsed_path)
    t2 = Tree(consensus_tree_path)
    dists.append(rf_dist(t1, t2))

print(sum(dists) / len(dists))
