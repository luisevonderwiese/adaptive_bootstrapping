rule generate_label:
    input:
        msa_nodup = msa_nodup_path,
        ml_trees = search100_prefix + ".raxml.mlTrees",
        best_tree = search100_prefix + ".raxml.bestTree"
    output:
        bootstraps = label_prefix + ".csv",
    params:
        prefix  = label_prefix,
    log:
        cmdlog = label_prefix + ".label.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "label "
        "--msa {input.msa_nodup} "
        "--mltrees {input.ml_trees} "
        "--besttree {input.best_tree} "
        "--model  GTR+G "
        "--prefix {params.prefix} "
        "--raxmlng /hits/fast/cme/haeusele/adaptive_bootstrapping/snakemake_new/bin/raxml-ng "
        "--iqtree /hits/fast/cme/haeusele/adaptive_bootstrapping/snakemake_new/bin/iqtree2 "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "

