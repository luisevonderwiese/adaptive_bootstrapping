import os
import pandas as pd
from ete3 import Tree



def avg_support(t):
    supports = [node.support for node in t.traverse()]
    return sum(supports) / len(supports)


for data_type in ["sim", "treebase"]:
    res = []
    outdir = os.path.join("data", data_type, "bootstrapping")
    for ds in os.listdir(outdir):
        if data_type == "treebase":
            bs_path = os.path.join(outdir, ds, "fbp.raxml.support")
        else:
            bs_path = os.path.join(outdir, ds, "bootstrap.raxml.support")
        ml_path = os.path.join(outdir, ds, "fbp_ml.raxml.support")
        if not os.path.isfile(bs_path) or not os.path.isfile(ml_path):
            continue
        avg_bs = avg_support(Tree(bs_path))
        avg_ml = avg_support(Tree(ml_path))
        print(avg_bs)
        print(avg_ml)
        res.append([ds, avg_bs, avg_ml])
    df = pd.DataFrame(res, columns = ["dataset", "avg_support_bs", "avg_support_ml"])
    df.to_csv(os.path.join("data", data_type, "avg_supports.csv"))

