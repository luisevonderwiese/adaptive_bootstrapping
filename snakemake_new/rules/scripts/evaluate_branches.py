import warnings

import ete3
from ete3 import Tree
import pandas as pd
from scipy.stats import skew
import os

from Bio import AlignIO

def determine_duplicate_groups(msa_path):
    ending = msa_path.split(".")[-1]
    if ending == "fasta":
        f = "fasta"
    elif ending == "phy" or ending == "phylip":
        f = "phylip-relaxed"
    else:
        print(ending, "not supported")
        return None
    align = AlignIO.read(msa_path, f)
    seq_map = {}
    for rec in align:
        s = rec.seq
        if not s in seq_map:
            seq_map[s] = []
        seq_map[s].append(rec.id)
    final_map = {}
    for i, (_, taxa) in enumerate(seq_map.items()):
        for taxon in taxa:
            final_map[taxon] = i
    return final_map

def identify_exp_zero_branches(tree, duplicate_groups):
    for node in tree.traverse("postorder"):
        if node.is_leaf():
            node.add_feature("duplicate_group", duplicate_groups[node.name])
            continue
        c = node.children
        duplicate_group = c[0].duplicate_group
        if duplicate_group != -1:
            for child in c:
                if child.duplicate_group != duplicate_group:
                    duplicate_group = -1
                    break
        node.add_feature("duplicate_group", duplicate_group)
        exp_zero = (duplicate_group != -1)
        for child in c:
            child.add_feature("exp_zero", exp_zero)

def identify_zero_branches(tree, avg_seq_len):
    t = max(0.000001, 0.5 / avg_seq_len)
    for node in tree.iter_descendants():
        if node.dist <= t:
            zero = True
        else:
            zero = False
        node.add_feature("zero", zero)



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



def evaluate_dataset(tree_inf_path, msa_stats_path, out_path, support_metric, support_factor, tree_true_path, tree_resolved_path):
    
    tree_inf = ete3.Tree(tree_inf_path, format=0)
    all_leaves_inf = set([l.name for l in tree_inf.iter_leaves()])

    check_true = (tree_true_path != "")
    if check_true:
        tree_true = ete3.Tree(tree_true_path, format=0)
        all_leaves_true = set([l.name for l in tree_true.iter_leaves()])

    msa_stats_df = pd.read_csv(msa_stats_path)
    #duplicate_groups = determine_duplicate_groups(msa_path)
    avg_seq_len = msa_stats_df.iloc[0]["avg_seq_len"]
    #identify_exp_zero_branches(tree_inf, duplicate_groups)
    identify_zero_branches(tree_inf, avg_seq_len)

    branch_id_counter = 0
    for node in tree_inf.iter_descendants():
        if node.support is not None and not node.is_leaf():
            node.__setattr__("name", branch_id_counter)
            branch_id_counter += 1
    
    results = []
    for node in tree_inf.iter_descendants():
        if node.is_leaf():
            continue
        if not check_true:
            results.append((node.name, node.dist, round(node.support * support_factor), False, False, node.zero))
            continue
        bipartition_inf = get_bipartition(node, all_leaves_inf)
        bipartition_found = bipartition_in_tree(bipartition_inf, tree_true, all_leaves_true)
        results.append((node.name, node.dist, round(node.support * support_factor), bipartition_found, False, node.zero))
    
    check_resolved = (tree_resolved_path != "")
    if check_resolved:
        tree_resolved = ete3.Tree(tree_resolved_path, format=0)
        #identify_exp_zero_branches(tree_resolved, duplicate_groups)
        identify_zero_branches(tree_resolved, avg_seq_len)
        all_leaves_resolved = set([l.name for l in tree_resolved.iter_leaves()])
       
        for node in tree_resolved.iter_descendants():
            if node.support is not None and not node.is_leaf():
                node.__setattr__("name", branch_id_counter)
                branch_id_counter += 1


        for node_resolved in tree_resolved.iter_descendants():
            if node_resolved.is_leaf():
                continue
            bipartition_resolved = get_bipartition(node_resolved, all_leaves_resolved)
            collapsed = not bipartition_in_tree(bipartition_resolved, tree_inf, all_leaves_inf)
            if not collapsed:
                continue #branch evaluated above
            if not check_true:
                results.append((node_resolved.name, float("nan"), float("nan"), False, True, node_resolved.zero))
                continue
            bipartition_found = bipartition_in_tree(bipartition_resolved, tree_true, all_leaves_true)
            results.append((node_resolved.name, float("nan"), float("nan"), bipartition_found, True, node_resolved.zero))


    df_res = pd.DataFrame(results, columns=["branchID", "branch_length", support_metric, "inTrue", "collapsed", "zero"])
    df_res.to_csv(out_path)


evaluate_dataset(
        snakemake.input.support_tree, 
        snakemake.input.selection_stats, 
        snakemake.output.branch_stats, 
        snakemake.params.support_metric, 
        int(snakemake.params.support_factor), 
        snakemake.params.true_tree,
        snakemake.params.best_tree)
