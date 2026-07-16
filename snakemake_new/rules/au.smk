rule au:
    group:
        "msa_{cat}_{msa}"
    input:
        msa_nodup = msa_nodup_path,
        ml_trees = search100_prefix + ".raxml.mlTrees",
    output:
        au_values = au_prefix + ".raxml.treeTests"
    params:
        prefix  = au_prefix,
    log:
        cmdlog = au_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng-au --au-test "
        "--model GTR+G "
        "--msa {input.msa_nodup} "
        "--tree {input.ml_trees} "
        "--prefix {params.prefix} "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "

