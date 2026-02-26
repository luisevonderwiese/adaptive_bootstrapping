import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from collections import Counter
from sklearn.metrics import roc_auc_score
from scipy.stats import wasserstein_distance
from scipy.stats import energy_distance, entropy
import seaborn as sns

def get_entropy(support_values):
    count = Counter(list(support_values))
    pk = []
    for i in range(101):
        if not i in count:
            pk.append(0)
        else:
            pk.append(count[i] / len(support_values))
    return entropy(pk, base = 101)


def treewise(sub_dfs, group_by):
    treewise_dfs = {}
    x_values = []
    entropies = []
    high_ratios = []
    low_ratios = []

    for r, df in sub_dfs.items():
        res = []
        datasets = list(set(df["dataset"]))
        print(r)
        print(len(datasets))
        for dataset in datasets:
            sub_df = df[df["dataset"] == dataset]
            x_values.append(list(sub_df[group_by])[0])
            support_values = sub_df[support_data]
            e = get_entropy(support_values)
            entropies.append(e)
            high_ratio = len([s for s in support_values if s > 95]) / len(support_values)
            high_ratios.append(high_ratio)
            low_ratio = len([s for s in support_values if s < 5]) / len(support_values)
            low_ratios.append(low_ratio)
            res.append([dataset, np.mean(support_values), e, high_ratio, low_ratio])

        treewise_dfs[r] = pd.DataFrame(res, columns = ["dataset", "mean_support", "entropy", "high_ratio", "low_ratio"])

    plt.figure(figsize=(20, 10))
    plt.scatter(x_values, entropies, s = 10)
    if group_by in ["size", "patterns_over_taxa"]:
        plt.xscale("log")
    plt.xlabel(group_by)
    plt.ylabel("entropy")
    plt.savefig(os.path.join(plots_dir, "entropy.png"))
    plt.clf()

    plt.figure(figsize=(20, 10))
    plt.scatter(x_values, high_ratios, s = 10)
    if group_by in ["size", "patterns_over_taxa"]:
        plt.xscale("log")
    plt.xlabel(group_by)
    plt.ylabel("high ratio")
    plt.savefig(os.path.join(plots_dir, "high_ratio.png"))
    plt.clf()

    plt.figure(figsize=(20, 10))
    plt.scatter(x_values, low_ratios, s = 10)
    if group_by in ["size", "patterns_over_taxa"]:
        plt.xscale("log")
    plt.xlabel(group_by)
    plt.ylabel("low ratio")
    plt.savefig(os.path.join(plots_dir, "low_ratio.png"))
    plt.clf()

    for prop in ["mean_support", "entropy"]:#, "high_ratio", "low_ratio"]:
        plt.figure(figsize=(20, 10))
        counts =  {}
        for r, sub_df in treewise_dfs.items():
            counts[interval_lable(r)] = sub_df[prop]
        sns.boxplot(counts, palette = sns.color_palette("husl", len(counts)))
        plt.ylabel('average tree support')
        plt.savefig(os.path.join(plots_dir, "treewise_" + prop + "_box.png"))
        plt.clf()


def get_sub_dfs(df, group_by):
    if group_by == "difficulty":
        sub_dfs = {}
        lower = 0
        while lower < 1.0:
            upper = round(lower + 0.1, 1)
            sub_dfs[(lower, upper)] = df.loc[lambda x: x.difficulty.between(lower, upper, inclusive="left")]
            lower = upper
        return sub_dfs
    elif group_by == "difficulty_prediction":
        sub_dfs = {}
        lower = 0
        while lower < 1.0:
            upper = round(lower + 0.1, 1)
            sub_dfs[(lower, upper)] = df.loc[lambda x: x.difficulty_prediction.between(lower, upper, inclusive="left")]
            lower = upper
        return sub_dfs
    elif group_by == "patterns_over_taxa":
        ranges = [(0.0000001, 1), (1, 1.5), (1.5, 2), (2, 3), (3, 4), (4, 5), (5, 8), (8, 10), (10, 20), (20, 30), (30, 100), (100, 10000)]
        sub_dfs = {}
        for (lower, upper) in ranges:
            sub_dfs[(lower, upper)] = df.loc[lambda x: x.patterns_over_taxa.between(lower, upper, inclusive="left")]
        return sub_dfs
    elif group_by == "size":
        ranges = [(4, 15), (15, 30), (30, 40), (40, 50), (50, 75), (75, 100), (100, 1000000000)]
        sub_dfs = {}
        for (lower, upper) in ranges:
            sub_dfs[(lower, upper)] = df.loc[(df["size"] >= lower) & (df["size"] < upper)]
        return sub_dfs
    else:
        raise ValueError(group_by , "is not a grouping property")


def load_data(data_type, support_data):
    data_dir = os.path.join("data", data_type)
    input_df = pd.read_csv(os.path.join(data_dir, support_data + ".csv"), index_col=0)
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_prediction.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "patterns_over_taxa.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "sizes.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df[input_df["branch_length"] > 0.000001]
    return input_df

