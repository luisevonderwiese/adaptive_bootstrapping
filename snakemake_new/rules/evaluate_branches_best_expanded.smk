rule evaluate_branches_best_expanded:
    input:
        selection_stats = selection_stats_path,
        support_tree = best_expanded_support_prefix + ".raxml.support", 
    params:    
        support_metric = "sbs_Support",
        support_factor = "1", 
        true_tree = lambda wildcards: all_true_trees[wildcards.cat][wildcards.msa],
        best_tree = raxmlng_prefix + ".raxml.bestTree"
    output:
        branch_stats = best_expanded_branch_stats_path,
    script:
        "scripts/evaluate_branches.py"
