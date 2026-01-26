import pandas as pd
import matplotlib.pyplot as plt
import shutil
import os

df = pd.read_csv("output/properties.csv")
examined_datasets = [ds for ds in os.listdir("../data/sim/bootstrapping")]
res = []
for i, row in df.iterrows():
    if row["dataset"] in examined_datasets:
        continue
    if row["difficulty"] < 0.5:
        continue
    res.append([row["dataset"], row["difficulty"], row["size"]])

test = pd.DataFrame(res, columns = ["dataset", "difficulty", "size"])
print(len(test))
plt.scatter(test["size"], test["difficulty"], s = 10)
plt.xscale("log")
plt.savefig("output/sample_difficult.png")
plt.clf()

outdir = "../data/sim_difficult/msa"
if not os.path.isdir(outdir):
    os.makedirs(outdir)

msa_dir = "/hits/fast/cme/hoehledi/example_workflow/run_sparta/out/tb_mirror"
for i, row in test.iterrows():
    ds = row["dataset"]
    dest_dir = os.path.join(outdir, ds)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    dest = os.path.join(dest_dir, "gtr_g_sim_msa.fasta")
    src = os.path.join(msa_dir, ds, "gtr_g_sim_msa.fasta")
    shutil.copy(src, dest)
    dest = os.path.join(dest_dir, "gtr_g.raxml.bestTree")
    src = os.path.join(msa_dir, ds, "gtr_g.raxml.bestTree")
    shutil.copy(src, dest)


