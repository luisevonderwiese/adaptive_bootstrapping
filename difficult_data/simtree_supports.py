import os


def run_support(treepath, bs_trees, prefix):
    command = "./../snakemake_new/bin/raxml-ng --support"
    command += " --tree " + treepath
    command += " --model GTR+G"
    command += " --prefix " + prefix
    command += " --bs-trees " + bs_trees
    command += " --bs-metric fbp --seed 2 --threads 8"
    os.system(command)

for fn in os.listdir("alisim2/simtrees"):
    if not fn.endswith("_d.tree"):
        continue
    ds = "_".join(fn.split("_")[:-1])
    bs_trees = os.path.join("alisim2/raxml", ds + "_d", "bootstrapping.raxml.bootstraps")
    if not os.path.isfile(bs_trees):
        continue
    prefix_dir = os.path.join("simtree_supports", ds)
    if not os.path.isdir(prefix_dir):
        os.makedirs(prefix_dir)
    prefix = os.path.join(prefix_dir, "support_a")
    treepath = os.path.join("../data_new/treebase/raxml/", ds, "default_inference.raxml.bestTree")
    run_support(treepath, bs_trees, prefix)
    prefix = os.path.join(prefix_dir, "support_b")
    treepath = os.path.join("alisim2/simtrees", fn)
    run_support(treepath, bs_trees, prefix)

