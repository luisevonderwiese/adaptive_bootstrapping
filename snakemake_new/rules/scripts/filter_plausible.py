import os

threshold = 0.05

with open(snakemake.input.ml_trees, "r") as trees_file:
    ml_tree_strings = trees_file.read().split("\n")
with open(snakemake.input.test_values, "r") as au_file:
    au_results = au_file.read().split("\n")[:-1]
plausible_tree_strings = []
for i, line in enumerate(au_results):
    au_score = float(line.split("\t")[1])
    if au_score > threshold:
        plausible_tree_strings.append(ml_tree_strings[i])
with open(snakemake.output.plausible_trees, "w+") as outfile:
    outfile.write("\n".join(plausible_tree_strings))




