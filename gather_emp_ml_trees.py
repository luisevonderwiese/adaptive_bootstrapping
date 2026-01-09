import os

msa_dir = "data/treebase/msa"
out_dir = "data/treebase/ml_trees"

if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

for msa_name in os.listdir(msa_dir):
    out_path =  os.path.join(out_dir, msa_name.split(".")[0] + ".mlTrees")
    if os.path.isfile(out_path):
        continue
    res_dir = os.path.join("/hits/basement/cme/schmidja/difficulty_training_data/TreeBase_results/", msa_name, "output_files/raxmlng/inference/")
    if not os.path.isdir(res_dir):
        print("results don't exist")
        continue
    ml_trees = ""
    t = "pars"
    results_complete = True
    for i in range(100):
        if i == 50:
            t = "rand"
        best_tree_path = os.path.join(res_dir, t + "_" + str(i) + ".raxml.bestTree")
        if not os.path.isfile(best_tree_path):
            print("results not complete")
            results_complete = False
            break
        with open(best_tree_path, "r") as tree_file:
            ml_trees += tree_file.read() + "\n"
    if results_complete:
        with open(out_path, "w+") as out_file:
            out_file.write(ml_trees)
