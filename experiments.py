import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from collections import Counter
from sklearn.metrics import roc_auc_score
import seaborn as sns

def plot_mean_confidences(confidences, mode):
    for bin, confidence_dicts in confidences.items():
        all_support_values = []
        for confidence_dict in confidence_dicts:
            all_support_values += confidence_dict.keys()
        all_support_values = list(set(all_support_values))
        all_support_values.sort()
        if bin == 9:
            print(all_support_values)
        mean_confidences = []
        for support_value in all_support_values:
            support_confidences = []
            for confidence_dict in confidence_dicts:
                if support_value in confidence_dict:
                    c = confidence_dict[support_value]
                    if c == c:
                        support_confidences.append(c)
            if len(support_confidences) == 0:
                mean_confidences.append(float("nan"))
                print(bin)
                print(support_value)
            else:
                mean_confidences.append(sum(support_confidences) / len(support_confidences))
        plt.plot(all_support_values, mean_confidences, label = interval_lable(bin /10), color = plt.cm.viridis(bin/10))
    plt.xlabel("support_value")
    plt.ylabel(mode)
    f = plt.gcf()
    f.set_figheight(10)
    f.set_figwidth(10)
    add_fancy_legend()
    plt.savefig(os.path.join(plots_dir, "mean_" + mode + ".png"))
    plt.clf()


def treewise(df, mode = "confidence"):
    subdir = os.path.join(plots_dir, mode)
    if not os.path.isdir(subdir):
        os.makedirs(subdir)
    datasets = list(set(df["dataset"]))
    res = []
    confidences = {}
    for dataset in datasets:
        sub_df = df[df["dataset"] == dataset]
        support_values = list(set(df[support_data]))
        support_values.sort()
        threshold = float("nan")
        confidence_dict = {}
        for support_value in support_values:
            below = sub_df[sub_df[support_data] <= support_value]
            above = sub_df[sub_df[support_data] > support_value]
            tn = len(below[below["inTrue"] == False])
            fn = len(below[below["inTrue"] == True])
            fp = len(above[above["inTrue"] == False])
            tp = len(above[above["inTrue"] == True])
            if mode == "confidence":
                if (fp + tn) == 0:
                    confidence = float("nan")
                else:
                    confidence = tn / (fp + tn)
            elif mode == "tp_relative":
                if fp + tp == 0:
                    confidence = float("nan")
                else:
                    confidence = tp / (fp + tp)
            else:
                print(mode, "not defined")
                retrun
            if confidence > 0.95 and threshold != threshold:
                threshold = support_value
            confidence_dict[support_value] = confidence
        if threshold != threshold:
            threshold = 100
        bin = int(sub_df["difficult"].mean() * 10)
        if not bin in confidences:
            confidences[bin] = []
        confidences[bin].append(confidence_dict)
        plt.plot(confidence_dict.keys(), confidence_dict.values())
        plt.axhline(y=0.95, color='grey', linestyle='--')
        plt.savefig(os.path.join(subdir, dataset + ".png"))
        plt.clf()
        res.append([dataset, sub_df["difficult"].mean(), threshold])
    plot_mean_confidences(confidences, mode)
    df = pd.DataFrame(res, columns = ["dataset", "difficult", "threshold"])
    return df

def plot_treewise(treewise_df, mode):
    plt.scatter(treewise_df["difficult"], treewise_df["threshold"], s = 10)
    plt.xlabel("difficult")
    plt.ylabel("threshold")
    plt.savefig(os.path.join(plots_dir, "treewise_" + mode + ".png"))
    plt.clf()

def get_sub_dfs(df):
    sub_dfs = {}
    lower = 0
    while lower < 1.0:
        sub_dfs[lower] = df.loc[lambda x: x.difficulty.between(lower, lower + step_size, inclusive="left")]
        lower += step_size
        lower = round(lower, 1)
    return sub_dfs

def load_data(data_type, support_data):
    data_dir = os.path.join("data", data_type)
    input_df = pd.read_csv(os.path.join(data_dir, support_data + ".csv"), index_col=0)
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "sizes.csv"), index_col=0), on = "dataset")
    #print(df.shape[0])
    #pythia_df = pd.read_parquet("input/pythia_2.0.0_training_data.parquet")[["verbose_name", "difficult"]]
    #pythia_df.verbose_name = pythia_df.verbose_name.str.strip(".phy")
    #df = pd.merge(df, pythia_df, left_on="dataset", right_on="verbose_name", how="inner")
    return input_df

def interval_lable(lower):
    return "[" + str(lower) + ", " + str(round(lower + step_size, 1)) + ")"

def add_fancy_legend():
    ax = plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 - box.height * 0.05, box.width, box.height * 0.95])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=5)


def get_window_dfs(sub_dfs):
    window_size = 10
    meta_dfs = {}
    for lower, df in sub_dfs.items():
        res = []
        support_value = window_size / 2
        while support_value <= 100 - window_size / 2:
            window = df[df[support_data] > support_value - window_size / 2]
            window = window[window[support_data] < support_value + window_size / 2]
            if len(window) == 0:
                in_true = 0
            else:
                in_true = len(window[window["inTrue"] == True]) / len(window)
            res.append([support_value, in_true])
            support_value += window_size
        meta_df = pd.DataFrame(res, columns = ["support_value", "fraction_in_tt"])
        meta_dfs[lower] = meta_df
    return meta_dfs


def get_meta_dfs(sub_dfs):
    meta_dfs = {}
    for lower, df in sub_dfs.items():
        support_values = list(set(df[support_data]))
        support_values.sort()
        res = []
        for support_value in support_values:
            equal = df[df[support_data] == support_value]
            num_correct = len(equal[equal["inTrue"] == True])
            num_incorrect = len(equal[equal["inTrue"] == False])
            ratio_correct = num_correct / (num_correct + num_incorrect)
            below = df[df[support_data] <= support_value]
            above = df[df[support_data] > support_value]
            tn = len(below[below["inTrue"] == False])
            fn = len(below[below["inTrue"] == True])
            fp = len(above[above["inTrue"] == False])
            tp = len(above[above["inTrue"] == True])
            if fp + tp == 0:
                tp_relative = float("nan")
            else:
                tp_relative = tp / (fp + tp)
            if fn + tn == 0:
                tn_relative = float("nan")
            else:
                tn_relative = tn / (fn + tn)
            if fp + tn == 0:
                alpha = float("nan")
            else:
                alpha = fp / (fp + tn)
            if fn + tp == 0:
                beta = float("nan")
            else:
                beta = fn / (fn + tp)
            confidence = 1 - alpha
            power = 1 - beta
            res.append([support_value, num_correct, num_incorrect, ratio_correct, tn, fn, fp, tp,
            tn_relative, tp_relative, alpha, beta, confidence, power])
        meta_df = pd.DataFrame(res, columns = ["support_value", "num_correct", "num_incorrect", "ratio_correct", "tn", "fn", "fp", "tp",
        "tn_relative", "tp_relative", "alpha", "beta", "confidence", "power"])
        meta_dfs[lower] = meta_df
    return meta_dfs

def auc_scores(sub_dfs):
    res = []
    for lower, df in sub_dfs.items():
        true = list(df["inTrue"])
        forecast = [v / 100.0 for v in list(df[support_data])]
        auc = roc_auc_score(true, forecast)
        res.append([interval_lable(lower), auc])
    tab = tabulate(res, headers = ["", "auc"], tablefmt = "pipe")
    print(tab)

