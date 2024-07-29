"""
112 questions using a 5-point Likert scale.
"""
import collections

from cldfbench_gramadapt import Dataset
import plot_likert
import pandas as pd


def run(args):
    with Dataset().plot_data(__file__) as cldf:
        data = collections.defaultdict(list)

        for v in cldf.objects('ValueTable'):
            if v.parameter.data['datatype'] == 'Scalar' and v.cldf.codeReference:
                data[(v.parameter.data['Domain'], v.parameter.id)].append(v.code.data['Ordinal'])

        ml = max(len(v) for v in data.values())
        for v in data.values():
            while len(v) <= ml:
                v.append(None)

        pid2dom = {}
        all_vars = collections.OrderedDict()
        for (domain, pid), values in sorted(data.items(), key=lambda i: i[0]):
            pid2dom[pid] = domain
            all_vars[pid] = values
        ax = plot_likert.plot_likert(pd.DataFrame(all_vars), [1, 2, 3, 4, 5], figsize=(15, 25))
        labels, last = [], None
        for item in reversed(ax.get_yticklabels()):  # We only label the first variable of each domain
            label = pid2dom[item.get_text()]
            if label != last:
                labels.append(label)
            else:
                labels.append('')
            last = label

        ax.set_yticklabels(reversed(labels))
        for label in ax.get_yticklabels():
            label.set_fontsize('large')
