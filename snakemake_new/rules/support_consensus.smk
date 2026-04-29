rule support_consensus:
    input:
       bs_trees = bootstrapping_prefix + ".raxml.bootstrapsCollapsedStrict",
       consensus_tree = consensus_prefix + ".raxml.consensusTreeMR"
    output:
        support_tree = consensus_support_prefix + ".raxml.support",
    params:
        prefix  = consensus_support_prefix,
    log:
        cmdlog = consensus_support_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng --support "
        "--tree {input.consensus_tree} "
        "--model  GTR+G "
        "--prefix {params.prefix} "
        "--bs-trees {input.bs_trees} "
        "--bs-metric fbp "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "
