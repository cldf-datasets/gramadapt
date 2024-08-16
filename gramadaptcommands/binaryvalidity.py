"""
143 binary questions
"""
import itertools
import collections

from cldfbench_gramadapt import Dataset
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
from seaborn import clustermap
from clldutils.color import qualitative_colors


def run(args):
    with (Dataset().plot_data(__file__) as cldf):
        data = collections.defaultdict(dict)
        ndata = collections.defaultdict(set)

        pids = set()
        for v in cldf.objects('ValueTable'):
            if v.parameter.data['datatype'] == 'Binary-YesNo':
                pids.add(v.cldf.parameterReference)
                data[v.cldf.contributionReference][v.cldf.parameterReference] = \
                    -1 if v.code and v.code.cldf.name == 'No' \
                        else (1 if v.code and v.code.cldf.name == 'Yes' else 0)
                ndata[v.cldf.parameterReference].add((
                    v.cldf.contributionReference,
                    v.code.cldf.name if v.code else None))
        for pid1, pid2 in itertools.combinations(ndata.keys(), 2):
            if ndata[pid1] == ndata[pid2]:
                pass
                #print(pid1, pid2)
                #print(ndata[pid1])
                #print(ndata[pid2])
        #return

        pids = sorted(pids)
        sets = sorted(data.keys())
        domains = {pid: pid[:3] for pid in pids}
        domains = {k: 'OV' if v.startswith('O') else v for k, v in domains.items()}
        cl = collections.OrderedDict(zip(
            sorted(set(domains.values())),
            qualitative_colors(len(set(domains.values())), set='tol')))

        g = clustermap(
            np.array([[data[s].get(pid, 0) for s in sets] for pid in pids]),
            yticklabels=True,
            cmap='coolwarm',
            col_cluster=False,
            figsize=(12, 22),
            row_colors=[cl[domains[pid]] for pid in pids],
            )

        reordered_labels = [pids[ni] for ni in g.dendrogram_row.reordered_ind]
        g.ax_heatmap.set(
            yticks=[i + 0.5 for i, _ in enumerate(reordered_labels)],
            yticklabels=reordered_labels)

        handles = [Patch(facecolor=cl[d]) for d in cl]
        plt.legend(
            handles,
            cl,
            title='Domains',
            bbox_to_anchor=(1, 1),
            bbox_transform=plt.gcf().transFigure,
            loc='upper right')
        plt.tight_layout()
