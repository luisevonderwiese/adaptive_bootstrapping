rule remove_duplicates:
    output:
        msa_nodup = msa_nodup_path,
    params:
        msa = lambda wildcards: msas[wildcards.cat][wildcards.msa],
    script:
        "scripts/remove_duplicates.py"
