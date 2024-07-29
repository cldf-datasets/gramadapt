"""
38 categorical questions asked about a language, with the same set of possible answers.
"""
import collections

from cldfbench_gramadapt import Dataset
import matplotlib.pyplot as plt
from clldutils.color import qualitative_colors

DOMAIN = [
    'The Focus Group language',
    'The Neighbour Group language',
    'Some other language',
    'This is highly contextual',
    'B']


def run(args):
    with Dataset().plot_data(__file__) as cldf:
        data = collections.defaultdict(list)
        domains = collections.defaultdict(list)
        for v in cldf.objects('CodeTable'):
            if v.parameter.data['datatype'] == 'Types':
                domains[v.parameter.id].append(v.cldf.name)
        pids = {pid for pid, domain in domains.items() if set(domain) == set(DOMAIN)}
        for v in cldf.objects('ValueTable'):
            if v.parameter.id in pids:
                data[v.parameter.id].append(v.code.cldf.name if v.code else None)

        ml = max(len(v) for v in data.values())
        for v in data.values():
            while len(v) <= ml:
                v.append(None)

        data = sorted(data.items(), key=lambda i: i[0])
        cats = DOMAIN
        colors = qualitative_colors(5, set='tol')

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.invert_yaxis()
        #ax.xaxis.set_visible(False)

        labels = [pid for pid, _ in data]
        starts = {pid: 0 for pid, _ in data}

        for i, (cat, color) in enumerate(zip(cats, colors)):
            widths = [values.count(cat) for _, values in data]
            rects = ax.barh(
                labels,
                widths,
                left=[starts[pid] for pid, _ in data],
                height=0.7,
                label=cat,
                color=color)
            ax.bar_label(rects, label_type='center', color='white')
            for pid, values in data:
                starts[pid] += values.count(cat)
        ax.legend(
            ncols=len(labels),
            bbox_to_anchor=(0, 1),
            loc='lower left',
            fontsize='small')
