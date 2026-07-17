import os
import math
import numpy as np
import pandas as pd
from collections import Counter


import matplotlib.pyplot as plt
from cycler import cycler
from tabulate import tabulate

from sklearn.metrics import roc_auc_score
from scipy.stats import entropy
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

def threshold(df, support_data, level_of_risk, remove_collapsed):
    if remove_collapsed:
        df = df[df["collapsed"] == False]
    support_values = list(set(df[support_data]))
    support_values = [v for v in support_values if v == v]
    support_values.sort()
    for support_value in support_values:
        stats = get_stats(df, support_data, support_value)
        below = df[df[support_data] <= support_value]
        above = df[df[support_data] > support_value]
        tn = len(below[below["inTrue"] == False])
        fn = len(below[below["inTrue"] == True])
        fp = len(above[above["inTrue"] == False])
        tp = len(above[above["inTrue"] == True])
        if math.isnan(stats["confidence"]):
            continue
        if 1 - stats["confidence"] <= level_of_risk:
            return support_value

def get_stats(df, support_data, threshold):
    stats = {}
    stats["threshold"] = threshold
    all = len(df)
    df_collapsed = df[df["collapsed"] == True]
    if len(df_collapsed) != 0:
        print("using collapsed branches for stats")
    df = df[df["collapsed"] == False] #from here on, collapsed branches must be removed in any case, since they have no support values (nan)
    below = df[df[support_data] <= threshold]
    above = df[df[support_data] > threshold]
    tn = len(below[below["inTrue"] == False]) +  len(df_collapsed[df_collapsed["inTrue"] == False])
    fn = len(below[below["inTrue"] == True]) +  len(df_collapsed[df_collapsed["inTrue"] == True])
    fp = len(above[above["inTrue"] == False])
    tp = len(above[above["inTrue"] == True])
    if fp + tn == 0:
        stats["confidence"] = float("nan")
    else:
        stats["confidence"] = tn / (fp + tn)
    if fn + tp == 0:
        stats["power"] = float("nan")
    else:
        stats["power"] = tp / (fn + tp)
    if tp + fp == 0:
        stats["precision"] = float("nan")
    else:
        stats["precision"] = tp / (tp + fp)
    stats["tn_rel"] = tn / all
    stats["fn_rel"] = fn / all
    stats["fp_rel"] = fp / all
    stats["tp_rel"] = tp / all
    return stats


def get_support_stats(df, support_data):
    values = {}
    supports = df[support_data]
    if len(supports) == 0:
            values["mean_support"] = float("nan")
            values["q1_support"] = float("nan")
            values["q2_support"] = float("nan")
            values["q3_support"] = float("nan")
            values["min_support"] = float("nan")
            values["max_support"] = float("nan")
            return values
    values["mean_support"] = np.nanmean(supports)
    values["q1_support"] = np.quantile(supports, 0.25)
    values["q2_support"] = np.quantile(supports, 0.5)
    values["q3_support"] = np.quantile(supports, 0.75)
    values["min_support"] = min(supports)
    values["max_support"] = max(supports)
    return values


def bucket_size_analysis(df):
    datasets = list(set(df["dataset"]))
    tree_sizes = []
    collapsed_branch_ratios = []
    for dataset in datasets:
        sub_df = df[df["dataset"] == dataset]
        num_collapsed = len(sub_df[sub_df["collapsed"] == True])
        collapsed_branch_ratios.append(num_collapsed / len(sub_df))
        tree_sizes.append(len(sub_df[sub_df["collapsed"] == False]))
    return {
            "num_datasets": len(datasets), \
            "avg_num_branches" : sum(tree_sizes) / len(tree_sizes), \
            "collapsed_branch_ratio" :  sum(collapsed_branch_ratios) / len(collapsed_branch_ratios)\
            }


def bucket_threshold(bucket_df, group_by, threshold):
    print("Determine bucket threshold")
    for i, row in bucket_df.iterrows():
        if row["num_branches"] < threshold:
            return row[group_by]


