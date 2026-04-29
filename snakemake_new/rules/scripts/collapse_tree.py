import os
import pandas as pd
from ete3 import Tree
from collapse import collapse_branches

t = Tree(snakemake.input.tree)
avg_seq_len = pd.read_csv(snakemake.input.selection_stats).iloc[0]["avg_seq_len"]
collapse_branches(t, avg_seq_len)
t.write(outfile = snakemake.output.tree_collapsed, format = 5)
