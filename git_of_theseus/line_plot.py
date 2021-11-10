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

import argparse, dateutil.parser, json, numpy, sys
from matplotlib import pyplot


from .utils import generate_n_colors


def line_plot(input_fn, display=False, outfile='line_plot.png', max_n=20):
    data = json.load(open(input_fn))  # TODO do we support multiple arguments here?
    y = numpy.array(data['y'])
    if y.shape[0] > max_n:
        js = sorted(range(len(data['labels'])), key=lambda j: max(y[j]), reverse=True)
        top_js = sorted(js[:max_n], key=lambda j: data['labels'][j])
        y = numpy.array([y[j] for j in top_js])
        labels = [data['labels'][j] for j in top_js]
    else:
        labels = data['labels']
    pyplot.figure(figsize=(16, 12), dpi=120)
    pyplot.style.use('ggplot')
    ts = [dateutil.parser.parse(t) for t in data['ts']]
    colors = generate_n_colors(len(labels))
    for color, label, series in zip(colors, labels, y):
        pyplot.plot(ts, series, color=color, label=label, linewidth=3)
    pyplot.legend(loc=2)
    pyplot.ylabel('Lines of code')
    print('Writing output to %s' % outfile)
    pyplot.savefig(outfile)
    pyplot.tight_layout()
    if display:
        pyplot.show()


def line_plot_cmdline():
    parser = argparse.ArgumentParser(description='Plot line plot')
    parser.add_argument('--display', action='store_true', help='Display plot')
    parser.add_argument('--outfile', default='line_plot.png', type=str, help='Output file to store results (default: %(default)s)')
    parser.add_argument('--max-n', default=20, type=int, help='Max number of dataseries (default: %(default)s)')
    parser.add_argument('input_fn')
    kwargs = vars(parser.parse_args())

    line_plot(**kwargs)


if __name__ == '__main__':
    line_plot_cmdline()
