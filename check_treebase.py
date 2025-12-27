import os
import shutil

results_dir = "data/treebase/check/"
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
invalid_msas = []
msa_dir = "data/treebase/msa"
for msa in os.listdir(msa_dir):
    msa_path = os.path.join(msa_dir, msa)
    prefix = os.path.join(results_dir, msa + ".check")
    command = "./raxml-ng --check --model GTR+G --msa " + msa_path + " --prefix " + prefix + " > out.txt"
    os.system(command)
    with open(prefix + ".raxml.log", "r") as results_file:
        found = False
        lines = results_file.readlines()
        for line in lines:
            if line.startswith("Alignment can be successfully read by RAxML-NG."):
                found = True
                break
        if not found:
            invalid_msas.append(msa)

target_dir = "data/treebase/invalid_msas"
if not os.path.isdir(target_dir):
    os.makedirs(target_dir)
for msa in invalid_msas:
    s = os.path.join(msa_dir, msa)
    d = os.path.join(target_dir, msa)
    shutil.move(s, d)
