import os
import random
import copy
import numpy as np
import pandas as pd

from ete3 import Tree
from Bio import AlignIO

def discordant_tree(tree):
    labels = [l.name for l in tree.iter_leaves()]
    random.shuffle(labels)
    d_tree = copy.deepcopy(tree)
    i = 0
    for l in d_tree.iter_leaves():
        l.name = labels[i]
        i += 1
    return d_tree

def get_small_m(n):
    return int(n * (np.random.normal(loc = 1, scale = 0.5, size = (1, 1))[0][0]))

def select(prob = 0.1):
    return random.randrange(100) < (prob * 100)


def create_rogues(tree):
    r_tree = copy.deepcopy(tree)
    for node in r_tree.iter_descendants():
        if select():
            node.dist = 1.0
    return r_tree


def run_alisim(treepath, length, outpath):
    command = "./iqtree3 --alisim "
    command += outpath
    command += " -t " + treepath
    command += " --length " + str(length)
    command += " -af fasta"
    command += " -m GTR+G"
    command += " --seed 1"
    os.system(command)

def concat_aligns(alignpath_1, alignpath_2, c_alignpath):
    try:
        align1 = AlignIO.read(alignpath_1, "fasta")
        align2 = AlignIO.read(alignpath_2, "fasta")
    except:
        return
    dict2 = {rec.id : rec.seq for rec in align2}
    for rec in align1:
        rec.seq += dict2[rec.id]
    AlignIO.write(align1, c_alignpath, "fasta")
    os.remove(alignpath_1)
    os.remove(alignpath_2)



def simulate(treepath, alignpath, treeprefix, simprefix):
    try:
        t = Tree(treepath)
    except Exception as e:
        print(treepath)
        print(e)
        return
    n = len([l for l in t.iter_leaves()])
    align = AlignIO.read(alignpath, "phylip")
    m = align.get_alignment_length()

    d_tree = discordant_tree(t)
    d_treepath = treeprefix + "d.tree"
    d_tree.write(outfile = d_treepath)
    outpath = simprefix + "d_a"
    run_alisim(treepath, m // 2, outpath)
    d_outpath = simprefix + "d_b"
    run_alisim(d_treepath, m // 2, d_outpath)
    alignpath_1 = outpath + ".fa"
    alignpath_2 = d_outpath + ".fa"
    c_alignpath = simprefix + "d.fa"
    concat_aligns(alignpath_1, alignpath_2, c_alignpath)

    s_outpath = simprefix + "s"
    run_alisim(treepath, get_small_m(n), s_outpath)

    r_tree = create_rogues(t)
    r_treepath = treeprefix + "r.tree"
    r_tree.write(outfile = r_treepath)
    r_outpath = simprefix + "r"
    run_alisim(r_treepath, m, r_outpath)



difficulty_df = pd.read_csv("../data_new/treebase/difficulty_labels.csv")
difficulty_df = difficulty_df[difficulty_df["difficulty"] > 0.6]
difficulty_df = difficulty_df[difficulty_df["difficulty"] <= 0.7]
print(len(difficulty_df))
datasets = list(difficulty_df["dataset"])

treedir = "alisim2/simtrees"
if not os.path.isdir(treedir):
    os.makedirs(treedir)
simdir = "alisim2/msa"
if not os.path.isdir(simdir):
    os.makedirs(simdir)

for ds in datasets:
    treeprefix = os.path.join(treedir, ds + "_")
    simprefix = os.path.join(simdir, ds + "_")
    treepath = os.path.join("../data_new/treebase/raxml/", ds, "default_inference.raxml.bestTree")
    alignpath = os.path.join("../data_new/treebase/msa_nodup", ds + ".phy")
    simulate(treepath, alignpath, treeprefix, simprefix)
