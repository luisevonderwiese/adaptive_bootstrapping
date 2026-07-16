rule remove_duplicates_from_true_tree:
    input:
        msa_nodup = msa_nodup_path,
    output:
        true_tree_nodup = true_tree_nodup_path,
    params:
        true_tree = lambda wildcards: all_true_trees[wildcards.cat][wildcards.msa],
    script:
        "scripts/remove_duplicates_from_true_tree.py"