def remove_small_buckets(input_df, support_data, group_by, remove_collapsed, plots_dir, auto = False, plot = False, threshold = 0.7, auto_threshold = 1000):
    bucket_df = get_bucket_df(input_df, support_data, group_by, truth_available = False, remove_collapsed = remove_collapsed)
    if plot:
        plot_prop("num_branches", bucket_df, group_by, plots_dir, suffix = "", param = auto_threshold)
    if auto:
        x = bucket_threshold(bucket_df, group_by, auto_threshold)
    else:
        x = threshold
    print("Filtering input data")
    #input_df = input_df[input_df[group_by] < x]
    input_df = input_df[input_df[group_by] > 0.6]
    print(str(len(input_df)), "branches remaining")
    return input_df


def get_meta_df(df, support_data, remove_collapsed):
    print("Generate big meta df")
    if remove_collapsed:
        df = df[df["collapsed"] == False]
    support_values = list(set(df[support_data]))
    support_values = [v for v in support_values if v == v]
    support_values.sort()
    res = []
    for support_value in support_values:
        res.append(get_stats(df, support_data, support_value))
    return pd.DataFrame(res)


def get_bucket_borders(group_by):
    if group_by in ["difficulty", "difficulty_predict", "difficulty_collapsed"]:
        borders = []
        step_size = 0.01
        radius = 0.01
        current_difficulty = radius
        while current_difficulty < 1:
            borders.append((current_difficulty - radius, current_difficulty + radius, current_difficulty))
            current_difficulty += step_size
        return borders
    if group_by == "size":
        borders = []
        factor = math.sqrt(2)
        lower = 4
        marker = 4 * factor
        upper = 4 * factor * factor
        while upper < 10000:
            borders.append((lower, upper, marker))
            lower = marker
            marker = upper
            upper *= factor
        return borders
    if group_by == "branch_length":
        borders = []
        factor = math.sqrt(math.sqrt(10))
        lower = 0.000001
        marker = lower * factor
        upper = lower * factor * factor
        while upper < 100:
            borders.append((lower, upper, marker))
            lower = marker
            marker = upper
            upper *= factor
        return borders
    raise ValueError(group_by + " not supported!")


def zero_ratios(df, truth_available):
    ratios = {}
    datasets = list(set(df["dataset"]))
    all = len(df)
    zero = len(df[df["zero"] == True])
    ratios["num_branches"] = all
    ratios["zero_ratio"] = zero / all
    if "exp_zero" in df.columns:
        exp_zero = len(df[df["exp_zero"] == True])
        ratios["exp_zero_ratio"] = exp_zero / all
    if not truth_available:
        return ratios
    correct_df = df[df["inTrue"] == True]
    all_true = len(correct_df)
    zero_true = len(correct_df[correct_df["zero"] == True])
    if all_true == 0:
        ratios["zero_ratio_correct"] = float("nan")
    else:
        ratios["zero_ratio_correct"] = zero_true / all_true
    if all_true == all:
        ratios["zero_ratio_incorrect"] = float("nan")
    else:
        ratios["zero_ratio_incorrect"] = (zero - zero_true) / (all - all_true)
    return ratios



def get_bucket_values(df, support_data, truth_available, level_of_risk, fixed_threshold, remove_collapsed):
    values = {}
    values.update(bucket_size_analysis(df))
    values.update(zero_ratios(df, truth_available))

    not_collapsed_df = df[df["collapsed"] == False]
    if remove_collapsed:
        df = not_collapsed_df #Remove collapsed branches for the rest of the analysis

    if truth_available:
        predicts = []
        for i, row in df.iterrows():
            if row[support_data] == row[support_data]:
                predicts.append(row[support_data] /  100.0)
            else:
                predicts.append(0.0)
        values["auc"] = roc_auc_score(list(df["inTrue"]), predicts)

        stats_fixed = get_stats(df, support_data, fixed_threshold)
        for name, value in stats_fixed.items():
            values[name + "_fixed"] = value
        ind_threshold = threshold(df, support_data, level_of_risk, remove_collapsed = False) #if necessary, collapsed already removed
        stats_ind = get_stats(df, support_data, ind_threshold)

        for name, value in stats_ind.items():
            values[name + "_ind"] = value

    #values["entropy"] = get_entropy(list(df[support_data]))

    df = not_collapsed_df #from here on, collapsed branches must be removed in any case, since they have no support values (nan)

    if not truth_available:
        values.update(get_support_stats(df, support_data))
        return values

    correct_df = df[df["inTrue"] == True]
    incorrect_df = df[df["inTrue"] == False]
    for (suffix, sub_df) in [("", df), ("_correct", correct_df), ("_incorrect", incorrect_df)]:
        support_stats = get_support_stats(sub_df, support_data)
        for name, value in support_stats.items():
            values[name + suffix] = value
    values["ratio_correct"] = len(correct_df) / len(df)



    return values




