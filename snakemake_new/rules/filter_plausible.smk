rule filter_plausible:
    group:
        "msa_{cat}_{msa}" 
    input:
        ml_trees = search100_prefix + ".raxml.mlTrees",
        test_values = au_prefix + ".raxml.treeTests",
    output:
        plausible_trees = search100_prefix + ".raxml.plausibleTrees"
    script:
        "scripts/filter_plausible.py"
