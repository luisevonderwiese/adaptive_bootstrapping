import os
from ete3 import Tree

def get_bipartition(node, all_leaves):
    leaves = set([leaf.name for leaf in node.iter_leaves()])
    others = all_leaves.difference(leaves)
    return (leaves, others)

def bipartition_in_tree(bip, tree_other, all_leaves_other):
    for node_other in tree_other.iter_descendants():
        if node_other.is_leaf():
            continue
        bip_other = get_bipartition(node_other, all_leaves_other)
        if ((bip[0] == bip_other[0]) and (bip[1] == bip_other[1])) or \
            ((bip[0] == bip_other[1]) and (bip[1] == bip_other[0])):
            return True
    return False


for ds in os.listdir("simtree_supports"):
    try:
        tree_a = Tree(os.path.join("simtree_supports", ds, "support_a.raxml.support"))
        tree_b = Tree(os.path.join("simtree_supports", ds, "support_b.raxml.support"))
    except:
        continue
    print(ds)
    all_leaves_a = set([l.name for l in tree_a.iter_leaves()])
    all_leaves_b = set([l.name for l in tree_b.iter_leaves()])

    common_supports = []
    distinct_supports_a = []
    for node_a in tree_a.traverse():
        try:
            node_a.support
        except AttributeError:
            continue
        bip_a = get_bipartition(node_a, all_leaves_a)
        if bipartition_in_tree(bip_a, tree_b, all_leaves_b):
            common_supports.append(node_a.support)
        else:
            distinct_supports_a.append(node_a.support)
    distinct_supports_b = []
    for node_b in tree_b.traverse():
        try:
            node_b.support
        except AttributeError:
            continue
        bip_b = get_bipartition(node_b, all_leaves_b)
        if bipartition_in_tree(bip_b, tree_a, all_leaves_a):
            continue #already consindered in tree a
        distinct_supports_b.append(node_b.support)
    try:
        avg_common = sum(common_supports) / len(common_supports)
    except:
        avg_common = float("nan")
    try:
        avg_a = sum(distinct_supports_a) / len(distinct_supports_a)
    except:
        avg_a = float("nan")
    try:
        avg_b = sum(distinct_supports_b) / len(distinct_supports_b)
    except:
        avg_b = float("nan")
    print(ds, str(avg_common), str(avg_a), str(avg_b))

