import sys, seaborn, dateutil.parser, numpy, json
from matplotlib import pyplot

commit_history = json.load(open(sys.argv[1]))

deltas = []
total_n = 0
for commit, history in commit_history.items():
    t0, orig_count = history[0]
    total_n += orig_count
    last_count = orig_count
    for t, count in history[1:]:
        deltas.append((t-t0, count-last_count, 0))
        last_count = count
    deltas.append((history[-1][0] - t0, -last_count, -orig_count))

deltas.sort()
total_k = total_n
xs = []
ys = []
max_total_n = 0
for t, delta_k, delta_n in deltas:
    xs.append(t / (365.25 * 24 * 60 * 60))
    ys.append(100. * total_k / total_n)
    total_k += delta_k
    total_n += delta_n
    max_total_n = max(max_total_n, total_n)
    if total_n < 0.05 * max_total_n:
        break

pyplot.clf()
pyplot.plot(xs, ys)
pyplot.xlabel('Years')
pyplot.ylabel('%')
pyplot.ylim([0, 100])
pyplot.title('% of commit still present in code base over time')
pyplot.show()

