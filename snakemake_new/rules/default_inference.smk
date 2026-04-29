rule default_inference:
    input:
       msa_nodup = msa_nodup_path, 
    output:
        best_tree = raxmlng_prefix + ".raxml.bestTree",
    params:
        prefix  = raxmlng_prefix,
    log:
        cmdlog = raxmlng_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng "
        "--msa {input.msa_nodup} "
        "--tree pars{{10}},rand{{10}} "
        "--model  GTR+G "
        "--prefix {params.prefix} "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "
