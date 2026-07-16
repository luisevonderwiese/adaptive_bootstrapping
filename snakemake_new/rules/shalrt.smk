rule shalrt:
    input:
       msa_nodup = msa_nodup_path, 
       best_tree = raxmlng_prefix + ".raxml.bestTree"
    output:
        support_tree = shalrt_prefix + ".raxml.supportSH",
    params:
        prefix  = shalrt_prefix,
    log:
        cmdlog = shalrt_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng --sh "
        "--msa {input.msa_nodup} "
        "--tree {input.best_tree} "
        "--model  GTR+G "
        "--prefix {params.prefix} "
        "--sh-reps 10000 "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "
