import os
from ete3 import Tree
import pandas as pd

def rf_dist(t1, t2):
    rf, max_rf, common_leaves, parts_t1, parts_t2, discard_t1, discart_t2 = t1.robinson_foulds(t2, unrooted_trees=True)
    return rf / max_rf



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

assert(False)

#sim bs trees
bs_dir = "data/sim/bootstrapping"
res = []
for ds in os.listdir(bs_dir):
    bs_trees_path = os.path.join(bs_dir, ds, "bootstrap.raxml.bootstraps")
    avg_dist = average_pairwise_dist(bs_trees_path)
    print(avg_dist)
    res.append([ds, avg_dist])

df = pd.DataFrame(res, columns = ["dataset", "avg_rf_dist"])
df.to_csv("data/sim/dist_bs.csv")


#treebase ml trees
ml_dir = "data/treebase/ml_trees"
res = []
for ds in os.listdir(ml_dir):
    ml_trees_path = os.path.join(ml_dir, ds)
    avg_dist = average_pairwise_dist(ml_trees_path)
    print(avg_dist)
    res.append([ds.split(".")[0], avg_dist])

df = pd.DataFrame(res, columns = ["dataset", "avg_rf_dist"])
df.to_csv("data/treebase/dist_ml.csv")


#treebase bs trees
bs_dir = "data/treebase/bootstrapping"
res = []
for ds in os.listdir(bs_dir):
    bs_trees_path = os.path.join(bs_dir, ds, "bootstrap.raxml.bootstraps")
    avg_dist = average_pairwise_dist(bs_trees_path)
    print(avg_dist)
    res.append([ds, avg_dist])

df = pd.DataFrame(res, columns = ["dataset", "avg_rf_dist"])
df.to_csv("data/treebase/dist_bs.csv")

