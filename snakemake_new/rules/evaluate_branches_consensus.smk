rule evaluate_branches_consensus:
    input:
        selection_stats = selection_stats_path,
        support_tree = consensus_support_prefix + ".raxml.support",
    params: 
        support_metric = "sbs_Support_consensus",
        support_factor = "1", 
        true_tree = lambda wildcards: all_true_trees[wildcards.cat][wildcards.msa], 
        best_tree = "",
    output:
        branch_stats = consensus_branch_stats_path,
    script:
        "scripts/evaluate_branches.py"
