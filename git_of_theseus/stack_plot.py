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

import argparse, dateutil.parser, itertools, json, numpy, seaborn, sys
from matplotlib import pyplot


def generate_n_colors(n):
    vs = numpy.linspace(0.4, 1.0, 7)
    colors = [(.9, .4, .4)]
    def euclidean(a, b):
        return sum((x-y)**2 for x, y in zip(a, b))
    while len(colors) < n:
        new_color = max(itertools.product(vs, vs, vs), key=lambda a: min(euclidean(a, b) for b in colors))
        colors.append(new_color)
    return colors


def stack_plot():
    parser = argparse.ArgumentParser(description='Plot stack plot')
    parser.add_argument('--display', action='store_true', help='Display plot')
    parser.add_argument('--outfile', default='stack_plot.png', help='Output file to store results (default: %(default)s)')
    parser.add_argument('--max-n', default=20, type=int, help='Max number of dataseries (will roll everything else into "other") (default: %(default)s)')
    parser.add_argument('--normalize', action='store_true', help='Normalize the plot to 100%%')
    parser.add_argument('inputs')
    args = parser.parse_args()

    data = json.load(open(args.inputs))
    y = numpy.array(data['y'])
    if y.shape[0] > args.max_n:
        js = sorted(range(len(data['labels'])), key=lambda j: max(y[j]), reverse=True)
        other_sum = numpy.sum(y[j] for j in js[args.max_n:])
        top_js = sorted(js[:args.max_n], key=lambda j: data['labels'][j])
        y = numpy.array([y[j] for j in top_js] + [other_sum])
        labels = [data['labels'][j] for j in top_js] + ['other']
    else:
        labels = data['labels']
    if args.normalize:
        y = 100. * numpy.array(y) / numpy.sum(y, axis=0)
    pyplot.figure(figsize=(13, 8))
    pyplot.stackplot([dateutil.parser.parse(t) for t in data['ts']],
                     numpy.array(y),
                     labels=labels,
                     colors=generate_n_colors(len(labels)))
    pyplot.legend(loc=2)
    if args.normalize:
        pyplot.ylabel('Share of lines of code (%)')
        pyplot.ylim([0, 100])
    else:
        pyplot.ylabel('Lines of code')
    pyplot.savefig(args.outfile)
    pyplot.tight_layout()
    if args.display:
        pyplot.show()


if __name__ == '__main__':
    stack_plot()
