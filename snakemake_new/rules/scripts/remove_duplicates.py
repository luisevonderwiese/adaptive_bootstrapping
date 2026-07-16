import os
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.AlignIO.PhylipIO import RelaxedPhylipWriter
import sys

#with open("foo.out", "w+") as f:
#    sys.stdout = f
#print("0")
msa_path = snakemake.params.msa
outpath = snakemake.output.msa_nodup
ending = msa_path.split(".")[-1]
if ending == "fasta" or ending == "fa":
    f = "fasta"
elif ending == "phy" or ending == "phylip":
    f = "phylip-relaxed"
else:
    print(ending, "not supported")
align = AlignIO.read(msa_path, f)
seq_map = {}
for rec in align:
    s = rec.seq
    allowed_set = set(['A', 'C', 'G', 'T'])
    l = len(''.join([c for c in s if c in allowed_set]))
    if l == 0: #only gaps
        continue
    if not s in seq_map:
        seq_map[s] = []
    seq_map[s].append(rec)
remaining_records = [l[0] for _,l in seq_map.items()]
align = MultipleSeqAlignment(remaining_records, annotations={}, column_annotations={})
with open(outpath, "w+") as f:
    writer = RelaxedPhylipWriter(f)
    writer.write_alignment(align)
