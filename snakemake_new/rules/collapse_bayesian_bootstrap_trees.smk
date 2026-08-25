rule collapse_baysian_bootstrapping_trees:
    input:
        trees = bootstrapping_bayesian_prefix + ".raxml.bootstraps",
        selection_stats = selection_stats_path,
    output:
        trees_collapsed = bootstrapping_bayesian_prefix + ".raxml.bootstrapsCollapsedStrict"
    script:
        "scripts/collapse_trees.py"
