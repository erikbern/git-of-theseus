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

import sys, seaborn, dateutil.parser, numpy, json, collections, math, scipy.optimize, argparse, os

from matplotlib import pyplot

def survival_plot():
    parser = argparse.ArgumentParser(description='Plot survival plot')
    parser.add_argument('--exp-fit', action='store_true', help='Plot exponential fit')
    parser.add_argument('--display', action='store_true', help='Display plot')
    parser.add_argument('--outfile', default='survival_plot.png', help='Output file to store results (default: %(default)s)')
    parser.add_argument('--years', type=float, default=5, help='Number of years on x axis (default: %(default)s)')
    parser.add_argument('inputs', nargs='*')
    args = parser.parse_args()

    all_deltas = []
    YEAR = 365.25 * 24 * 60 * 60
    pyplot.figure(figsize=(13, 8))

    for fn in args.inputs:
        print('reading %s' % fn)
        commit_history = json.load(open(fn))

        print('counting %d commits' % len(commit_history))
        deltas = collections.defaultdict(lambda: numpy.zeros(2))
        total_n = 0
        for commit, history in commit_history.items():
            t0, orig_count = history[0]
            total_n += orig_count
            last_count = orig_count
            for t, count in history[1:]:
                deltas[t-t0] += (count-last_count, 0)
                last_count = count
            deltas[history[-1][0] - t0] += (-last_count, -orig_count)

        all_deltas.append((total_n, deltas))
        print('adding %d deltas...' % len(deltas))
        total_k = total_n
        P = 1.0
        xs = []
        ys = []
        for t in sorted(deltas.keys()):
            delta_k, delta_n = deltas[t]
            xs.append(t / YEAR)
            ys.append(100. * P)
            P *= 1 + delta_k / total_n
            total_k += delta_k
            total_n += delta_n
            if P < 0.05:
                break

        print('plotting...')
        if args.exp_fit:
            pyplot.plot(xs, ys, color='darkgray')
        else:
            parts = os.path.split(fn)
            pyplot.plot(xs, ys, label=(len(parts) > 1 and parts[-2] or None))


    def fit(k):
        loss = 0.0
        for total_n, deltas in all_deltas:
            total_k = total_n
            P = 1.0
            for t in sorted(deltas.keys()):
                delta_k, delta_n = deltas[t]
                pred = total_n * math.exp(-k * t / YEAR)
                loss += (total_n * P - pred)**2
                P *= 1 + delta_k / total_n
                total_k += delta_k
                total_n += delta_n
        print(k, loss)
        return loss

    if args.exp_fit:
        print('fitting exponential function')
        k = scipy.optimize.fmin(fit, 0.5, maxiter=50)[0]
        ts = numpy.linspace(0, args.years, 1000)
        ys = [100. * math.exp(-k * t) for t in ts]
        pyplot.plot(ts, ys, color='red', label='Exponential fit, half-life = %.2f years' % (math.log(2) / k))

    pyplot.xlabel('Years')
    pyplot.ylabel('%')
    pyplot.xlim([0, args.years])
    pyplot.ylim([0, 100])
    pyplot.title('% of lines still present in code after n years')
    pyplot.legend()
    pyplot.tight_layout()
    pyplot.savefig(args.outfile)
    if args.display:
        pyplot.show()


if __name__ == '__main__':
    survival_plot()
