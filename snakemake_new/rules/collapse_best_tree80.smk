rule collapse_best_tree80:
    input:
        tree = search80_prefix + ".raxml.bestTree",
        selection_stats = selection_stats_path,
    output:
        tree_collapsed = search80_prefix + ".raxml.bestTreeCollapsedStrict"
    script:
        "scripts/collapse_tree.py"
