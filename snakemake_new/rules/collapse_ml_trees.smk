rule collapse_ml_trees:
    input:
        trees = search100_prefix + ".raxml.mlTrees",
        selection_stats = selection_stats_path,
    output:
        trees_collapsed = search100_prefix + ".raxml.mlTreesCollapsedStrict"
    script:
        "scripts/collapse_trees.py"
