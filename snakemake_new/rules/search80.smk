rule search80:
    input:
        msa_nodup = msa_nodup_path,
    output:
        ml_tree = search80_prefix + ".raxml.mlTrees",
    params:
        prefix  = search80_prefix,
    log:
        cmdlog = search80_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng "
        "--msa {input.msa_nodup} "
        "--model  GTR+G "
        "--tree pars{{40}},rand{{40}} "
        "--prefix {params.prefix} "
        "--seed 3 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "


