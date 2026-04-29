import os
import pandas as pd
from Bio import AlignIO
from ete3 import Tree
from collapse import zero_threshold

treepath = snakemake.input.best_tree
msapath = snakemake.input.msa_nodup
outpath = snakemake.output.selection_stats


align = AlignIO.read(msapath, "phylip-relaxed")
lengths = []

for record in align:
    seq_str = str(record.seq)
    allowed_set = set(['A', 'C', 'G', 'T'])
    seq_str = ''.join([c for c in seq_str if c in allowed_set])
    lengths.append(len(seq_str))

avg_seq_len = sum(lengths) / len(lengths)
size = len(align)
seq_len = align.get_alignment_length()

threshold = zero_threshold(avg_seq_len) 
max_brlen = 0
zero_branches = 0
internal_branches = 0
t = Tree(treepath)

for node in t.iter_descendants():
    brlen = node.dist
    max_brlen = max(max_brlen, brlen)
    if not node.is_leaf():
        internal_branches += 1
        if brlen <= threshold:
            zero_branches += 1


df = pd.DataFrame([[size, seq_len, avg_seq_len, max_brlen, zero_branches / internal_branches]], \
        columns = ["size", "seq_len", "avg_seq_len", "max_brlen", "r_z"])

df.to_csv(outpath)



