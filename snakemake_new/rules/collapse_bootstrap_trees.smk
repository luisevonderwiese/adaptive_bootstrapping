rule collapse_bootstrapping_trees:
    input:
        trees = bootstrapping_prefix + ".raxml.bootstraps",
        selection_stats = selection_stats_path,
    output:
        trees_collapsed = bootstrapping_prefix + ".raxml.bootstrapsCollapsedStrict"
    script:
        "scripts/collapse_trees.py"
