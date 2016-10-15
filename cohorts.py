from __future__ import print_function
import git, sys, datetime, numpy, traceback, time
from matplotlib import pyplot
import seaborn, progressbar

repo = git.Repo(sys.argv[1])
fm = '%Y'
interval = 7 * 24 * 60 * 60
commit2cohort = {}
commits = []
bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
for i, commit in enumerate(repo.iter_commits('master')):
    bar.update(i)
    cohort = datetime.datetime.utcfromtimestamp(commit.committed_date).strftime(fm)
    commit2cohort[commit.hexsha] = cohort
    commits.append(commit)

def get_file_histogram(commit, path):
    h = {}
    try:
        for old_commit, lines in repo.blame(commit, entry.path):
            cohort = commit2cohort[old_commit.hexsha]
            h[cohort] = h.get(cohort, 0) + len(lines)
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()
    return h

last_date = None
curves = {}
ts = []
file_histograms = {}
last_commit = None
for commit in reversed(commits):
    if last_date is not None and commit.committed_date < last_date + interval:
        continue
    t = datetime.datetime.utcfromtimestamp(commit.committed_date)
    ts.append(t)
    changed_files = set()
    for diff in commit.diff(last_commit):
        if diff.a_blob:
            changed_files.add(diff.a_blob.path)
        if diff.b_blob:
            changed_files.add(diff.b_blob.path)
    last_commit = commit
    
    last_date = commit.committed_date
    histogram = {}
    entries = [entry for entry in commit.tree.traverse()
               if entry.type == 'blob' and entry.mime_type.startswith('text/')]
    print(commit.hexsha, t, len(entries), len(changed_files))
    bar = progressbar.ProgressBar(max_value=len(entries))
    for i, entry in enumerate(entries):
        bar.update(i)
        if entry.path in changed_files or entry.path not in file_histograms:
            file_histograms[entry.path] = get_file_histogram(commit, entry.path)
        for cohort, count in file_histograms[entry.path].items():
            histogram[cohort] = histogram.get(cohort, 0) + count
            curves.setdefault(cohort, [])

    for cohort, curve in curves.items():
        curve.append(histogram.get(cohort, 0))

print('redrawing cohort plot...')
cohorts = list(sorted(curves.keys()))
y = numpy.array([[0] * (len(ts) - len(curves[cohort])) + curves[cohort] for cohort in cohorts])
pyplot.clf()
pyplot.stackplot(ts, y, labels=['Code added in %s' % c for c in cohorts])
pyplot.legend(loc=2)
pyplot.ylabel('Lines of code')
pyplot.savefig('cohorts.png')

