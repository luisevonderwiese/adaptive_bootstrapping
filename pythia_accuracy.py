import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

def plot_accuracy(base_dir, data_type, nodup_prediction):
    plots_dir = os.path.join(base_dir, data_type, "plots")
    if not os.path.isdir(plots_dir):
        os.makedirs(plots_dir)
    if nodup_prediction:
        predict_path = os.path.join(base_dir, data_type, "difficulty_prediction_nodup.csv")
    else:
        predict_path = os.path.join(base_dir, data_type, "difficulty_prediction.csv")
    df = pd.read_csv(predict_path).merge(pd.read_csv(os.path.join(base_dir, data_type, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    plt.figure(figsize=(9, 6))
    plt.scatter(df["difficulty"], df["difficulty_prediction"], s = 6)
    mae = mean_absolute_error(df["difficulty"], df["difficulty_prediction"])
    mape = mean_absolute_percentage_error(df["difficulty"], df["difficulty_prediction"])
    print(mae)
    print(mape)
    plt.gca().axline((0, 0), slope=1, color='grey', linestyle = "--")
    plt.xlabel("ground truth")
    plt.ylabel("prediction")
    if nodup_prediction:
        out_path = os.path.join(plots_dir, "pythia_accuracy_nodup.png")
    else:
        out_path = os.path.join(plots_dir, "pythia_accuracy.png")
    plt.savefig(out_path)
    plt.clf()


def plot_collapse_effect(base_dir, data_type):
    print(data_type)
    plots_dir = os.path.join(base_dir, data_type, "plots")
    if not os.path.isdir(plots_dir):
        os.makedirs(plots_dir)
    df = pd.read_csv(os.path.join(base_dir, data_type, "difficulty_labels_collapsed.csv")).merge(pd.read_csv(os.path.join(base_dir, data_type, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    plt.figure(figsize=(9, 6))
    plt.scatter(df["difficulty"], df["difficulty_collapsed"], s = 6)
    #mae = mean_absolute_error(df["difficulty"], df["difficulty_collapsed"])
    #mape = mean_absolute_percentage_error(df["difficulty"], df["difficulty_collapsed"])
    #print(mae)
    #print(mape)
    plt.xlabel("ground truth")
    plt.ylabel("groud truth (collapsed)")
    plt.savefig(os.path.join(plots_dir, "pythia_collapsed.png"))
    plt.clf()


def plot_collapse_effect(base_dir, data_type):
    plots_dir = os.path.join(base_dir, data_type, "plots")
    if not os.path.isdir(plots_dir):
        os.makedirs(plots_dir)
    df = pd.read_csv(os.path.join(base_dir, data_type, "difficulty_labels_collapsed.csv")).merge(pd.read_csv(os.path.join(base_dir, data_type, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    plt.figure(figsize=(9, 6))
    plt.scatter(df["difficulty"], df["difficulty_collapsed"], s = 6)
    plt.xlabel("ground truth")
    plt.ylabel("groud truth (collapsed)")
    plt.savefig(os.path.join(plots_dir, "pythia_collapsed.png"))
    plt.clf()

def plot_nodup_effect(base_dir, base_dir_nodup, data_type):
    plots_dir = os.path.join(base_dir_nodup, data_type, "plots")
    if not os.path.isdir(plots_dir):
        os.makedirs(plots_dir)
    df = pd.read_csv(os.path.join(base_dir_nodup, data_type, "difficulty_labels.csv")).merge(pd.read_csv(os.path.join(base_dir, data_type, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner", suffixes = ["_nodup", "_old"])
    print(len(df[df["difficulty_old"] >= df["difficulty_nodup"]]) / len(df))
    equal = 0
    increase = 0
    decrease = 0
    for i, row in df.iterrows():
        diff = row["difficulty_nodup"] - row["difficulty_old"]
        if diff == 0:
            equal += 1
        elif diff > 0:
            increase += 1
        else:
            decrease += 1

    print("equal", str(equal / len(df)))
    print("increase", str(increase / len(df)))
    print("decrease", str(decrease / len(df)))
    plt.figure(figsize=(9, 6))
    plt.scatter(df["difficulty_old"], df["difficulty_nodup"], s = 6)
    plt.xlabel("difficult (original)")
    plt.ylabel("difficulty (no dup.)")
    plt.gca().axline((0, 0), slope=1, color='grey', linestyle = "--")
    plt.savefig(os.path.join(plots_dir, "pythia_nodup.png"))
    plt.clf()





#plot_accuracy("difficult_data", "alisim2", False)
#plot_accuracy("difficult_data", "alisim2", True)
#plot_accuracy("difficult_data", "evonaps_difficult", False)
#plot_accuracy("difficult_data", "evonaps_difficult", True)

#plot_accuracy("data", "sim", False)
plot_accuracy("data", "sim", True)
#plot_accuracy("data", "treebase", False)
plot_accuracy("data", "treebase", True)

#plot_collapse_effect("data", "sim")
#plot_collapse_effect("data", "treebase")

plot_nodup_effect("data_reworked", "data", "sim")
plot_nodup_effect("data_reworked", "data", "treebase")
