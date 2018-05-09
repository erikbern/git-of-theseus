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

from __future__ import print_function
import argparse, git, datetime, numpy, pygments.lexers, traceback, time, os, fnmatch, json, progressbar

# Some filetypes in Pygments are not necessarily computer code, but configuration/documentation. Let's not include those.
IGNORE_PYGMENTS_FILETYPES = ['*.json', '*.md', '*.ps', '*.eps', '*.txt', '*.xml', '*.xsl', '*.rss', '*.xslt', '*.xsd', '*.wsdl', '*.wsf', '*.yaml', '*.yml']


def analyze(cohortfm=None, interval=None, ignore=None, only=None, outdir=None, branch=None, all_filetypes=None, repos=None):
    default_filetypes = set()
    for _, _, filetypes, _ in pygments.lexers.get_all_lexers():
        default_filetypes.update(filetypes)
    default_filetypes.difference_update(IGNORE_PYGMENTS_FILETYPES)

    parser = argparse.ArgumentParser(description='Analyze git repo')
    parser.add_argument('--cohortfm', default='%Y', type=str, help='A Python datetime format string such as "%%Y" for creating cohorts (default: %(default)s)')
    parser.add_argument('--interval', default=7*24*60*60, type=int, help='Min difference between commits to analyze (default: %(default)s)')
    parser.add_argument('--ignore', default=[], action='append', help='File patterns that should be ignored (can provide multiple, will each subtract independently)')
    parser.add_argument('--only', default=[], action='append', help='File patterns that have to match (can provide multiple, will all have to match)')
    parser.add_argument('--outdir', default='.', help='Output directory to store results (default: %(default)s)')
    parser.add_argument('--branch', default='master', type=str, help='Branch to track (default: %(default)s)')
    parser.add_argument('--all-filetypes', action='store_true', help='Include all files (if not set then will only analyze %s' % ','.join(default_filetypes))
    parser.add_argument('repos', nargs=1)
    args = parser.parse_args()

    cohortfm = cohortfm or args.cohortfm
    interval = interval or args.interval
    ignore = ignore if ignore is not None else args.ignore
    only = only if only is not None else args.only
    outdir = outdir or args.outdir
    branch = branch or args.branch
    all_filetypes = all_filetypes if all_filetypes is not None else args.all_filetypes
    repos = repos or args.repos

    repo = git.Repo(args.repos[0])
    commit2cohort = {}
    code_commits = [] # only stores a subset
    master_commits = []
    commit2timestamp = {}
    curves_set = set()
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print('Listing all commits')
    with progressbar.ProgressBar(max_value=progressbar.UnknownLength) as bar:
        for i, commit in enumerate(repo.iter_commits(branch)):
            bar.update(i)
            cohort = datetime.datetime.utcfromtimestamp(commit.committed_date).strftime(cohortfm)
            commit2cohort[commit.hexsha] = cohort
            curves_set.add(('cohort', cohort))
            curves_set.add(('author', commit.author.name))
            if len(commit.parents) == 1:
                code_commits.append(commit)
                last_date = commit.committed_date
                commit2timestamp[commit.hexsha] = commit.committed_date

    print('Backtracking the master branch')
    with progressbar.ProgressBar(max_value=progressbar.UnknownLength) as bar:
        i, commit = 0, repo.head.commit
        last_date = None
        while True:
            bar.update(i)
            if not commit.parents:
                break
            if last_date is None or commit.committed_date < last_date - interval:
                master_commits.append(commit)
                last_date = commit.committed_date
            i, commit = i+1, commit.parents[0]

    ok_entry_paths = {}
    def entry_path_ok(path):
        # All this matching is slow so let's cache it
        if path not in ok_entry_paths:
            ok_entry_paths[path] = (
                (all_filetypes or any(fnmatch.fnmatch(os.path.split(path)[-1], filetype) for filetype in default_filetypes))
                and all([fnmatch.fnmatch(path, pattern) for pattern in only])
                and not any([fnmatch.fnmatch(path, pattern) for pattern in ignore]))
        return ok_entry_paths[path]

    def get_entries(commit):
        return [entry for entry in commit.tree.traverse()
                if entry.type == 'blob' and entry_path_ok(entry.path)]

    print('Counting total entries to analyze + caching filenames')
    entries_total = 0
    with progressbar.ProgressBar(max_value=len(master_commits)) as bar:
        for i, commit in enumerate(reversed(master_commits)):
            bar.update(i)
            n = 0
            for entry in get_entries(commit):
                n += 1
                _, ext = os.path.splitext(entry.path)
                curves_set.add(('ext', ext))
            entries_total += n

    def get_file_histogram(commit, path):
        h = {}
        try:
            for old_commit, lines in repo.blame(commit, path):
                cohort = commit2cohort.get(old_commit.hexsha, "MISSING")
                _, ext = os.path.splitext(path)
                keys = [('cohort', cohort), ('ext', ext), ('author', old_commit.author.name)]

                if old_commit.hexsha in commit2timestamp:
                    keys.append(('sha', old_commit.hexsha))

                for key in keys:
                    h[key] = h.get(key, 0) + len(lines)
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
        return h

    curves = {}
    ts = []
    file_histograms = {}
    last_commit = None
    commit_history = {}

    print('Analyzing commit history')
    with progressbar.ProgressBar(max_value=entries_total, widget_kwargs=dict(samples=10000)) as bar:
        entries_processed = 0
        for commit in reversed(master_commits):
            t = datetime.datetime.utcfromtimestamp(commit.committed_date)
            ts.append(t)
            changed_files = set()
            for diff in commit.diff(last_commit):
                if diff.a_blob:
                    changed_files.add(diff.a_blob.path)
                if diff.b_blob:
                    changed_files.add(diff.b_blob.path)
            last_commit = commit

            histogram = {}
            entries = get_entries(commit)
            for entry in entries:
                bar.update(entries_processed)
                entries_processed += 1
                if entry.path in changed_files or entry.path not in file_histograms:
                    file_histograms[entry.path] = get_file_histogram(commit, entry.path)
                for key, count in file_histograms[entry.path].items():
                    histogram[key] = histogram.get(key, 0) + count

            for key, count in histogram.items():
                key_type, key_item = key
                if key_type == 'sha':
                    commit_history.setdefault(key_item, []).append((commit.committed_date, count))

            for key in curves_set:
                curves.setdefault(key, []).append(histogram.get(key, 0))

    def dump_json(output_fn, key_type, label_fmt=lambda x: x):
        key_items = sorted(k for t, k in curves_set if t == key_type)
        fn = os.path.join(outdir, output_fn)
        print('Writing %s data to %s' % (key_type, fn))
        f = open(fn, 'w')
        json.dump({'y': [curves[(key_type, key_item)] for key_item in key_items],
                   'ts': [t.isoformat() for t in ts],
                   'labels': [label_fmt(key_item) for key_item in key_items]
        }, f)
        f.close()

    # Dump accumulated stuff
    dump_json('cohorts.json', 'cohort', lambda c: 'Code added in %s' % c)
    dump_json('exts.json', 'ext')
    dump_json('authors.json', 'author')

    # Dump survival data
    fn = os.path.join(outdir, 'survival.json')
    f = open(fn, 'w')
    print('Writing survival data to %s' % fn)
    json.dump(commit_history, f)
    f.close()


if __name__ == '__main__':
    analyze()
