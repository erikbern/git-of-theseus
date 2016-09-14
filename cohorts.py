from __future__ import print_function
import git, sys, datetime, numpy, traceback
from matplotlib import pyplot
import seaborn, progressbar

repo = git.Repo(sys.argv[1])
fm = '%Y'
interval = 7 * 24 * 60 * 60
commit2cohort = {}

for commit in repo.iter_commits('master'):
    cohort = datetime.datetime.utcfromtimestamp(commit.committed_date).strftime(fm)
    commit2cohort[commit.hexsha] = cohort

last_date = None
curves = {}
ts = []
for commit in repo.iter_commits('master'):
    if last_date is not None and commit.committed_date > last_date - interval:
        continue
    t = datetime.datetime.utcfromtimestamp(commit.committed_date)
    ts.append(t)
    print(commit.hexsha, t)
    
    last_date = commit.committed_date
    histogram = {}
    entries = [entry for entry in commit.tree.traverse()
               if entry.type == 'blob' and entry.mime_type.startswith('text/')]
    bar = progressbar.ProgressBar(max_value=len(entries))
    for i, entry in enumerate(entries):
        bar.update(i)
        try:
            for old_commit, lines in repo.blame(commit, entry.path):
                cohort = commit2cohort[old_commit.hexsha]
                histogram[cohort] = histogram.get(cohort, 0) + len(lines)
                curves.setdefault(cohort, [])
        except:
            traceback.print_exc()

    for cohort, curve in curves.items():
        curve.append(histogram.get(cohort, 0))

    def rev(l):
        return list(reversed(l))
    cohorts = list(sorted(curves.keys()))
    x = rev(ts)
    y = numpy.array([rev(curves[cohort]) for cohort in cohorts])
    pyplot.clf()
    pyplot.stackplot(x, y, labels=['Code added in %s' % c for c in cohorts])
    pyplot.legend(loc=2)
    pyplot.ylabel('Lines of code')
    pyplot.savefig('cohorts.png')
        
