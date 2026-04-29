from ete3 import Tree

def zero_threshold(avg_seq_len):
    return max(0.5 / avg_seq_len, 0.000001)

def collapse_branches(t, avg_seq_len):
    threshold = zero_threshold(avg_seq_len)
    for node in t.iter_descendants():
        if node.is_leaf():
            continue
        if node.dist <= threshold:
            node.delete()


