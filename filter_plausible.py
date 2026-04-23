import os

threshold = 0.05

data_type = "sim"

au_d = os.path.join("data/", data_type, "au")
ml_d = os.path.join("data/", data_type, "difficulty_labels")

for msa_name in os.listdir(au_d):
    ml_trees_path = os.path.join(ml_d, msa_name, "labelGen.raxml.mlTrees")
    if not os.path.isfile(ml_trees_path):
        continue
    with open(ml_trees_path, "r") as trees_file:
        ml_tree_strings = trees_file.read().split("\n")
    au_path = os.path.join(au_d, msa_name, "au.raxml.treeTests")
    if not os.path.isfile(au_path):
        continue
    with open(au_path, "r") as au_file:
        au_results = au_file.read().split("\n")[:-1]
    plausible_tree_strings = []
    for i, line in enumerate(au_results):
        au_score = float(line.split("\t")[1])
        if au_score > threshold:
            plausible_tree_strings.append(ml_tree_strings[i])
    plausible_trees_path = os.path.join(au_d, msa_name, "plausible.trees")
    print(len(plausible_tree_strings))
    with open(plausible_trees_path, "w+") as outfile:
        outfile.write("\n".join(plausible_tree_strings))