def plot(meta_dfs, x, y, horz = float("nan")):
    row_count = 3
    col_count = 4
    fig, axes = plt.subplots(row_count, col_count, figsize=(5 * col_count, 5 * row_count))
    for ax in axes.flat:
        ax.set(xlabel=x, ylabel=y)
    for ax in axes.flat:
        ax.label_outer()
    row = 0
    col = 0
    for lower, meta_df in meta_dfs.items():
        ax = axes[row][col]
        col += 1
        if col == col_count:
            col = 0
            row += 1
        x_values = meta_df[x]
        y_values = meta_df[y]
        y_values = [y for _, y in sorted(zip(x_values, y_values))]
        x_values = x_values.sort_values()
        ax.plot(x_values, y_values)
        if horz == horz:
            plt.axhline(y=horz, color='grey', linestyle='--')
        ax.set_title(interval_lable(lower))
    plt.savefig(os.path.join(plots_dir, x + "_" + y + ".png"))
    plt.clf()


def plot_special(meta_dfs):
    row_count = 3
    col_count = 4
    fig, axes = plt.subplots(row_count, col_count, figsize=(5 * col_count, 5 * row_count))
    for ax in axes.flat:
        ax.set(xlabel="support_value", ylabel="cnt")
    for ax in axes.flat:
        ax.label_outer()
    row = 0
    col = 0
    for lower, meta_df in meta_dfs.items():
        meta_df["p"] = meta_df["fp"] + meta_df["tp"]
        ax = axes[row][col]
        col += 1
        if col == col_count:
            col = 0
            row += 1
        ax.plot(meta_df["support_value"], meta_df["p"], label = "p")
        ax.plot(meta_df["support_value"], meta_df["tp"], label = "tp")
        ax.set_title(interval_lable(lower))
    fig.legend(axes[0][0].get_legend_handles_labels()[1])
    plt.savefig(os.path.join(plots_dir, "special.png"))
    plt.clf()

def thresholds(sub_dfs, level_of_risk):
    meta_dfs = {}
    res = []
    for lower, df in sub_dfs.items():
        support_values = list(set(df[support_data]))
        support_values.sort()
        for support_value in support_values:
            below = df[df[support_data] <= support_value]
            above = df[df[support_data] > support_value]
            tn = len(below[below["inTrue"] == False])
            fn = len(below[below["inTrue"] == True])
            fp = len(above[above["inTrue"] == False])
            tp = len(above[above["inTrue"] == True])
            confidence = tn / (fp + tn)
            if confidence > 1 - level_of_risk:
                power = tp / (fn + tp)
                res.append([interval_lable(lower), support_value, power])
                break
    print("level of risk:", str(level_of_risk))
    tab = tabulate(res, headers = ["difficulty", "threshold", "power"], tablefmt = "pipe")
    print(tab)

def plot_sizes(input_df):
    plt.scatter(input_df["size"], input_df["difficulty"], s = 10)
    plt.xlabel("Tree size")
    plt.ylabel("Difficulty")
    plt.savefig(os.path.join(plots_dir, "sizes.png"))
    plt.clf()

def plot_counts(meta_dfs):
    row_count = 3
    col_count = 4
    fig, axes = plt.subplots(row_count, col_count, figsize=(5 * col_count, 3 * row_count))
    for ax in axes.flat:
        ax.set(xlabel="support_value", ylabel="num_branches")
    for ax in axes.flat:
        ax.label_outer()
    row = 0
    col = 0
    for lower, meta_df in meta_dfs.items():
        ax = axes[row][col]
        col += 1
        if col == col_count:
            col = 0
            row += 1
        ax.bar(meta_df["support_value"], meta_df["num_correct"], color='g', label ="correct")
        ax.bar(meta_df["support_value"], meta_df["num_incorrect"], bottom=meta_df["num_correct"], color='r', label="incorrect")
        ax.set_title("[" + str(lower) + ", " + str(round(lower + step_size, 1)) + ")")
    fig.legend(axes[0][0].get_legend_handles_labels()[1])
    plt.savefig(os.path.join(plots_dir, "counts.png"))
    plt.clf()

def plot_counts_boxplots(meta_dfs):
    counts = {}
    plt.figure(figsize=(20, 10))
    for lower, meta_df in meta_dfs.items():
        this_counts = []
        for i, row in meta_df.iterrows():
            this_counts += int(row["num_correct"] + row["num_incorrect"]) * [row["support_value"]]
        counts[interval_lable(lower)] = this_counts
    sns.violinplot(counts, palette = sns.color_palette("husl", len(counts)))
    plt.savefig(os.path.join(plots_dir, "counts_box.png"))
    plt.clf()