def interval_lable(r):
    return "[" + str(r[0]) + ", " + str(r[1]) + ")"

def add_fancy_legend():
    ax = plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 - box.height * 0.05, box.width, box.height * 0.95])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=5)


def get_window_dfs(sub_dfs):
    window_size = 5
    meta_dfs = {}
    for r, df in sub_dfs.items():
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
        meta_dfs[r] = meta_df
    return meta_dfs


def get_meta_df(df):
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
        e = entropy([len(below) / (len(above) + len(below)), len(above) / (len(above) + len(below))], base = 2)
        res.append([support_value, num_correct, num_incorrect, ratio_correct, tn, fn, fp, tp,
        tn_relative, tp_relative, 1 - tp_relative, alpha, beta, confidence, power, e])
    return pd.DataFrame(res, columns = ["support_value", "num_correct", "num_incorrect", "ratio_correct", "tn", "fn", "fp", "tp",
        "tn_relative", "tp_relative", "fp_relative", "alpha", "beta", "confidence", "power", "entropy"])


def get_meta_dfs(sub_dfs, support_data):
    meta_dfs = {}
    for r, df in sub_dfs.items():
        meta_dfs[r] = get_meta_df(df)
    return meta_dfs

def auc_scores(sub_dfs):
    res = []
    for r, df in sub_dfs.items():
        true = list(df["inTrue"])
        forecast = [v / 100.0 for v in list(df[support_data])]
        if len(forecast) == 0:
            continue
        auc = roc_auc_score(true, forecast)
        res.append([interval_lable(r), auc])
    tab = tabulate(res, headers = ["", "auc"], tablefmt = "pipe")
    print(tab)

def thresholds(sub_dfs, level_of_risk):
    res = []
    t = float("nan")
    for r, df in sub_dfs.items():
        support_values = list(set(df[support_data]))
        support_values.sort()
        for support_value in support_values:
            below = df[df[support_data] <= support_value]
            above = df[df[support_data] > support_value]
            tn = len(below[below["inTrue"] == False])
            fn = len(below[below["inTrue"] == True])
            fp = len(above[above["inTrue"] == False])
            tp = len(above[above["inTrue"] == True])
            alpha = fp / (fp + tn)
            if alpha <= level_of_risk:
                beta = fn / (fn + tp)
                if tp + fp == 0:
                    tp_relative = float("nan")
                else:
                    tp_relative = tp / (tp + fp)
                res.append([interval_lable(r), support_value, alpha, beta, tp_relative])
                if t!= t:
                    t = support_value
                break
    print("level of risk:", str(level_of_risk))
    tab = tabulate(res, headers = ["difficulty", "threshold", "alpha", "beta", "tp_relative"], tablefmt = "pipe")
    print(tab)
    return t

def fixed_thresholds(sub_dfs, threshold):
    res = []
    for r, df in sub_dfs.items():
        below = df[df[support_data] <= threshold]
        above = df[df[support_data] > threshold]
        tn = len(below[below["inTrue"] == False])
        fn = len(below[below["inTrue"] == True])
        fp = len(above[above["inTrue"] == False])
        tp = len(above[above["inTrue"] == True])
        alpha = fp / (fp + tn)
        beta = fn / (fn + tp)
        res.append([interval_lable(r), alpha, beta])
    print("threshold:", str(threshold))
    tab = tabulate(res, headers = ["difficulty", "alpha", "beta"], tablefmt = "pipe")
    print(tab)

def plot_sizes(input_df):
    plt.figure(figsize=(20, 10))
    plt.scatter(input_df["size"], input_df["difficulty"], s = 10)
    plt.xlabel("Tree size")
    plt.ylabel("Difficulty")
    plt.xscale("log")
    plt.savefig(os.path.join(plots_dir, "sizes.png"))
    plt.clf()
    plt.close()

    big_meta_df = get_meta_df(input_df)

    plt.figure(figsize=(20, 10))
    plt.scatter(big_meta_df["support_value"], big_meta_df["confidence"], s = 10)
    plt.plot(big_meta_df["support_value"], big_meta_df["confidence"])
    plt.xlabel("support_value")
    plt.ylabel("confidence")
    plt.axvline(x = 70, color ='grey')
    plt.axhline(y = 0.9, color ='grey')
    plt.savefig(os.path.join(plots_dir, "confidence.png"))
    plt.clf()
    plt.close()

    plt.figure(figsize=(20, 10))
    plt.scatter(big_meta_df["alpha"], big_meta_df["power"], s = 10)
    plt.plot(big_meta_df["alpha"], big_meta_df["power"])
    plt.axvline(x = 0.1, color ='grey')
    plt.xlabel("alpha")
    plt.ylabel("power")
    plt.savefig(os.path.join(plots_dir, "roc.png"))
    plt.clf()
    plt.close()



