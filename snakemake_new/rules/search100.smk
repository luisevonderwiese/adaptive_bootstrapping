rule search100:
    input:
       msa_nodup = msa_nodup_path,
    output:
        ml_tree = search100_prefix + ".raxml.mlTrees",
    params:
        prefix  = search100_prefix,
    log:
        cmdlog = search100_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng "
        "--msa {input.msa_nodup} "
        "--model  GTR+G "
        "--tree pars{{50}},rand{{50}} "
        "--prefix {params.prefix} "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "


