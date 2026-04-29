rule find_best_tree:
    input:
        log_file1 = raxmlng_prefix + ".raxml.log",
        log_file2 = search80_prefix + ".raxml.log",
        best_tree1 = raxmlng_prefix + ".raxml.bestTree",
        best_tree2 = search80_prefix + ".raxml.bestTree",
    output:
        best_tree = search100_prefix + ".raxml.bestTree"
    script:
        "scripts/find_best_tree.py"
