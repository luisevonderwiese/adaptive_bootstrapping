rule evaluate_branches_best_bayesian:
    input:
        selection_stats = selection_stats_path,
        support_tree = best_bayesian_support_prefix + ".raxml.support", 
    params:    
        support_metric = "bayesian_Support",
        support_factor = "1", 
        true_tree = lambda wildcards: all_true_trees[wildcards.cat][wildcards.msa],
        best_tree = raxmlng_prefix + ".raxml.bestTree"
    output:
        branch_stats = best_bayesian_branch_stats_path,
    script:
        "scripts/evaluate_branches.py"
