import os

with open(snakemake.input.ml_trees1, "r") as infile:
    s = infile.read()
    
with open(snakemake.input.ml_trees2, "r") as infile:
    s += infile.read()

with open(snakemake.output.fused_trees, "w+") as outfile:
    outfile.write(s)