def plot_comb(meta_dfs, x, y, horz = float("nan"), diagonal = False):
    for lower, meta_df in meta_dfs.items():
        x_values = meta_df[x]
        y_values = meta_df[y]
        y_values = [y for _, y in sorted(zip(x_values, y_values))]
        x_values = x_values.sort_values()
        plt.plot(x_values, y_values, label = interval_lable(lower), color = plt.cm.viridis(lower))
    plt.xlabel(x)
    plt.ylabel(y)
    if horz == horz:
        plt.axhline(y=horz, color='grey', linestyle='--')
    if diagonal:
        plt.plot([5, 95], [0.05, 0.95], color='grey', linestyle='--')
    f = plt.gcf()
    f.set_figheight(10)
    f.set_figwidth(10)
    add_fancy_legend()
    plt.savefig(os.path.join(plots_dir, x + "_" + y + "_comb.png"))
    plt.clf()

def plot_avg_supports(dfs):
    row_count = 3
    col_count = 4
    fig, axes = plt.subplots(row_count, col_count, figsize=(5 * col_count, 3 * row_count))
    for ax in axes.flat:
        ax.set(xlabel="num_tips", ylabel="average_support")
    for ax in axes.flat:
        ax.label_outer()
    row = 0
    col = 0
    for lower, df in sub_dfs.items():
        sizes = list(set(df["size"]))
        min_size = min(sizes)
        max_size = max(sizes)
        step = (max_size - min_size) / 20
        s = min_size
        avg_supports = []
        labels = []
        while s <= max_size:
            sub_df = df[df["size"] > s]
            sub_df = sub_df[sub_df["size"] <= s + step]
            if len(sub_df) == 0:
                s += step
                continue
            avg_supports.append(sub_df[support_data].mean())
            labels.append(int(s + (step / 2)))
            s += step
        print(labels)
        print(avg_supports)
        ax = axes[row][col]
        col += 1
        if col == col_count:
            col = 0
            row += 1
        ax.plot(labels, avg_supports)
        ax.set_title("[" + str(lower) + ", " + str(round(lower + step_size, 1)) + ")")
    plt.savefig(os.path.join(plots_dir, "support_num_tips.png"))
    plt.clf()


step_size = 0.1

for data_type in ["sim", "treebase"]:
    #for support_data in ["sbs_Support", "sbs_Support_true", "sbs_Support_ml", "tbe_Support"]:
    for support_data in ["sbs_Support_true", "sbs_Support_ml"]:
        if data_type == "treebase" and support_data == "sbs_Support_true":
            continue
        plots_dir = os.path.join("data", data_type, "plots", support_data)
        if not os.path.isdir(plots_dir):
            os.makedirs(plots_dir)

        input_df = load_data(data_type, support_data)

        #determine statisics per tree and consider average
        #treewise_df = treewise(input_df, "confidence")
        #plot_treewise(treewise_df, "confidence")
        #treewise_df = treewise(input_df, "tp_relative")
        #plot_treewise(treewise_df, "tp_relative")

        #plot_sizes(input_df)

        sub_dfs =  get_sub_dfs(input_df)
        meta_dfs = get_meta_dfs(sub_dfs)

        plot_counts_boxplots(meta_dfs)
        if data_type == "treebase" or support_data == "sbs_Support_true":
            continue
        plot_counts(meta_dfs)

        thresholds(sub_dfs, 0.1)
        thresholds(sub_dfs, 0.05)
        auc_scores(sub_dfs)

        plot_comb(meta_dfs, "support_value", "tp_relative")
        plot_comb(meta_dfs, "support_value", "confidence", horz = 0.9)
        plot_comb(meta_dfs, "alpha", "power")

        window_dfs = get_window_dfs(sub_dfs)
        plot_comb(window_dfs, "support_value", "fraction_in_tt", float("nan"), True)
