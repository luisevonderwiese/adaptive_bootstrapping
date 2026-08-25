rule generate_label:
    input:
        msa_nodup = msa_nodup_path,
    output:
        label = label_prefix + ".csv",
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
        "--model  GTR+G "
        "--prefix {params.prefix} "
        "--raxmlng /hits/fast/cme/haeusele/adaptive_bootstrapping/snakemake_new/bin/raxml-ng "
        "--iqtree /hits/fast/cme/haeusele/adaptive_bootstrapping/snakemake_new/bin/iqtree2 "
        "--ntrees 100 "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "

