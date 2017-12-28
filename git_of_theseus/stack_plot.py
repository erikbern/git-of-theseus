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

import sys, seaborn, dateutil.parser, numpy, json, argparse

from matplotlib import pyplot

def stack_plot():
    parser = argparse.ArgumentParser(description='Plot stack plot')
    parser.add_argument('--display', action='store_true', help='Display plot')
    parser.add_argument('--outfile', default='stack_plot.png', help='Output file to store results (default: %(default)s)')
    parser.add_argument('inputs')
    args = parser.parse_args()

    data = json.load(open(args.inputs))
    y = numpy.array(data['y'])
    pyplot.figure(figsize=(13, 8))
    pyplot.stackplot([dateutil.parser.parse(t) for t in data['ts']],
                     numpy.array(y),
                     labels=data['labels'])
    pyplot.legend(loc=2)
    pyplot.ylabel('Lines of code')
    pyplot.savefig(args.outfile)
    if args.display:
        pyplot.show()


if __name__ == '__main__':
    stack_plot()