def plot_counts(meta_dfs):
    for i, (r, meta_df) in enumerate(meta_dfs.items()):
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        ax = axes[0]
        ax.bar(meta_df["support_value"], meta_df["num_correct"], color='g', label ="correct", log = True)
        ax.set_xlabel('support value')
        ax.set_ylabel('#branches')
        ax = axes[1]
        ax.bar(meta_df["support_value"], meta_df["num_incorrect"], color='r', label="incorrect", log = True)
        ax.set_xlabel('support value')
        ax.set_ylim(0, 100000)
        fig.legend()
        plt.savefig(os.path.join(plots_dir, "counts_" + str(i) + ".png"))
        plt.clf()
        plt.close()

def plot_counts_boxplots(sub_dfs, support_data):
    counts = {}
    plt.figure(figsize=(20, 10))
    for r, sub_df in sub_dfs.items():
        counts[interval_lable(r)] = sub_df[support_data]
    sns.boxplot(counts, palette = sns.color_palette("husl", len(counts)))
    plt.ylabel('support value')
    plt.savefig(os.path.join(plots_dir, "counts_box.png"))
    plt.clf()


def plot_comb(meta_dfs, x, y, horz = float("nan"), diagonal = False):
    for i, (r, meta_df) in enumerate(meta_dfs.items()):
        x_values = meta_df[x]
        y_values = meta_df[y]
        y_values = [y for _, y in sorted(zip(x_values, y_values))]
        x_values = x_values.sort_values()
        plt.scatter(x_values, y_values, s = 10, color = plt.cm.viridis(i / (len(meta_dfs) - 1)))
        plt.plot(x_values, y_values, label = interval_lable(r), color = plt.cm.viridis(i / (len(meta_dfs) - 1)))
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

def emd(data_type1, support_data1, data_type2, support_data2):
    print(data_type1, support_data1, "vs", data_type2, support_data2)
    input_df1 = load_data(data_type1, support_data1)
    input_df2 = load_data(data_type2, support_data2)
    sub_dfs1 =  get_sub_dfs(input_df1)
    sub_dfs2 =  get_sub_dfs(input_df2)
    res = []
    for r, sub_df1 in sub_dfs1.items():
        sub_df2 = sub_dfs2[lower]
        emd = wasserstein_distance(sub_df1[support_data1], sub_df2[support_data2])
        ed = energy_distance(sub_df1[support_data1], sub_df2[support_data2])
        res.append([interval_lable(r), emd, ed])
    tab = tabulate(res, headers = ["difficulty", "emd", "energy distance"], tablefmt = "pipe")
    print(tab)




#emd("sim", "sbs_Support", "sim", "sbs_Support_true")
#emd("sim", "sbs_Support", "sim", "sbs_Support_ml")
#emd("treebase", "sbs_Support", "treebase", "sbs_Support_ml")


for data_type in ["sim", "treebase"]: #"treebase", "sim_difficult"]:
    for support_data in ["sbs_Support"]:#, "sbs_Support_ml", "tbe_Support", "ebg_Support", "ufboot"]: #["sbs_Support", "sbs_Support_true", "sbs_Support_ml",
        if data_type == "treebase" and support_data == "sbs_Support_true":
            continue
        plots_dir = os.path.join("data", data_type, "plots", support_data)
        if not os.path.isdir(plots_dir):
            os.makedirs(plots_dir)
        input_df = load_data(data_type, support_data)
        #plot_sizes(input_df)

        print(data_type, support_data)
        for group_by in ["difficulty"]: #, "size", "difficulty_prediction", "patterns_over_taxa"]:
            plots_dir = os.path.join("data", data_type, "plots", support_data, group_by)
            if not os.path.isdir(plots_dir):
                os.makedirs(plots_dir)

            sub_dfs =  get_sub_dfs(input_df, group_by)
            #treewise(sub_dfs, group_by)
            #plot_counts_boxplots(sub_dfs, support_data)

            if data_type == "treebase" or support_data == "sbs_Support_true":
                continue
            t = thresholds({(0.0, 1.0) : input_df}, 0.05)
            fixed_thresholds(sub_dfs, t)
            thresholds(sub_dfs, 0.05)
            #thresholds(sub_dfs, 0.1)
            #thresholds(sub_dfs, 0.05)
            auc_scores(sub_dfs)

            meta_dfs = get_meta_dfs(sub_dfs, support_data)
            plot_counts(meta_dfs)

            plot_comb(meta_dfs, "support_value", "tp_relative")
            plot_comb(meta_dfs, "support_value", "confidence", horz = 0.9)
            plot_comb(meta_dfs, "support_value", "power")
            plot_comb(meta_dfs, "alpha", "power")

            window_dfs = get_window_dfs(sub_dfs)
            plot_comb(window_dfs, "support_value", "fraction_in_tt", float("nan"), True)