def get_bucket_df(input_df, support_data, group_by, truth_available, level_of_risk = 0.1, fixed_threshold = 0, remove_collapsed = True):
    print("Generating bucket df")
    borders = get_bucket_borders(group_by)
    bucket_values = []
    for (lower, upper, marker) in borders:
        df = input_df[input_df[group_by] >= lower]
        df = df[df[group_by] < upper]
        if len(df) == 0:
            continue
        current_values = get_bucket_values(df, support_data, truth_available, level_of_risk, fixed_threshold, remove_collapsed)
        current_values[group_by] = marker
        bucket_values.append(current_values)
    return pd.DataFrame(bucket_values)



def auc_buckets(bucket_df, group_by):
    print("analyzing auc scores")
    res = {}
    for i, row in bucket_df.iterrows():
        res[row[group_by]] = row["auc"]
    l = sorted(res, key=res.get)
    min_key = l[0]
    max_key = l[-1]
    print(str(min_key), str(res[min_key]))
    print(str(max_key), str(res[max_key]))
    #print(np.nanmean(res.values))


c = {"mean_support" : "dodgerblue",
    "" : "dodgerblue",
    "mean_support_correct" : "yellowgreen",
    "_correct" : "yellowgreen",
    "mean_support_incorrect": "firebrick",
    "_incorrect": "firebrick",
    "ratio_correct" : "grey",
    "threshold" : "grey",
    "confidence" : "navy",
    "power" : "cyan",
    "precision" : "goldenrod",
    "tn_rel_fixed": "cyan",
    "tp_rel_fixed": "gold",
    "fn_rel_fixed": "darkgoldenrod",
    "fp_rel_fixed": "navy",}




def add_fancy_legend():
    ax = plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 - box.height * 0.05, box.width, box.height * 0.95])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=5)






def plot_prop(prop, bucket_df, group_by, plots_dir, suffix = "", param = 0):
    print("Generating fancy plot for", prop)
    plt.figure(figsize=(20, 10))
    plt.scatter(bucket_df[group_by],bucket_df[prop], s = 10, label = prop)
    plt.plot(bucket_df[group_by],bucket_df[prop])
    plt.xlabel(group_by)
    if group_by in ["size", "branch_length"]:
        plt.xscale("log")
    if prop in ["auc"]:
        plt.gca().set_ylim(-0.05, 1.05)
    if prop == "num_branches":
        plt.axhline(param, color = "grey", linestyle = "--")
    plt.ylabel(prop)
    plt.savefig(os.path.join(plots_dir, prop + suffix + ".png"))
    plt.close()


def plot_confusion(bucket_df, group_by, plots_dir):
    print("Generating fancy plot for confusion")
    plt.figure(figsize=(20, 10))
    for prop in ["fn_rel_fixed", "tp_rel_fixed", "fp_rel_fixed", "tn_rel_fixed"]:
        plt.scatter(bucket_df[group_by],bucket_df[prop], s = 10, label = prop)
        plt.plot(bucket_df[group_by],bucket_df[prop])
    plt.xlabel(group_by)
    plt.gca().set_ylim(-0.05, 1.05)
    plt.ylabel("relative number")
    add_fancy_legend()
    plt.savefig(os.path.join(plots_dir, "confusion.png"))
    plt.close()

