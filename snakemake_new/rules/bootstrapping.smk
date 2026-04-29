rule bootstrapping:
    input:
        msa_nodup = msa_nodup_path,
    output:
        bootstraps = bootstrapping_prefix + ".raxml.bootstraps",
    params:
        prefix  = bootstrapping_prefix,
    log:
        cmdlog = bootstrapping_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng --bootstrap "
        "--msa {input.msa_nodup} "
        "--model  GTR+G "
        "--prefix {params.prefix} "
        "--bs-trees 100 "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "

