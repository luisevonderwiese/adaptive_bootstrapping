import os
import shutil

def get_score(logstring):
    return float(logstring.split("Final LogLikelihood: ")[1].split("\n")[0])

scores = []
for logpath in [snakemake.input.log_file1, snakemake.input.log_file2]:
    with open(snakemake.input.log_file1, "r") as logfile:
        scores.append(get_score(logfile.read()))

if scores[0] >= scores[1]:
    shutil.copy(snakemake.input.best_tree1, snakemake.output.best_tree)
else:
    shutil.copy(snakemake.input.best_tree1, snakemake.output.best_tree)

