import warnings

import ete3
from ete3 import Tree
import pandas as pd
from scipy.stats import skew
import os


def get_bipartition(node, all_leaves):
    leaves = set([leaf.name for leaf in node.iter_leaves()])
    others = all_leaves.difference(leaves)
    return (leaves, others)

def evaluate(base_dir, prefix, name, factor, check_true_tree):
    out_path = os.path.join(base_dir, name + ".csv")
    #if os.path.isfile(out_path):
    #    return
    if prefix == "ufboot":
        results_dir = os.path.join(base_dir, "ufboot")
    else:
        results_dir = os.path.join(base_dir, "bootstrapping")
    data_dir = os.path.join(base_dir, "msa")
    results = []

    for dataset in os.listdir(results_dir):
        dataset = dataset.split(".")[0]
        tree_format = 0
        if prefix == "ebg":
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".raxml.supportEBG")
        elif prefix == "ufboot":
            tree_format = 1
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".splits.nex.suptree")
            if not os.path.isfile(tree_inf_path):
                continue
        else:
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".raxml.support")
        try:
            tree_inf = ete3.Tree(tree_inf_path, format=tree_format)
        except ete3.parser.newick.NewickError as e:
            #print(e)
            print("Inferred Tree broken")
            print(tree_inf_path)
            continue
        if check_true_tree:
            tree_true_path = os.path.join(data_dir, dataset + ".phy", "gtr_g.raxml.bestTree")
            try:
                tree_true = ete3.Tree(tree_true_path, format=0)
            except ete3.parser.newick.NewickError as e:
                print("True Tree broken")
                print(tree_true_path)
                continue
            all_leaves_true = set([l.name for l in tree_true.iter_leaves()])
            all_leaves_inf = set([l.name for l in tree_inf.iter_leaves()])
        print(dataset)
        branch_id_counter = 0
        for node in tree_inf.traverse():
            if node.support is not None and not node.is_leaf():
                if prefix == "ufboot" and node.name != "":
                    support = int(node.name.split("/")[0])
                    node.__setattr__("support", support)
                node.__setattr__("name", branch_id_counter)
                branch_id_counter += 1
        for node in tree_inf.traverse():
            if node.is_leaf():
                continue

            if not check_true_tree:
                results.append((dataset, node.name, node.dist, round(node.support * factor), 0))
                continue
            bipartition_inf = get_bipartition(node, all_leaves_inf)
            bipartition_found = False
            for node_true in tree_true.traverse():
                if node_true.is_leaf():
                    continue
                bipartition_true = get_bipartition(node_true, all_leaves_true)
                if ((bipartition_inf[0] == bipartition_true[0]) and (bipartition_inf[1] == bipartition_true[1])) or \
                    ((bipartition_inf[0] == bipartition_true[1]) and (bipartition_inf[1] == bipartition_true[0])):
                    results.append((dataset, node.name, node.dist, round(node.support * factor), 1))
                    bipartition_found = True
                    break

            if not bipartition_found:
                results.append((dataset, node.name, node.dist, round(node.support * factor), 0))


    df_res = pd.DataFrame(results, columns=["dataset", "branchID", "branch_length", name, "inTrue"])
    df_res.to_csv(out_path)



#evaluate("data/sim", "bootstrap", "sbs_Support", 1, True)
evaluate("data/sim", "tbe", "tbe_Support", 100, True)
#evaluate("data/sim", "fbp_true", "sbs_Support_true", 1, False)
#evaluate("data/sim", "fbp_ml", "sbs_Support_ml", 1, True)
#evaluate("data/sim", "ebg", "ebg_Support", 1, True)
#evaluate("data/sim", "ufboot", "ufboot", 1, True)

#evaluate("data/treebase", "fbp", "sbs_Support", 1, False)
#evaluate("data/treebase", "fbp_ml", "sbs_Support_ml", 1, False)
evaluate("data/treebase", "tbe", "tbe_Support", 100, False)
#evaluate("data/treebase", "ebg", "ebg_Support", 1, False)
#evaluate("data/treebase", "ufboot", "ufboot", 1, False)
