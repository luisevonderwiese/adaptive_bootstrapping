import os
import pandas as pd
import numpy as np

import evaluation_util as util

def load_data(data_type):
    print("loading data", data_type)
    data_dir = os.path.join("data_reworked", data_type)
    input_df = pd.read_csv(os.path.join(data_dir, "branch_stats.csv"), index_col=0)
    input_df = input_df.merge(pd.read_csv(os.path.join(data_dir, "difficulty_labels.csv"), index_col=0), on = "dataset", how = "inner")
    input_df["collapsed"] = False
    assert len(input_df[(input_df["zero"] == False) & (input_df["zero"] == True)]) == 0
    print(str(len(input_df)), "branches")
    print(str(len(list(set(input_df["dataset"])))), "datasets")
    return input_df



level_of_risk = 0.1
group_by = "difficulty"
remove_collapsed = False

support_data = "sbs_Support"

#combined_plots(branch_stats, support_data, group_by)

data_type = "sim"

plots_dir = os.path.join("data_reworked", data_type, "plots", group_by)
if not os.path.isdir(plots_dir):
    os.makedirs(plots_dir)

input_df = load_data(data_type)
print("Mean supports")
print("all:", str(np.nanmean(input_df[support_data])))
df = input_df[input_df["zero"] == False]
print("non-zero:", str(np.nanmean(df[support_data])))
df = input_df[input_df["zero"] == True]
print("zero:", str(np.nanmean(df[support_data])))
df = input_df[input_df["exp_zero"] == True]
print("exp. zero:", str(np.nanmean(df[support_data])))


if data_type == "treebase":
    bucket_df = util.get_bucket_df(input_df, support_data, group_by, truth_available = False, remove_collapsed = remove_collapsed)
else:
    big_meta_df = util.get_meta_df(input_df, support_data, remove_collapsed)
    print("Determining general threshold")
    t = util.threshold(input_df, support_data, level_of_risk, remove_collapsed)
    print(t)
    util.plot_confidence_all(big_meta_df, plots_dir, "", level_of_risk, t)
    bucket_df = util.get_bucket_df(input_df, support_data, group_by, True, level_of_risk, t, remove_collapsed)

util.plot_zero_ratio(bucket_df, group_by, plots_dir)
util.plot_supports_fancy(bucket_df, group_by, plots_dir, "")
util.plot_prop("num_branches", bucket_df, group_by, plots_dir, suffix = "", param = 1000)

if data_type == "sim":
    util.plot_supports_fancy(bucket_df, group_by, plots_dir, "_correct")
    util.plot_supports_fancy(bucket_df, group_by, plots_dir, "_incorrect")
    util.plot_prop("auc", bucket_df, group_by, plots_dir)
    util.plot_supports(bucket_df, group_by, plots_dir)
    util.plot_fixed_threshold(bucket_df, group_by, plots_dir)
    util.plot_confusion(bucket_df, group_by, plots_dir)
    util.plot_ind_thresholds(bucket_df, group_by, plots_dir)
    util.auc_buckets(bucket_df, group_by)
