rule find_best_tree_collapsed:
    input:
        log_file1 = raxmlng_prefix + ".raxml.log",
        log_file2 = search80_prefix + ".raxml.log",
        best_tree1 = raxmlng_prefix + ".raxml.bestTreeCollapsedStrict",
        best_tree2 = search80_prefix + ".raxml.bestTreeCollapsedStrict",
    output:
        best_tree = search100_prefix + ".raxml.bestTreeCollapsedStrict"
    script:
        "scripts/find_best_tree.py"
