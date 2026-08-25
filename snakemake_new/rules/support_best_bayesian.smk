rule support_best_bayesian:
    input:
       bs_trees = bootstrapping_bayesian_prefix + ".raxml.bootstrapsCollapsedStrict",
       best_tree = raxmlng_prefix + ".raxml.bestTreeCollapsedStrict"
    output:
        support_tree = best_bayesian_support_prefix + ".raxml.support",
    params:
        prefix  = best_bayesian_support_prefix,
    log:
        cmdlog = best_bayesian_support_prefix + ".raxml.cmdlog",
    threads: 8
    resources:
        mem_mb = 4000,
        disk_mb = 4000,
        run_time = 480,
    shell:
        "./bin/raxml-ng --support "
        "--tree {input.best_tree} "
        "--model  GTR+G "
        "--prefix {params.prefix} "
        "--bs-trees {input.bs_trees} "
        "--bs-metric fbp "
        "--seed 2 "
        "--threads 8 "
        "--redo "
        "> {log.cmdlog} "
