import os
import pandas as pd
import matplotlib.pyplot as plt

for data_type in ["sim", "treebase"]:
    plots_dir = os.path.join("data", data_type, "plots")
    if not os.path.isdir(plots_dir):
        os.makedirs(plots_dir)
    df = pd.read_csv(os.path.join("data", data_type, "avg_supports.csv")).merge(pd.read_csv(os.path.join("data", data_type, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")

    plt.scatter(df["avg_support_bs"], df["avg_support_ml"], s = 10)
    plt.xlabel("avg_support_bs")
    plt.ylabel("avg_support_ml")
    plt.savefig(os.path.join("data", data_type, "plots/avg_supports.png"))
    plt.clf()

    plt.scatter(df["difficulty"], df["avg_support_ml"], s = 10)
    plt.xlabel("difficulty")
    plt.ylabel("avg_support_ml")
    plt.savefig(os.path.join("data", data_type, "plots/avg_support_ml_difficulty.png"))
    plt.clf()

    plt.scatter(df["difficulty"], df["avg_support_bs"], s = 10)
    plt.xlabel("difficulty")
    plt.ylabel("avg_support_bs")
    plt.savefig(os.path.join("data", data_type, "plots/avg_support_bs_difficulty.png"))
    plt.clf()
