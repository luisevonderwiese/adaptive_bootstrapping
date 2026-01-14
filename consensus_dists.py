import os
from ete3 import Tree
import pandas as pd


def rf_dist(t1, t2):
    rf, max_rf, common_leaves, parts_t1, parts_t2, discard_t1, discart_t2 = t1.robinson_foulds(t2, unrooted_trees=True)
    return rf / max_rf


ml_ctree_name = "consense_ml_mre.raxml.consensusTreeMRE"
bs_ctree_name = "consense_bs_mre.raxml.consensusTreeMRE"

for data_type in ["sim", "treebase"]:
    res = []
    outdir = os.path.join("data", data_type, "bootstrapping") 
    for ds in os.listdir(outdir):
        ml_ctree_path = os.path.join(outdir, ds, ml_ctree_name)
        bs_ctree_path = os.path.join(outdir, ds, bs_ctree_name)
        if not os.path.isfile(ml_ctree_path) or not os.path.isfile(bs_ctree_path):
            continue
        dist = rf_dist(Tree(ml_ctree_path), Tree(bs_ctree_path))
        print(dist)
        res.append([ds, dist])
    df = pd.DataFrame(res, columns = ["dataset", "rf_dist_consensus_trees"])
    df.to_csv(os.path.join("data", data_type, "consensus_dists.csv"))
