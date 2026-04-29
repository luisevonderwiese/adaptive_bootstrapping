import os
import pandas as pd
from ete3 import Tree
from collapse import collapse_branches

with open(snakemake.input.trees, "r") as infile:
    trees = [Tree(line) for line in infile.readlines()]
avg_seq_len = pd.read_csv(snakemake.input.selection_stats).iloc[0]["avg_seq_len"]
for t in trees:
    collapse_branches(t, avg_seq_len)
with open(snakemake.output.trees_collapsed, "w+") as outfile:
    outfile.write("\n".join([t.write(format = 5) for t in trees]))
