rule evaluate_branches_shalrt:
    input:
        selection_stats = selection_stats_path,
        support_tree = shalrt_prefix + ".raxml.supportSH"
    params:    
        support_metric = "shalrt_Support",
        support_factor = "1", 
        true_tree = lambda wildcards: all_true_trees[wildcards.cat][wildcards.msa],
        best_tree = ""
    output:
        branch_stats = shalrt_branch_stats_path,
    script:
        "scripts/evaluate_branches.py"
