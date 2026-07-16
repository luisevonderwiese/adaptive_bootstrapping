import os
import pandas as pd
import ete3
from ete3 import Tree



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



def evaluate(base_dir, prefix, name):
    out_path = os.path.join(name + ".csv")
    
    results_dir = os.path.join(base_dir, "bootstrapping")
    data_dir = os.path.join(base_dir, "msa")
    results = []
    msa_stats_df = pd.read_csv(os.path.join(base_dir, "msa_stats.csv"))

    for dataset in os.listdir(results_dir):
        dataset = dataset.split(".")[0]
        if name == "ebg_Support":
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".raxml.supportEBG")
        else:
            tree_inf_path = os.path.join(results_dir, dataset, prefix + ".raxml.support")
        try:
            tree_inf = ete3.Tree(tree_inf_path, format=0)
        except ete3.parser.newick.NewickError as e:
            #print(e)
            print("Inferred Tree broken")
            print(tree_inf_path)
            continue
        tree_true_path = os.path.join(data_dir, dataset + ".phy", "gtr_g.raxml.bestTree")
        msa_path = os.path.join(data_dir, dataset + ".phy", "gtr_g_sim_msa.fasta")
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
            if not node.is_leaf():
                node.__setattr__("name", branch_id_counter)
                branch_id_counter += 1
        for node in tree_inf.iter_descendants():
            if node.is_leaf():
                continue
            bipartition_inf = get_bipartition(node, all_leaves_inf)
            bipartition_found = bipartition_in_tree(bipartition_inf, tree_true, all_leaves_true)
            if bipartition_found:
                results.append((dataset, node.name, node.support, 1))
            else:
                results.append((dataset, node.name, node.support, 0))

    df_res = pd.DataFrame(results, columns=["dataset", "branchID", name, "inTrue"])
    df_res.to_csv(out_path)


evaluate("/hits/fast/cme/haeusele/adaptive_bootstrapping/data/sim", "bootstrap", "sbs_Support")
evaluate("/hits/fast/cme/haeusele/adaptive_bootstrapping/data/sim", "ebg", "ebg_Support")
