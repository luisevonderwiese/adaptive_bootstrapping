rule collapse_true_tree:
    input:
        tree = true_tree_nodup_path,
        selection_stats = selection_stats_path,
    output:
        tree_collapsed = true_tree_collapsed_path,
    script:
        "scripts/collapse_tree.py"
