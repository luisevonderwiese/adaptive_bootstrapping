import os
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from ete3 import Tree
import sys

msa_nodup_path = snakemake.input.msa_nodup
true_tree_path = snakemake.params.true_tree
outpath = snakemake.output.true_tree_nodup

if true_tree_path == "":
    os._exit(1)

ending = msa_nodup_path.split(".")[-1]
if ending == "fasta" or ending == "fa":
    f = "fasta"
elif ending == "phy" or ending == "phylip":
    f = "phylip-relaxed"
else:
    print(ending, "not supported")
align = AlignIO.read(msa_nodup_path, f)
nodup_taxa = list(seq.id for seq in align)

true_tree = Tree(true_tree_path)
for leaf in true_tree.iter_leaves():
    if not leaf.name in nodup_taxa:
        leaf.delete()

true_tree.write(outfile = outpath)
