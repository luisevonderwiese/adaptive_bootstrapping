import shutil
import os

sim_dir = "data_new/sim/msa"
if not os.path.isdir(sim_dir):
    os.makedirs(sim_dir)

treebase_dir = "data_new/treebase/msa"
if not os.path.isdir(treebase_dir):
    os.makedirs(treebase_dir)

msa_dir = "/hits/fast/cme/hoehledi/example_workflow/run_sparta/out/tb_mirror"
for ds in os.listdir(msa_dir):
    dest_sim_dir = os.path.join(sim_dir, ds)
    if not os.path.isdir(dest_sim_dir):
        os.makedirs(dest_sim_dir)
    dest_treebase_dir = os.path.join(treebase_dir, ds)
    if not os.path.isdir(dest_treebase_dir):
        os.makedirs(dest_treebase_dir)
    required_files = [os.path.join(msa_dir, ds, "gtr_g_sim_msa.fasta"), \
            os.path.join(msa_dir, ds, "gtr_g.raxml.bestTree"), \
            os.path.join(msa_dir, ds, "msa.fasta")]
    all_present = True
    for required_file in required_files:
        if not os.path.isfile(required_file):
            print(str(required_file), "missing")
            all_present = False
    if not all_present:
        continue
    dest = os.path.join(dest_sim_dir, "msa.fasta")
    src = os.path.join(msa_dir, ds, "gtr_g_sim_msa.fasta")
    shutil.copy(src, dest)
    dest = os.path.join(dest_sim_dir, "true.tree")
    src = os.path.join(msa_dir, ds, "gtr_g.raxml.bestTree")
    shutil.copy(src, dest)
    dest = os.path.join(dest_treebase_dir, "msa.fasta")
    src = os.path.join(msa_dir, ds, "msa.fasta")
    shutil.copy(src, dest)
    print(ds)
                


