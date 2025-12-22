import os
import pandas as pd
import pypythia.prediction as pred
import pathlib

data_dir = "/hits/fast/cme/hoehledi/example_workflow/run_sparta/out/tb_mirror"
res = []
for ds in os.listdir(data_dir):
    msa_path = os.path.join(data_dir, ds, "gtr_g_sim_msa.fasta")
    if not os.path.isfile(msa_path):
        continue
    with open(msa_path, "r") as msa_file:
        size = msa_file.read().count(">")
    try:
        difficulty = pred.predict_difficulty(pathlib.Path(msa_path))
    except Exception as e:
        print(e)
        continue
    res.append([ds, size, difficulty])

df = pd.DataFrame(res, columns = ["dataset", "size", "difficulty"])
outdir = "output"
if not os.path.isdir(outdir):
    os.makedirs(outdir)
df.to_csv(os.path.join(outdir, "properties.csv"))
