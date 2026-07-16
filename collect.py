import os
import pandas as pd


def collect_difficulties(label_dir, out_path, collapsed = False):
    res = []
    for ds in os.listdir(label_dir):
        if collapsed:
            res_file = os.path.join(label_dir, ds, "difficulty_label_collapsed.csv")
        else:
            res_file = os.path.join(label_dir, ds, "difficulty_label.csv")
        if not os.path.isfile(res_file):
            print(ds, "label missing")
            continue
        difficult = pd.read_csv(res_file)["difficulty"].iloc[0]
        res.append([ds, difficult])
    if collapsed:
        df = pd.DataFrame(res, columns = ["dataset", "difficulty_collapsed"])
    else:
        df = pd.DataFrame(res, columns = ["dataset", "difficulty"])
    df.to_csv(out_path)

def collect_difficulties_old(label_dir, out_path):
    res = []
    for ds in os.listdir(label_dir):
        res_file = os.path.join(label_dir, ds, "labelGen.csv")
        if not os.path.isfile(res_file):
            print(ds, "label missing")
            continue
        difficult = pd.read_csv(res_file)["difficulty"].iloc[0]
        res.append([ds, difficult])
    df = pd.DataFrame(res, columns = ["dataset", "difficulty"])
    df.to_csv(out_path)


def collect_stats(super_dir, out_path):
    big_df = pd.DataFrame()
    cnt = 0
    for ds in os.listdir(super_dir):
        print(ds)
        ds_name = ds.split(".")[0]
        res_file = os.path.join(super_dir, ds)
        if not os.path.isfile(res_file):
            print(ds_name, "stats missing")
            continue
        ds_df = pd.read_csv(res_file)
        ds_df["dataset"] = pd.Series([ds_name for x in range(len(ds_df.index))])
        big_df = pd.concat([big_df, ds_df], axis=0)
        cnt += 1
    print(cnt)
    big_df.to_csv(out_path)

base_dir = "data_new"
cats = ["sim"]


for cat in cats:
    label_dir = os.path.join(base_dir, cat, "difficulty_labels")
    out_path = os.path.join(base_dir, cat, "difficulty_labels.csv")
    #collect_difficulties(label_dir, out_path)
    
    out_path = os.path.join(base_dir, cat, "difficulty_labels_collapsed.csv")
    #collect_difficulties(label_dir, out_path, collapsed = True)
    
    stats_dir = os.path.join(base_dir, cat, "selection_stats")
    out_path = os.path.join(base_dir, cat, "selection_stats.csv")
    #collect_stats(stats_dir, out_path)

    stats_dir = os.path.join(base_dir, cat, "best_tt_collapsed_branch_stats")
    out_path = os.path.join(base_dir, cat, "best_tt_collapsed_branch_stats.csv")
    #collect_stats(stats_dir, out_path)

    
    stats_dir = os.path.join(base_dir, cat, "best_branch_stats")
    out_path = os.path.join(base_dir, cat, "best_branch_stats.csv")
    #collect_stats(stats_dir, out_path)
    
    stats_dir = os.path.join(base_dir, cat, "consensus_branch_stats")
    out_path = os.path.join(base_dir, cat, "consensus_branch_stats.csv")
    #collect_stats(stats_dir, out_path)

    stats_dir = os.path.join(base_dir, cat, "shalrt_branch_stats")
    out_path = os.path.join(base_dir, cat, "shalrt_branch_stats.csv")
    #collect_stats(stats_dir, out_path)



base_dir = "data_reworked"
cats = ["sim", "treebase"]

for cat in cats:
    stats_dir = os.path.join(base_dir, cat, "branch_stats")
    out_path = os.path.join(base_dir, cat, "branch_stats.csv")
    #collect_stats(stats_dir, out_path)

    if cat != "treebase":
        label_dir = os.path.join(base_dir, cat, "difficulty_labels")
        out_path = os.path.join(base_dir, cat, "difficulty_labels.csv")
        #collect_difficulties_old(label_dir, out_path)


base_dir = "difficult_data"
cats = ["evonaps_difficult", "alisim2"]


for cat in cats:
    label_dir = os.path.join(base_dir, cat, "difficulty_labels")
    out_path = os.path.join(base_dir, cat, "difficulty_labels.csv")
    collect_difficulties(label_dir, out_path)

    out_path = os.path.join(base_dir, cat, "difficulty_labels_collapsed.csv")
    collect_difficulties(label_dir, out_path, collapsed = True)

    stats_dir = os.path.join(base_dir, cat, "selection_stats")
    out_path = os.path.join(base_dir, cat, "selection_stats.csv")
    collect_stats(stats_dir, out_path)

    stats_dir = os.path.join(base_dir, cat, "best_tt_collapsed_branch_stats")
    out_path = os.path.join(base_dir, cat, "best_tt_collapsed_branch_stats.csv")
    #collect_stats(stats_dir, out_path)


    stats_dir = os.path.join(base_dir, cat, "best_branch_stats")
    out_path = os.path.join(base_dir, cat, "best_branch_stats.csv")
    collect_stats(stats_dir, out_path)

    stats_dir = os.path.join(base_dir, cat, "consensus_branch_stats")
    out_path = os.path.join(base_dir, cat, "consensus_branch_stats.csv")
    #collect_stats(stats_dir, out_path)

    stats_dir = os.path.join(base_dir, cat, "shalrt_branch_stats")
    out_path = os.path.join(base_dir, cat, "shalrt_branch_stats.csv")
    #collect_stats(stats_dir, out_path)