def plot_zero_ratio(bucket_df, group_by, plots_dir):
    print("Generating fancy plot for zero ratios")
    plt.figure(figsize=(20, 10))
    plt.scatter(bucket_df[group_by],bucket_df["zero_ratio"], s = 10, color = c[""], label = "zero_ratio")
    plt.plot(bucket_df[group_by],bucket_df["zero_ratio"], color = c[""])
    if "zero_ratio_correct" in bucket_df.columns:
        plt.scatter(bucket_df[group_by],bucket_df["zero_ratio_correct"], s = 10, color = c["_correct"], label = "zero_ratio_correct")
        plt.plot(bucket_df[group_by],bucket_df["zero_ratio_correct"], color = c["_correct"])
    if "zero_ratio_incorrect" in bucket_df.columns:
        plt.scatter(bucket_df[group_by],bucket_df["zero_ratio_incorrect"], s = 10, color = c["_incorrect"], label = "zero_ratio_incorrect")
        plt.plot(bucket_df[group_by],bucket_df["zero_ratio_incorrect"], color = c["_incorrect"])
    if "exp_zero_ratio" in bucket_df.columns:
        plt.scatter(bucket_df[group_by],bucket_df["exp_zero_ratio"], s = 10, color = "grey", label = "exp_zero_ratio")
        plt.plot(bucket_df[group_by],bucket_df["exp_zero_ratio"], color = "grey")
    plt.xlabel(group_by)
    if group_by in ["size", "branch_length"]:
        plt.xscale("log")
    plt.ylabel("ratio")
    plt.gca().set_ylim(-0.05, 1.05)
    add_fancy_legend()
    plt.savefig(os.path.join(plots_dir, "zero_ratio.png"))
    plt.close()


def plot_supports_fancy(bucket_df, group_by, plots_dir, suffix = ""):
    print("Generating fancy plot for support value distribution")
    #bucket_df = bucket_df[bucket_df["difficulty"] <= 0.25]
    plt.figure(figsize=(20, 10))
    plt.plot(bucket_df[group_by], bucket_df["max_support" + suffix], color = "grey", linestyle = "--")
    plt.plot(bucket_df[group_by], bucket_df["min_support" + suffix], color = "grey", linestyle = "--")
    plt.fill_between(bucket_df[group_by], bucket_df["q1_support" + suffix], bucket_df["q3_support" + suffix], color = c[suffix], alpha = 0.2)
    plt.plot(bucket_df[group_by], bucket_df["q2_support" + suffix], color = c[suffix])
    plt.plot(bucket_df[group_by], bucket_df["mean_support" + suffix], color = c[suffix], linestyle = "--")
    plt.gca().set_ylim(-5, 105)
    plt.xlabel(group_by)
    if group_by in ["size", "branch_length"]:
        plt.xscale("log")
    plt.savefig(os.path.join(plots_dir, "supports_fancy" + suffix + ".png"))
    plt.close()

def plot_supports(bucket_df, group_by, plots_dir):
    print("Generating plot for support value distribution")
    plt.figure(figsize=(20, 10))
    for prop in ["mean_support"]:#, "mean_support_correct", "mean_support_incorrect"]:
        plt.scatter(bucket_df[group_by], bucket_df[prop] / 100, s = 10, color = c[prop], label = prop)
        plt.plot(bucket_df[group_by], bucket_df[prop] / 100, color = c[prop])
    plt.scatter(bucket_df[group_by], bucket_df["ratio_correct"], s = 10, color = c["ratio_correct"], label = "ratio_correct")
    plt.plot(bucket_df[group_by], bucket_df["ratio_correct"], color = c["ratio_correct"])
    plt.gca().set_ylim(-0.05, 1.05)
    add_fancy_legend()
    plt.xlabel(group_by)
    if group_by in ["size", "branch_length"]:
        plt.xscale("log")
    plt.savefig(os.path.join(plots_dir, "supports.png"))
    plt.close()


def plot_ind_thresholds(bucket_df, group_by, plots_dir, suffix = ""):
    print("Generating plot for independent thresholds")
    plt.figure(figsize=(20, 10))
    plt.scatter(bucket_df[group_by], bucket_df["threshold_ind"] / 100, color = c["threshold"], s = 10, label = "threshold")
    plt.plot(bucket_df[group_by], bucket_df["threshold_ind"] / 100, color = c["threshold"])
    plt.scatter(bucket_df[group_by], bucket_df["power_ind"], s = 10, color = c["power"], label = "power")
    plt.plot(bucket_df[group_by], bucket_df["power_ind"], color = c["power"])
    plt.scatter(bucket_df[group_by], bucket_df["precision_ind"], s = 10, color = c["precision"], label = "precision")
    plt.plot(bucket_df[group_by], bucket_df["precision_ind"], color = c["precision"])
    plt.gca().set_ylim(-0.05, 1.05)
    add_fancy_legend()
    plt.xlabel(group_by)
    if group_by in ["size", "branch_length"]:
        plt.xscale("log")
    plt.savefig(os.path.join(plots_dir, "thresholds" + suffix + ".png"))
    plt.close()


