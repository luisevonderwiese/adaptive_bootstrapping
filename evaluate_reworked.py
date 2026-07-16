import warnings

import ete3
from ete3 import Tree
import pandas as pd
from scipy.stats import skew
import os

from Bio import AlignIO

def determine_duplicate_groups(align):
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

def get_avg_seq_len(align):
    lengths = []
    for record in align:
        seq_str = str(record.seq)
        allowed_set = set(['A', 'C', 'G', 'T'])
        seq_str = ''.join([c for c in seq_str if c in allowed_set])
        lengths.append(len(seq_str))

    return sum(lengths) / len(lengths)


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



def evaluate_dataset(tree_inf_path, msa_path, out_path, support_metric, support_factor, tree_true_path):

    try:
        tree_inf = ete3.Tree(tree_inf_path, format=0)
    except:
        print("inferred tree broken")
        return
    all_leaves_inf = set([l.name for l in tree_inf.iter_leaves()])

    check_true = (tree_true_path != "")
    if check_true:
        tree_true = ete3.Tree(tree_true_path, format=0)
        all_leaves_true = set([l.name for l in tree_true.iter_leaves()])

    ending = msa_path.split(".")[-1]
    if ending == "fasta":
        f = "fasta"
    elif ending == "phy" or ending == "phylip":
        f = "phylip-relaxed"
    else:
        print(ending, "not supported")
        return None
    try:
        align = AlignIO.read(msa_path, f)
    except Exception as e:
        print(e)
        return
    duplicate_groups = determine_duplicate_groups(align)
    avg_seq_len = get_avg_seq_len(align)
    identify_exp_zero_branches(tree_inf, duplicate_groups)
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
            results.append((node.name, node.dist, round(node.support * support_factor), False, node.exp_zero, node.zero))
            continue
        bipartition_inf = get_bipartition(node, all_leaves_inf)
        bipartition_found = bipartition_in_tree(bipartition_inf, tree_true, all_leaves_true)
        results.append((node.name, node.dist, round(node.support * support_factor), bipartition_found, node.exp_zero, node.zero))

    df_res = pd.DataFrame(results, columns=["branchID", "branch_length", support_metric, "inTrue", "exp_zero", "zero"])
    df_res.to_csv(out_path)


base_dir = "data_reworked/sim"
msa_dir = os.path.join(base_dir, "msa")
out_dir = os.path.join(base_dir, "branch_stats")
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
for dir_name in os.listdir(msa_dir):
    dataset = dir_name.split(".")[0]
    out_path = os.path.join(out_dir, dataset + ".csv")
    if os.path.isfile(out_path):
        continue
    evaluate_dataset(   tree_inf_path = os.path.join(base_dir, "raxml", dataset, "bootstrap.raxml.support"), \
                        msa_path = os.path.join(msa_dir, dir_name, "gtr_g_sim_msa.fasta"), \
                        out_path = out_path, \
                        support_metric = "sbs_Support", \
                        support_factor = 1, \
                        tree_true_path = os.path.join(msa_dir, dir_name, "gtr_g.raxml.bestTree"))
    print(dataset)


base_dir = "data_reworked/treebase"
msa_dir = os.path.join(base_dir, "msa")
out_dir = os.path.join(base_dir, "branch_stats")
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
for dir_name in os.listdir(msa_dir):
    dataset = dir_name.split(".")[0]
    out_path = os.path.join(out_dir, dataset + ".csv")
    if os.path.isfile(out_path):
        continue
    evaluate_dataset(   tree_inf_path = os.path.join(base_dir, "raxml", dataset, "fbp.raxml.support"), \
                        msa_path = os.path.join(msa_dir, dir_name), \
                        out_path = out_path, \
                        support_metric = "sbs_Support", \
                        support_factor = 1, \
                        tree_true_path = "")
    print(dataset)

