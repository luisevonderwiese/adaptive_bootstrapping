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



def average_pairwise_dist(path):
    with open(path, "r") as tree_file:
        trees = [Tree(line) for line in tree_file.readlines()]
    dists = []
    for i, t1 in enumerate(trees):
        for j, t2 in enumerate(trees):
            if i >= j:
                continue
            dists.append(rf_dist(t1, t2))
    return sum(dists) / len(dists)



#sim ml trees
label_dir = "data/sim/difficulty_labels"
outpath = "data/sim/dist_ml.csv"
if not os.path.isfile(outpath):#
    done_datasets = []
    with open(outpath, "w+") as outfile:
        outfile.write("dataset,avg_rf_dist\n")
else:
    done_datasets = list(pd.read_csv(outpath)["dataset"])
for ds in os.listdir(label_dir):
    if ds in done_datasets:
        continue
    ml_trees_path = os.path.join(label_dir, ds, "labelGen.raxml.mlTrees")
    if not os.path.isfile(ml_trees_path):
        continue
    avg_dist = average_pairwise_dist(ml_trees_path)
    print(avg_dist)
    with open(outpath, "a") as outfile:
        outfile.write(ds + "," + str(avg_dist) + "\n")

#sim bs trees
bs_dir = "data/sim/bootstrapping"
outpath = "data/sim/dist_bs.csv"
if not os.path.isfile(outpath):#
    done_datasets = []
    with open(outpath, "w+") as outfile:
        outfile.write("dataset,avg_rf_dist\n")
else:
    done_datasets = list(pd.read_csv(outpath)["dataset"])
for ds in os.listdir(bs_dir):
    if ds in done_datasets:
        continue
    bs_trees_path = os.path.join(bs_dir, ds, "bootstrap.raxml.bootstraps")
    if not os.path.isfile(bs_trees_path):
        continue
    avg_dist = average_pairwise_dist(bs_trees_path)
    print(avg_dist)
    with open(outpath, "a") as outfile:
        outfile.write(ds + "," + str(avg_dist) + "\n")

#treebase ml trees
ml_dir = "data/treebase/ml_trees"
outpath = "data/treebase/dist_ml.csv"
if not os.path.isfile(outpath):#
    done_datasets = []
    with open(outpath, "w+") as outfile:
        outfile.write("dataset,avg_rf_dist\n")
else:
    done_datasets = list(pd.read_csv(outpath)["dataset"])
for ds in os.listdir(ml_dir):
    if ds in done_datasets:
        continue
    ml_trees_path = os.path.join(ml_dir, ds)
    if not os.path.isfile(ml_trees_path):
        continue
    avg_dist = average_pairwise_dist(ml_trees_path)
    print(avg_dist)
    with open(outpath, "a") as outfile:
        outfile.write(ds + "," + str(avg_dist) + "\n")

#treebase bs trees
bs_dir = "data/treebase/bootstrapping"
outpath = "data/treebase/dist_bs.csv"
if not os.path.isfile(outpath):#
    done_datasets = []
    with open(outpath, "w+") as outfile:
        outfile.write("dataset,avg_rf_dist\n")
else:
    done_datasets = list(pd.read_csv(outpath)["dataset"])
for ds in os.listdir(bs_dir):
    if ds in done_datasets:
        continue
    bs_trees_path = os.path.join(bs_dir, ds, "bootstrap.raxml.bootstraps")
    if not os.path.isfile(bs_trees_path):
        continue
    avg_dist = average_pairwise_dist(bs_trees_path)
    print(avg_dist)
    with open(outpath, "a") as outfile:
        outfile.write(ds + "," + str(avg_dist) + "\n")

