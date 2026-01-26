import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import shutil
import os

def classes_to_remove(df):
    classes = list(set(df["class"]))
    rc = []
    unique = []
    for c in classes:
        sub_df = df[df["class"] == c]
        if len(sub_df) == 1:
            unique.append(sub_df.iloc[0]["dataset"])
            rc.append(c)
    return rc, unique

def d_class(difficulty):
    return int(difficulty * 10)

def s_class(size):
    if size < 100:
        return int(size / 10)
    return 10 + int(size / 100)
def class_string(row):
    return str(s_class(row["size"])) + "_" + str(d_class(row["difficulty"]))


df = pd.read_csv("output/properties.csv")
df["class"] = [class_string(row) for _, row in df.iterrows()]
print(len(df))
plt.scatter(df["size"], df["difficulty"], s = 10)
plt.xscale("log")
plt.savefig("output/full.png")
plt.clf()

rc, unique = classes_to_remove(df)
print(rc)
unique_df = df[df["class"].isin(rc)]
df = df[~df["class"].isin(rc)]

train, test = train_test_split(df, train_size=0.9, random_state=None, shuffle=True, stratify=df["class"])

test = pd.concat([test, unique_df])
print(len(test))
plt.scatter(test["size"], test["difficulty"], s = 10)
plt.xscale("log")
plt.savefig("output/sample.png")
plt.clf()

outdir = "../data/sim/msa"
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


