import os
import pandas as pd

import evaluation_util as util

import matplotlib.pyplot as plt


def combined_plots(branch_stats, support_data, group_by, remove_collapsed, plots_dir):
    if not os.path.isdir(plots_dir):
        os.makedirs(plots_dir)
    sim_df = load_data("sim", branch_stats)
    sim_df = util.remove_small_buckets(sim_df, support_data, group_by, remove_collapsed, auto = False, plot = False, threshold = 0.7, auto_threshold = 1000, plots_dir = plots_dir)
    emp_df = load_data("treebase", branch_stats)
    emp_df = util.remove_small_buckets(emp_df, support_data, group_by, remove_collapsed, auto = False, plot = False, threshold = 0.7, auto_threshold = 1000, plots_dir = plots_dir)
    sim_bucket_df = util.get_bucket_df(sim_df, support_data, group_by, truth_available = False, level_of_risk = 0.1, fixed_threshold = 0, remove_collapsed = remove_collapsed)
    emp_bucket_df = util.get_bucket_df(emp_df, support_data, group_by, truth_available = False, level_of_risk = 0.1, fixed_threshold = 0, remove_collapsed = remove_collapsed)
    for prop in ["zero_ratio", "mean_support"]:
        print("Combined plot for", prop)
        plt.figure(figsize=(20, 10))
        plt.scatter(sim_bucket_df[group_by], sim_bucket_df[prop], s = 10, color = util.c[""], label = "simulated")
        plt.plot(sim_bucket_df[group_by], sim_bucket_df[prop], color = util.c[""])
        plt.scatter(emp_bucket_df[group_by], emp_bucket_df[prop], s = 10, color = "grey", label = "empirical")
        plt.plot(emp_bucket_df[group_by], emp_bucket_df[prop], color = "grey")
        plt.xlabel(group_by)
        plt.ylabel(prop)
        util.add_fancy_legend()
        plt.savefig(os.path.join(plots_dir, prop + "_combined.png"))
        plt.close()

def load_data(data_type, branch_stats):
    print("loading data", data_type, branch_stats)
    data_dir = os.path.join("data", data_type)
    input_df = pd.read_csv(os.path.join(data_dir, branch_stats + "_branch_stats.csv"), index_col=0)
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    #input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels_collapsed.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_prediction.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "selection_stats.csv"), index_col=0), on = "dataset", how = "inner")
    if branch_stats == "best":
        assert len(input_df[(input_df["collapsed"] == False) & (input_df["zero"])]) == 0
    print(str(len(input_df)), "branches")
    print(str(len(list(set(input_df["dataset"])))), "datasets")
    return input_df

def filter_input(input_df):
    input_df = input_df[input_df["r_z"] < 0.5]
    input_df = input_df[input_df["max_brlen"] < 1]
    return input_df


level_of_risk = 0.1
level_of_risk2 = 0.05
remove_collapsed = True
branch_stats = "best"
group_by = "difficulty" #"difficulty_collapsed"
support_data = "sbs_Support"

combined_plots(branch_stats, support_data, group_by, remove_collapsed, os.path.join("data/plots", branch_stats, group_by))

data_type = "sim" #"treebase"

plots_dir = os.path.join("data", data_type, "plots", branch_stats, group_by)
if not os.path.isdir(plots_dir):
    os.makedirs(plots_dir)

input_df = load_data(data_type, branch_stats)
#input_df = util.remove_small_buckets(input_df, support_data, group_by, remove_collapsed, plots_dir, auto = False, plot = True, threshold = 0.5, auto_threshold = 1000)
#input_df = filter_input(input_df)

if data_type == "treebase":
    bucket_df = util.get_bucket_df(input_df, support_data, group_by, truth_available = False, remove_collapsed = remove_collapsed)
else:
    big_meta_df = util.get_meta_df(input_df, support_data, remove_collapsed)
    print("Determining general threshold")
    t = util.threshold(input_df, support_data, level_of_risk, remove_collapsed)
    print(t)
    t2 = util.threshold(input_df, support_data, level_of_risk2, remove_collapsed)
    print(t2)
    util.plot_confidence_all(big_meta_df, plots_dir, "", level_of_risk, t, level_of_risk2, t2)
    bucket_df = util.get_bucket_df(input_df, support_data, group_by, True, level_of_risk, t, remove_collapsed)

util.plot_prop("num_branches", bucket_df, group_by, plots_dir, suffix = "", param = 1000, vlines = True)
util.plot_prop("num_datasets", bucket_df, group_by, plots_dir, suffix = "", vlines = True)
util.plot_zero_ratio(bucket_df, group_by, plots_dir, truth_available = False, vlines = True)
util.plot_supports_fancy(bucket_df, group_by, plots_dir, "", vlines = True)

if data_type == "sim":
    util.plot_supports_fancy(bucket_df, group_by, plots_dir, "_correct", vlines = True)
    util.plot_supports_fancy(bucket_df, group_by, plots_dir, "_incorrect", vlines = True)
    util.plot_prop("auc", bucket_df, group_by, plots_dir, param = 0, vlines = True)
    util.plot_supports(bucket_df, group_by, plots_dir, vlines = True)
    util.plot_fixed_threshold(bucket_df, group_by, plots_dir)
    #util.plot_confusion(bucket_df, group_by, plots_dir)
    util.plot_ind_thresholds(bucket_df, group_by, plots_dir)
    util.auc_buckets(bucket_df, group_by)