def plot_fixed_threshold(bucket_df, group_by, plots_dir, suffix = ""):
    print("Generating plot for fixed threshold")
    plt.figure(figsize=(20, 10))
    plt.scatter(bucket_df[group_by], bucket_df["confidence_fixed"], s = 10, color = c["confidence"], label = "confidence")
    plt.plot(bucket_df[group_by], bucket_df["confidence_fixed"], color = c["confidence"])
    plt.scatter(bucket_df[group_by], bucket_df["power_fixed"], s = 10, color = c["power"], label = "power")
    plt.plot(bucket_df[group_by], bucket_df["power_fixed"], color = c["power"])
    plt.scatter(bucket_df[group_by], bucket_df["precision_fixed"], s = 10, color = c["precision"], label = "precision")
    plt.plot(bucket_df[group_by], bucket_df["precision_fixed"], color = c["precision"])
    plt.gca().set_ylim(-0.05, 1.05)
    add_fancy_legend()
    plt.xlabel(group_by)
    if group_by in ["size", "branch_length"]:
        plt.xscale("log")
    plt.savefig(os.path.join(plots_dir, "threshold_fixed" + suffix + ".png"))
    plt.close()





def plot_confidence_all(big_meta_df, plots_dir, suffix = "", level_of_risk = float("nan"), t = float("nan")):
    plt.figure(figsize=(20, 10))
    plt.plot(big_meta_df["threshold"], big_meta_df["confidence"])
    plt.xlabel("threshold")
    plt.ylabel("confidence")
    if t == t:
        plt.axvline(x = t, color ='grey', linestyle='--')
    if level_of_risk == level_of_risk:
        plt.axhline(y = 1 - level_of_risk, color ='grey', linestyle='--')
    plt.gca().set_ylim(-0.05, 1.05)
    plt.savefig(os.path.join(plots_dir, "confidence" + suffix + ".png"))
    plt.clf()
    plt.close()



def combined_plots(branch_stats, support_data, group_by, remove_collapsed, plots_dir):
    plots_dir = os.path.join("data", "plots", branch_stats, group_by)
    if not os.path.isdir(plots_dir):
        os.makedirs(plots_dir)
    sim_df = load_data("sim", branch_stats)
    sim_df = remove_small_buckets(sim_df, support_data, group_by, remove_collapsed, auto = False, plot = False, threshold = 0.7, auto_threshold = 1000)
    emp_df = load_data("treebase", branch_stats)
    emp_df = remove_small_buckets(emp_df, support_data, group_by, remove_collapsed, auto = False, plot = False, threshold = 0.7, auto_threshold = 1000)
    sim_bucket_df = get_bucket_df(sim_df, support_data, group_by, truth_available = False, level_of_risk = 0.1, fixed_threshold = 0, remove_collapsed = remove_collapsed)
    emp_bucket_df = get_bucket_df(emp_df, support_data, group_by, truth_available = False, level_of_risk = 0.1, fixed_threshold = 0, remove_collapsed = remove_collapsed)
    for prop in ["zero_ratio", "mean_support"]:
        print("Combined plot for", prop)
        plt.figure(figsize=(20, 10))
        plt.scatter(sim_bucket_df[group_by], sim_bucket_df[prop], s = 10, color = c[""], label = "simulated")
        plt.plot(sim_bucket_df[group_by], sim_bucket_df[prop], color = c[""])
        plt.scatter(emp_bucket_df[group_by], emp_bucket_df[prop], s = 10, color = "grey", label = "empirical")
        plt.plot(emp_bucket_df[group_by], emp_bucket_df[prop], color = "grey")
        plt.xlabel(group_by)
        plt.ylabel(prop)
        add_fancy_legend()
        plt.savefig(os.path.join(plots_dir, prop + "_combined.png"))
        plt.close()
