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

def bipartition_in_tree(bip, tree_other, all_leaves_other):
    for node_other in tree_other.iter_descendants():
        if node_other.is_leaf():
            continue
        bip_other = get_bipartition(node_other, all_leaves_other)
        if ((bip[0] == bip_other[0]) and (bip[1] == bip_other[1])) or \
            ((bip[0] == bip_other[1]) and (bip[1] == bip_other[0])):
            return True
    return False



def evaluate(base_dir, prefix, name, factor, check_true_tree, check_resolved = False, prefix_resolved = ""):
    out_path = os.path.join(base_dir, name + ".csv")
    #if os.path.isfile(out_path):
    #    return
    
    if prefix == "ufboot":
        results_dir = os.path.join(base_dir, "ufboot")
    elif prefix.endswith("plausible"):
        results_dir = os.path.join(base_dir, "au")
    else:
        results_dir = os.path.join(base_dir, "bootstrapping")
    results_dir_resolved = os.path.join(base_dir, "bootstrapping")
    data_dir = os.path.join(base_dir, "msa")
    results = []

    for dataset in os.listdir(results_dir):
        dataset = dataset.split(".")[0]
        tree_format = 0
        if prefix == "ebg":
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".raxml.supportEBG")
        elif prefix == "shalrt":
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".raxml.supportSH")
        elif prefix == "ufboot":
            tree_format = 1
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".splits.nex.suptree")
            if not os.path.isfile(tree_inf_path):
                continue
        else:
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".booster.support")
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
        for node in tree_inf.iter_descendants():
            if node.support is not None and not node.is_leaf():
                if prefix == "ufboot" and node.name != "":
                    support = int(node.name.split("/")[0])
                    node.__setattr__("support", support)
                node.__setattr__("name", branch_id_counter)
                branch_id_counter += 1
        for node in tree_inf.iter_descendants():
            if node.is_leaf():
                continue
            if not check_true_tree:
                results.append((dataset, node.name, node.dist, round(node.support * factor), 0, 0))
                continue
            bipartition_inf = get_bipartition(node, all_leaves_inf)
            bipartition_found = bipartition_in_tree(bipartition_inf, tree_true, all_leaves_true)
            if bipartition_found:
                results.append((dataset, node.name, node.dist, round(node.support * factor), 1, 0))
            else:
                results.append((dataset, node.name, node.dist, round(node.support * factor), 0, 0))
        if check_resolved:
            tree_resolved_path = os.path.join(results_dir_resolved, dataset, prefix_resolved + ".booster.support")
            try:
                tree_resolved = ete3.Tree(tree_resolved_path, format=0)
            except:
                print("!!!!!!!!!!!!!!!!!!!! Resolved Tree broken")
                print(tree_resolved_path)
                continue

            all_leaves_resolved = set([l.name for l in tree_true.iter_leaves()])
            for node_resolved in tree_resolved.iter_descendants():
                if node_resolved.is_leaf():
                    continue
                bipartition_resolved = get_bipartition(node_resolved, all_leaves_resolved)
                collapsed = not bipartition_in_tree(bipartition_resolved, tree_inf, all_leaves_inf)
                if not collapsed:
                    continue
                if not check_true_tree:
                    results.append((dataset, node.name, 0, float("nan"), 0, 1))
                    continue
                bipartition_found = bipartition_in_tree(bipartition_resolved, tree_true, all_leaves_true)
                if bipartition_found:
                    results.append((dataset, node.name, 0, float("nan"), 1, 1))
                else:
                    results.append((dataset, node.name, 0, float("nan"), 0, 1))


    df_res = pd.DataFrame(results, columns=["dataset", "branchID", "branch_length", name, "inTrue", "collapsed"])
    df_res.to_csv(out_path)



#evaluate("data/sim", "bootstrap", "sbs_Support_booster", 100, True)
#evaluate("data/sim", "tbe", "tbe_Support", 100, True)
#evaluate("data/sim", "fbp_true", "sbs_Support_true", 1, False)
#evaluate("data/sim", "fbp_ml", "sbs_Support_ml", 1, True)
#evaluate("data/sim", "ebg", "ebg_Support", 1, True)
#evaluate("data/sim", "ufboot", "ufboot", 1, True)
#evaluate("data/sim", "shalrt", "shalrt_Support", 1, True)
evaluate("data/sim", "plausible", "sbs_Support_plausible_booster", 100, True, True, "bootstrap")
#evaluate("data/sim", "collapsed3", "sbs_Support_collapsed3_booster", 100, True, True, "bootstrap")
#evaluate("data/sim", "consense", "sbs_Support_consense_booster", 100, True, True, "bootstrap")

#evaluate("data/treebase", "fbp", "sbs_Support", 1, False)
#evaluate("data/treebase", "fbp_ml", "sbs_Support_ml", 1, False)
#evaluate("data/treebase", "tbe", "tbe_Support", 100, False)
#evaluate("data/treebase", "ebg", "ebg_Support", 1, False)
#evaluate("data/treebase", "ufboot", "ufboot", 1, False)
