import os
import pandas as pd
import shutil
from Bio import AlignIO



def read_model(model_path):
    count = 0
    model = ""
    with open(model_path) as file:
        for line in file:
            line = line.rstrip()
            model = line.split(",")[0]
            count += 1
        if count > 1:
            raise ValueError(f"{model_path} contains more than 1 partition!")
    return model


def run_alisim(out_path, tree_path, model_path, m):
    out_path = str(out_path)
    msa_dir = os.path.dirname(out_path)

    model_str = read_model(model_path)
    model_str = model_str.replace("+G4m{", "+G4{")

    command = "./../snakemake_new/bin/iqtree2 --alisim "
    command += out_path
    command += " -t " + tree_path
    command += " -m " + model_str
    command += " --length " + str(m)
    command += " -af fasta"
    command += " --seed 1 "
    os.system(command)

base_dir = "../difficult_data/evonaps_difficult"
outdir = os.path.join("evonaps_sim", "msa")
if not os.path.isdir(outdir):
    os.makedirs(outdir)
df = pd.read_csv(os.path.join(base_dir, "difficulty_labels.csv"))
df = df[df["difficulty"] > 0.7]
difficult_datasets = list(set(df["dataset"]))
for dataset in difficult_datasets:
    msa_path = os.path.join(base_dir, "msa_nodup", dataset + ".phy")
    align = AlignIO.read(msa_path, "phylip-relaxed")
    m = align.get_alignment_length()
    tree_path = os.path.join(base_dir, "raxml", dataset, "default_inference.raxml.bestTreeCollapsedStrict")
    model_path = os.path.join(base_dir, "raxml", dataset, "default_inference.raxml.bestModel")
    out_path =  os.path.join(outdir, dataset)
    run_alisim(out_path, tree_path, model_path, m)



