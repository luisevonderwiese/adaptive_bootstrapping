import warnings

import ete3
from ete3 import Tree
import pandas as pd
from scipy.stats import skew
import os


def get_bipartition(node):
    if not node.is_leaf():
        left_children = sorted([leaf.name for leaf in node.children[0].iter_leaves()])
        right_children = sorted([leaf.name for leaf in node.children[1].iter_leaves()])
        bipartition = (left_children, right_children)
        return bipartition
    return None



#results_dir = "TBE"
#name = "tbe_Support"
#factor = 100

base_dir =  "data/sim"
prefix = "bootstrap"
name = "sbs_Support"
factor = 1

results_dir = os.path.join(base_dir, "bootstrapping")
data_dir = os.path.join(base_dir, "msa")
results = []

for dataset in os.listdir(results_dir):
    dataset = dataset.split(".")[0]
    tree_inf_path = os.path.join(results_dir, dataset, prefix + ".raxml.support")
    tree_true_path = os.path.join(data_dir, dataset + ".phy", "gtr_g.raxml.bestTree")
 

    try:
        tree_inf = ete3.Tree(tree_inf_path, format=0)
    except ete3.parser.newick.NewickError as e:
        print("Inferred Tree broken")
        print(tree_inf_path)
        continue

    try:
        tree_true = ete3.Tree(tree_true_path, format=0)
    except ete3.parser.newick.NewickError as e:
        print("True Tree broken")
        print(tree_true_path)
        continue

    branch_id_counter = 0
    for node in tree_inf.traverse():
        branch_id_counter += 1
        if node.support is not None and not node.is_leaf():
            length = node.dist
            node.__setattr__("name", branch_id_counter)

    branch_id_counter = 0
    for node in tree_true.traverse():
        branch_id_counter += 1
        if node.support is not None and not node.is_leaf():
            length = node.dist
            node.__setattr__("name", branch_id_counter)

    for node in tree_inf.traverse():
        if not node.is_leaf():
            bipartition_inf = get_bipartition(node)

            if bipartition_inf is not None:
                bipartition_found = False
                for node_true in tree_true.traverse():
                    if node_true.is_leaf():
                        continue
                    bipartition_true = get_bipartition(node_true)
                    if bipartition_true is not None:
                        first_match = False
                        second_match = False
                        if (bipartition_inf[0] == bipartition_true[0]) or (bipartition_inf[0] == bipartition_true[1]):
                            first_match = True
                        if (bipartition_inf[1] == bipartition_true[0]) or (bipartition_inf[1] == bipartition_true[1]):
                            second_match = True
                        if second_match and first_match:  # bipartition is in true tree
                            bipartition_found = True
                            results.append((dataset, node_true.name, node.support * factor, 1))
                if not bipartition_found:
                    results.append((dataset, node_true.name, node.support * factor, 0))


df_res = pd.DataFrame(results, columns=["dataset", "branchID_True", name, "inTrue"])
df_res.to_csv(os.path.join(base_dir, name + ".csv"))
