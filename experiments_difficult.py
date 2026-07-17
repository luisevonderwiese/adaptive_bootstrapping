import os
import pandas as pd

import evaluation_util as util


def load_data(data_type, branch_stats):
    print("loading data", data_type, branch_stats)
    data_dir = os.path.join("difficult_data", data_type)
    input_df = pd.read_csv(os.path.join(data_dir, branch_stats + "_branch_stats.csv"), index_col=0)
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "selection_stats.csv"), index_col=0), on = "dataset", how = "inner")
    if data_type == "alisim":
        input_df = input_df[input_df["dataset"].endswith("_d")]
    if data_type == "alisim2":
            data_dir = os.path.join("data", "sim")
            input_df2 = pd.read_csv(os.path.join(data_dir, branch_stats + "_branch_stats.csv"), index_col=0)
            input_df2 = input_df2.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
            input_df2 = input_df2.merge(pd.read_csv(os.path.join(data_dir, "selection_stats.csv"), index_col=0), on = "dataset", how = "inner")
    if data_type == "evonaps_difficult":
            data_dir = os.path.join("data", "treebase")
            input_df2 = pd.read_csv(os.path.join(data_dir, branch_stats + "_branch_stats.csv"), index_col=0)
            input_df2 = input_df2.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
            input_df2 = input_df2.merge(pd.read_csv(os.path.join(data_dir, "selection_stats.csv"), index_col=0), on = "dataset", how = "inner")
    #input_df = pd.concat([input_df, input_df2])
    assert len(input_df[(input_df["collapsed"] == False) & (input_df["zero"])]) == 0
    print(str(len(input_df)), "branches")
    print(str(len(list(set(input_df["dataset"])))), "datasets")
    return input_df



level_of_risk = 0.1
remove_collapsed = True
branch_stats = "best"
group_by = "difficulty" #"difficulty_collapsed"

support_data = "sbs_Support"

#combined_plots(branch_stats, support_data, group_by, remove_collapsed)

data_type = "alisim2"

plots_dir = os.path.join("difficult_data", data_type, "plots", branch_stats, group_by)
if not os.path.isdir(plots_dir):
    os.makedirs(plots_dir)

input_df = load_data(data_type, branch_stats)
#input_df = util.remove_small_buckets(input_df, support_data, group_by, remove_collapsed, plots_dir, auto = False, plot = True, threshold = 0.7, auto_threshold = 1000)

if data_type == "evonaps_difficult":
    bucket_df = util.get_bucket_df(input_df, support_data, group_by, truth_available = False, remove_collapsed = remove_collapsed)
else:
    big_meta_df = util.get_meta_df(input_df, support_data, remove_collapsed)
    print("Determining general threshold")
    t = util.threshold(input_df, support_data, level_of_risk, remove_collapsed)
    print(t)
    util.plot_confidence_all(big_meta_df, plots_dir, "", level_of_risk, t)
    bucket_df = util.get_bucket_df(input_df, support_data, group_by, True, level_of_risk, t, remove_collapsed)

util.plot_prop("num_branches", bucket_df, group_by, plots_dir, suffix = "", param = 1000)
util.plot_zero_ratio(bucket_df, group_by, plots_dir)
util.plot_supports_fancy(bucket_df, group_by, plots_dir, "")

if data_type == "alisim2":
    util.plot_supports_fancy(bucket_df, group_by, plots_dir, "_correct")
    util.plot_supports_fancy(bucket_df, group_by, plots_dir, "_incorrect")
    util.plot_prop("auc", bucket_df, group_by, plots_dir)
    util.plot_supports(bucket_df, group_by, plots_dir)
    util.plot_fixed_threshold(bucket_df, group_by, plots_dir)
    util.plot_confusion(bucket_df, group_by, plots_dir)
    util.plot_ind_thresholds(bucket_df, group_by, plots_dir)
    util.auc_buckets(bucket_df, group_by)
