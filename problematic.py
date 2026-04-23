import os
import pandas as pd
from ete3 import Tree
from tabulate import tabulate
import shutil
import re

from Bio import AlignIO
from Bio.AlignIO.PhylipIO import RelaxedPhylipWriter


def rf_dist(t1, t2):
    if t1 is None or t2 is None:
        return float('nan')
    if t1 != t1 or t2 != t2:
        return float("nan")
    rf, max_rf, common_leaves, parts_t1, parts_t2,discard_t1, discart_t2 = t1.robinson_foulds(t2, unrooted_trees = True)
    if max_rf == 0:
        return float('nan')
    return rf/max_rf


def count_occurrences(true_tree, ml_trees):
    c = 0
    for t in ml_trees:
        if rf_dist(true_tree, t) == 0:
            c += 1
    return c

def run_au(msa_path, true_tree_path, best_tree_path, prefix):
    with open(best_tree_path, "r") as infile:
        s = infile.read()
    with open(true_tree_path, "r") as infile:
        s += infile.read()
    with open("temp.tree", "w+") as outfile:
        outfile.write(s)
    command = "./snakemake/raxml-ng-au --au-test --msa "
    command += msa_path
    command += " --model GTR+G "
    command += " --tree temp.tree"
    command += " --prefix " + prefix
    os.system(command)

def parse_au(prefix):
    au_path = prefix + ".raxml.treeTests"
    with open(au_path, "r") as au_file:
        au_results = au_file.read().split("\n")[:-1]
    au_score = float(au_results[1].split("\t")[1])
    if au_score > 0.05:
        return (au_score, True)
    else:
        return (au_score, False)

def run_moose(msa_path, prefix):
    command = "./snakemake/raxml-ng-2 --moose --data-type DNA --msa "
    command += msa_path
    command += " --prefix " + prefix
    os.system(command)

def parse_moose(prefix):
    print(prefix + ".raxml.log")
    with open(prefix + ".raxml.log", "r") as logfile:
        log = logfile.read()
    parts = log.split("Best model(s):\n")
    if len(parts) != 2:
        return None
    parts = re.split(r'\s+', parts[1])
    best_model = parts[2]
    best_score = float(parts[8][:-1])
    if best_model.endswith("m"):
        best_model = best_model[:-1]
    parts = log.split("Evaluated model")
    if len(parts) < 3:
        return None
    parts = parts[1:-1]
    parts = [re.split(r'\s+', part.split(")")[1]) for part in parts]
    score_map = {row[1] : float(row[4]) for row in parts}
    return (best_model, best_score, score_map["GTR+FO+G4"])
    
def run_true_start(msa_path, true_tree_path, prefix):
    command = "./snakemake/raxml-ng-2 --search1 --model GTR+G --msa "
    command += msa_path
    command += " --tree " + true_tree_path
    command += " --prefix " + prefix
    os.system(command)


def run_iqtree(msa_path, prefix):
    command = "./snakemake/iqtree2 -m GTR+FO+G"
    command += " -s " + msa_path
    command += " --prefix " + prefix
    os.system(command)

def convert_to_phy(msa_path, out_path):
    align = AlignIO.read(msa_path, "fasta")
    with open(out_path, "w+") as f:
        writer = RelaxedPhylipWriter(f)
        writer.write_alignment(align)

def run_phyml(msa_path, prefix_dir):
    command = "./snakemake/phyml -n 1 --model GTR -f o --pars --search BEST -i "
    command += msa_path
    os.system(command)
    tmp_prefix = msa_path + "_phyml"
    os.system("mv " + tmp_prefix + "* " + prefix_dir)


label_super_dir = "data/sim/difficulty_labels"
msa_super_dir  = "data/sim/msa"
datasets = ['14534_15', '19979_0', '115_1', '12863_0', '11906_1', '19116_1', '420_2', '654_0', '11477_2', '633_0', '11677_1', '24053_1', '19596_0', '17621_4', '13159_4', '14534_16', '19714_6', '14676_0', '16453_5', '10126_2', '10754_1', '12057_0', '723_0', '10307_2', '12786_9', '15971_1', '320_0', '10425_3', '16275_0', '12540_8', '19692_0', '17674_0', '11677_0']

res = []
df = pd.read_csv("data/sim/problematic.csv")
datasets = list(df["dataset"])
for dataset in datasets:
    msa_path = os.path.join("data/sim/msa/", dataset + ".phy", "gtr_g_sim_msa.fasta")
    true_tree_path = os.path.join("data/sim/msa/", dataset + ".phy", "gtr_g.raxml.bestTree")
    best_tree_path = os.path.join("data/sim/bootstrapping/", dataset, "bootstrap.raxml.bestTree")
    ml_trees_path = os.path.join("data/sim/difficulty_labels/", dataset, "labelGen.raxml.mlTrees")
    
    true_tree = Tree(true_tree_path)
    with open(ml_trees_path, "r") as infile:
        ml_tree_strings = infile.readlines()
    ml_trees = [Tree(s) for s in ml_tree_strings]
    occ = count_occurrences(true_tree, ml_trees)

    outdir = os.path.join("problematic/au", dataset)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    prefix = os.path.join(outdir, "au")
    #run_au(msa_path, true_tree_path, best_tree_path, prefix)
    (au, plausible) = parse_au(prefix)

    outdir = os.path.join("problematic/moose", dataset)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    prefix = os.path.join(outdir, "moose")
    #run_moose(msa_path, prefix)
    (best_model, best_score, gtr_score) = parse_moose(prefix)

    outdir = os.path.join("problematic/true_start", dataset)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    prefix = os.path.join(outdir, "inference")
    run_true_start(msa_path, true_tree_path, prefix)
    inferred_tree = Tree(prefix + ".raxml.bestTree")
    rf_dist_true_start = rf_dist(inferred_tree, true_tree)
    
    outdir = os.path.join("problematic/phy", dataset)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    phy_path = os.path.join(outdir, dataset + ".phy")
    convert_to_phy(msa_path, phy_path)
    outdir = os.path.join("problematic/phyml", dataset)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    #run_phyml(phy_path, outdir)
    #inferred_tree = Tree(os.path.join(outdir, dataset + ".phy_phyml_tree.txt"))
    #rf_dist_phyml = rf_dist(inferred_tree, true_tree)
    
    outdir = os.path.join("problematic/iqtree", dataset)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    prefix = os.path.join(outdir, "inference")
    #run_iqtree(phy_path, prefix)
    #inferred_tree = Tree(prefix + ".treefile")
    #rf_dist_iqtree = rf_dist(inferred_tree, true_tree)
    res.append([dataset, occ, plausible, rf_dist_true_start, best_model, best_score, gtr_score])

print(tabulate(res, headers = ["dataset", "occ (100)", "plausible", "rf_dist_true_start", "best_model", "best_score", "score_used"], tablefmt = "pipe"))
