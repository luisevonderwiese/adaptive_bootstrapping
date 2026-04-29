rule fuse_ml_trees:
    input:
        ml_trees1 = raxmlng_prefix + ".raxml.mlTrees",
        ml_trees2 = search80_prefix + ".raxml.mlTrees",
    output:
        fused_trees = search100_prefix + ".raxml.mlTrees"
    script:
        "scripts/fuse_ml_trees.py"
