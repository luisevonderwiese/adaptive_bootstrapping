rule collapse_best_tree:
    input:
        tree = raxmlng_prefix + ".raxml.bestTree",
        selection_stats = selection_stats_path,
    output:
        tree_collapsed = raxmlng_prefix + ".raxml.bestTreeCollapsedStrict"
    script:
        "scripts/collapse_tree.py"
