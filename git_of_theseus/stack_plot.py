# -*- coding: utf-8 -*-
#
# Copyright 2016 Erik Bernhardsson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import matplotlib
matplotlib.use('Agg')

import argparse, dateutil.parser, itertools, json, numpy, sys
from matplotlib import pyplot
from collections import defaultdict


def generate_n_colors(n):
    vs = numpy.linspace(0.4, 1.0, 7)
    colors = [(.9, .4, .4)]
    def euclidean(a, b):
        return sum((x-y)**2 for x, y in zip(a, b))
    while len(colors) < n:
        new_color = max(itertools.product(vs, vs, vs), key=lambda a: min(euclidean(a, b) for b in colors))
        colors.append(new_color)
    return colors


def stack_plot(input_fns, display=False,
    outfile='stack_plot.png', max_n=20, normalize=False, dont_stack=False, outmerged=False):
    
    loc = {}  # Helper data structure
    authors = set()  # All authors
    tss = set()  # All timestamps
    for fn in input_fns:
        print('Reading %s' % fn)
        data = json.load(open(fn))
        locr = defaultdict(defaultdict)
        for i, a in enumerate(data['labels']):
            authors.add(a)
            locr[a] = {}
            for j, t in enumerate(data['ts']):
                tss.add(t)
                locr[a][t] = data['y'][i][j]
        loc[fn] = locr

    authorss = sorted(authors)  # Authors, sorted
    tsss = sorted(tss)  # Timestamps, sorted

    merged = [[0 for j in range(len(tsss))] for i in range(len(authorss))]

    for i, r in enumerate(loc):
        # print("repo: ", r)
        for j, a in enumerate(authorss):
            # print("  ", a)
            l = 0
            for k, t in enumerate(tsss):
                # print(r, a, t)
                if a in loc[r].keys():
                    if t in loc[r][a].keys():
                        l = loc[r][a][t]
                        # print("l = ", l)
                merged[j][k] = merged[j][k] + l

    data = {
        'y': merged,
        'ts': [t for t in tsss],
        'labels': [a for a in authorss]
    }
    if outmerged:
        mergefn = 'merged.json'
        print('Writing data to %s' % mergefn)
        f = open(mergefn, 'w')
        json.dump(
            {
                'y': merged,
                'ts': [t for t in tsss],
                'labels': [a for a in authorss]
            }, f)
        f.close()

    y = numpy.array(data['y'])
    if y.shape[0] > max_n:
        js = sorted(range(len(data['labels'])), key=lambda j: max(y[j]), reverse=True)
        other_sum = numpy.sum(y[j] for j in js[max_n:])
        top_js = sorted(js[:max_n], key=lambda j: data['labels'][j])
        y = numpy.array([y[j] for j in top_js] + [other_sum])
        labels = [data['labels'][j] for j in top_js] + ['other']
    else:
        labels = data['labels']
    if normalize:
        y = 100. * numpy.array(y) / numpy.sum(y, axis=0)
    pyplot.figure(figsize=(13, 8))
    pyplot.style.use('ggplot')
    ts = [dateutil.parser.parse(t) for t in data['ts']]
    colors = generate_n_colors(len(labels))
    if dont_stack:
        for color, label, series in zip(colors, labels, y):
            pyplot.plot(ts, series, color=color, label=label, linewidth=2)
    else:
        pyplot.stackplot(ts, numpy.array(y), labels=labels, colors=colors)
    pyplot.legend(loc=2)
    if normalize:
        pyplot.ylabel('Share of lines of code (%)')
        pyplot.ylim([0, 100])
    else:
        pyplot.ylabel('Lines of code')
    print('Writing output to %s' % outfile)
    pyplot.savefig(outfile)
    pyplot.tight_layout()
    if display:
        pyplot.show()


def stack_plot_cmdline():
    parser = argparse.ArgumentParser(description='Plot stack plot')
    parser.add_argument('--display', action='store_true', help='Display plot')
    parser.add_argument('--outfile', default='stack_plot.png', type=str, help='Output file to store results (default: %(default)s)')
    parser.add_argument('--max-n', default=20, type=int, help='Max number of dataseries (will roll everything else into "other") (default: %(default)s)')
    parser.add_argument('--normalize', action='store_true', help='Normalize the plot to 100%%')
    parser.add_argument('--dont-stack', action='store_true', help='Don\'t stack plot')
    parser.add_argument('--outmerged', action='store_true', help='Output merged data to merged.json')
    parser.add_argument('input_fns', nargs='*')
    kwargs = vars(parser.parse_args())

    stack_plot(**kwargs)


if __name__ == '__main__':
    stack_plot_cmdline()
