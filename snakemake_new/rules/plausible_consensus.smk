rule plausible_consensus:
    group:
        "msa_{cat}_{msa}"
    input:
        plausible_trees = search100_prefix + ".raxml.plausibleTrees"
    output:
        consensus_tree = consensus_prefix + ".raxml.consensusTreeMR",
    params:
        prefix  = consensus_prefix,
    log:
        cmdlog = consensus_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng --consense MR "
        "--tree {input.plausible_trees} "
        "--prefix {params.prefix} "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "

