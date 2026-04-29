rule selection_stats:
    input:
        best_tree = raxmlng_prefix + ".raxml.bestTree",
        msa_nodup = msa_nodup_path,
    output:
        selection_stats = selection_stats_path,
    script:
        "scripts/selection_stats.py"
