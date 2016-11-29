import sys, seaborn, dateutil.parser, numpy, json, collections, math, scipy.optimize, argparse
from matplotlib import pyplot

parser = argparse.ArgumentParser(description='Plot survival plot')
parser.add_argument('--exp-fit', action='store_true', help='Plot exponential fit')
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
    total_k, initial_total_n = total_n, total_n
    xs = []
    ys = []
    for t in sorted(deltas.keys()):
        delta_k, delta_n = deltas[t]
        xs.append(t / YEAR)
        ys.append(100. * total_k / total_n)
        total_k += delta_k
        total_n += delta_n
        if total_n < 0.05 * initial_total_n:
            break

    print('plotting...')
    if args.exp_fit:
        pyplot.plot(xs, ys, color='darkgray')
    else:
        pyplot.plot(xs, ys)


def fit(k):
    loss = 0.0
    for total_n, deltas in all_deltas:
        total_k = total_n
        for t in sorted(deltas.keys()):
            delta_k, delta_n = deltas[t]
            pred = total_n * math.exp(-k * t / YEAR)
            loss += (total_k - pred)**2
            total_k += delta_k
            total_n += delta_n
    print(k, loss)
    return loss

if args.exp_fit:
    print('fitting exponential function')
    k = scipy.optimize.fmin(fit, 1.0, maxiter=50)[0]
    ts = numpy.linspace(0, args.years, 1000)
    ys = [100. * math.exp(-k * t) for t in ts]
    pyplot.plot(ts, ys, color='red', label='Exponential fit, half-life = %.2f years' % (math.log(2) / k))

pyplot.xlabel('Years')
pyplot.ylabel('%')
pyplot.xlim([0, args.years])
pyplot.ylim([0, 100])
pyplot.title('% of commit still present in code base over time')
pyplot.legend()
pyplot.savefig('survival_plot.png')
pyplot.show()

