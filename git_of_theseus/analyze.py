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

import argparse
import datetime
import git
import json
import multiprocessing
import os
import pygments.lexers
import warnings

from tqdm import tqdm
from wcmatch import fnmatch

# Some filetypes in Pygments are not necessarily computer code, but configuration/documentation. Let's not include those.
IGNORE_PYGMENTS_FILETYPES = ['*.json', '*.md', '*.ps', '*.eps', '*.txt', '*.xml', '*.xsl', '*.rss', '*.xslt', '*.xsd', '*.wsdl', '*.wsf', '*.yaml', '*.yml']

default_filetypes = set()
for _, _, filetypes, _ in pygments.lexers.get_all_lexers():
    default_filetypes.update(filetypes)
default_filetypes.difference_update(IGNORE_PYGMENTS_FILETYPES)


class BlameProc(multiprocessing.Process):
    def __init__(self, repo_dir, q, ret_q, blame_kwargs, commit2cohort, commit2timestamp):
        super().__init__(daemon=True)
        self.repo: git.Repo = git.Repo(repo_dir)
        self.q: multiprocessing.Queue = q
        self.ret_q: multiprocessing.Queue = ret_q
        self.blame_kwargs = dict(blame_kwargs)
        self.commit2cohort = dict(commit2cohort)
        self.commit2timestamp = dict(commit2timestamp)

    # Get Blame data for a `file` at `commit`
    def get_file_histogram(self, path, blame):
        h = {}
        for old_commit, lines in blame:
            cohort = self.commit2cohort.get(old_commit.hexsha, "MISSING")
            _, ext = os.path.splitext(path)
            keys = [('cohort', cohort), ('ext', ext), ('author', old_commit.author.name)]

            if old_commit.hexsha in self.commit2timestamp:
                keys.append(('sha', old_commit.hexsha))

            for key in keys:
                h[key] = h.get(key, 0) + len(lines)

        return h

    def run(self):
        try:
            while True:
                entry, commit = self.q.get()
                self.ret_q.put((entry, self.get_file_histogram(entry, self.repo.blame(commit, entry, **self.blame_kwargs))))
        except:
            pass


class BlameDriver:
    def __init__(self, repo_dir, proc_count, last_file_y, cur_y, blame_kwargs, commit2cohort, commit2timestamp, quiet):
        self.repo_dir = repo_dir
        self.q = multiprocessing.Queue()
        self.ret_q = multiprocessing.Queue()
        self.last_file_y = last_file_y
        self.cur_y = cur_y
        self.proc_pool = []
        if not quiet:
            print('Starting up processes: ', end='')
        for i in range(proc_count):
            self.proc_pool.append(BlameProc(repo_dir, self.q, self.ret_q, blame_kwargs, commit2cohort, commit2timestamp))
            self.proc_pool[i].start()
            if not quiet:
                print(i if i == 0 else ', ' + str(i), end='\n' if i == proc_count - 1 else '')

    def fetch(self, commit, check_entries, bar):
        processed_entries = 0
        total_entries = len(check_entries)

        for entry in check_entries:
            self.q.put((entry.path, commit.hexsha))

        while processed_entries < total_entries:
            path, file_y = self.ret_q.get()

            for key_tuple, file_locs in file_y.items():
                self.cur_y[key_tuple] = self.cur_y.get(key_tuple, 0) + file_locs
            self.last_file_y[path] = file_y
            processed_entries += 1
            bar.update()

        return self.cur_y


def analyze(repo_dir, cohortfm='%Y', interval=7 * 24 * 60 * 60, ignore=[], only=[], outdir='.', branch='master',
            all_filetypes=False, ignore_whitespace=False, procs=2, quiet=False, opt=False):
    repo = git.Repo(repo_dir)
    blame_kwargs = {}
    if ignore_whitespace:
        blame_kwargs['w'] = True
    master_commits = []  # only stores a subset
    commit2cohort = {}
    commit2timestamp = {}
    curve_key_tuples = set()  # Keys of each curve that will be tracked
    tqdm_args = {
        'smoothing': 0.025,  # Exponential smoothing is still rather jumpy, a tiny number will do
        'disable': quiet
    }
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Check if specified branch exists
    try:
        repo.git.show_ref('refs/heads/{:s}'.format(branch), verify=True)
    except git.exc.GitCommandError:
        default_branch = repo.active_branch.name
        warnings.warn("Requested branch: '{:s}' does not exist. Falling back to default branch: '{:s}'".format(branch, default_branch))

        branch = default_branch

    if not quiet and repo.git.version_info < (2, 31, 0):
        print('Old Git version {:d}.{:d}.{:d} detected. There are optimizations available in version 2.31.0 which speed up performance'.format(*repo.git.version_info))

    if opt:
        if not quiet:
            print('Generating git commit-graph... If you wish, this file is deletable later at .git/objects/info')
        repo.git.execute(['git', 'commit-graph', 'write', '--changed-paths'])  # repo.git.commit_graph('write --changed-paths') doesn't work for some reason

    desc = '{:<55s}'.format('Listing all commits')
    for commit in tqdm(repo.iter_commits(branch), desc=desc, unit=' Commits', **tqdm_args):
        cohort = datetime.datetime.utcfromtimestamp(commit.committed_date).strftime(cohortfm)
        commit2cohort[commit.hexsha] = cohort
        curve_key_tuples.add(('cohort', cohort))
        curve_key_tuples.add(('author', commit.author.name))
        commit2timestamp[commit.hexsha] = commit.committed_date

    desc = '{:<55s}'.format('Backtracking the master branch')
    with tqdm(desc=desc, unit=' Commits', **tqdm_args) as bar:
        commit = repo.head.commit
        last_date = None
        while True:
            if last_date is None or commit.committed_date < last_date - interval:
                master_commits.append(commit)
                last_date = commit.committed_date
            bar.update()
            if not commit.parents:
                break
            commit = commit.parents[0]

    def_ft_str = '+({:s})'.format('|'.join(default_filetypes))
    path_match_str = '{:s}|!+({:s})'.format('|'.join(only), '|'.join(ignore))
    path_match_zero = len(only) == 0 and len(ignore) == 0
    ok_entry_paths = dict()
    entry_cache = {}

    def entry_path_ok(path):
        # All this matching is slow so let's cache it
        if path not in ok_entry_paths:
            ok_entry_paths[path] = (
                    (all_filetypes or fnmatch.fnmatch(os.path.split(path)[-1], def_ft_str, flags=fnmatch.EXTMATCH))
                    and (path_match_zero or fnmatch.fnmatch(path, path_match_str, flags=fnmatch.NEGATE | fnmatch.EXTMATCH | fnmatch.SPLIT))
            )
        return ok_entry_paths[path]

    def get_entries(commit):
        if commit.hexsha not in entry_cache:
            entry_cache[commit.hexsha] = [entry for entry in commit.tree.traverse() if entry.type == 'blob' and entry_path_ok(entry.path)]
        return entry_cache[commit.hexsha]

    def get_top_dir(path):
        return os.path.dirname(path).split(os.sep)[0] + os.sep

    master_commits = master_commits[::-1]  # Reverse it so it's chnological ascending
    entries_total = 0
    desc = '{:<55s}'.format('Discovering entries & caching filenames')
    with tqdm(desc='{:<55s}'.format('Entries Discovered'), unit=' Entries', position=1, **tqdm_args) as bar:
        for commit in tqdm(master_commits, desc=desc, unit=' Commits', position=0, **tqdm_args):
            for entry in get_entries(commit):
                entries_total += 1
                _, ext = os.path.splitext(entry.path)
                curve_key_tuples.add(('ext', ext))
                curve_key_tuples.add(('dir', get_top_dir(entry.path)))
                bar.update()

    curves = {}  # multiple y axis, in the form key_tuple: Array[y-axis points]
    ts = []  # x axis
    last_file_y = {}  # Contributions of each individual file to each individual curve, when the file was last seen
    cur_y = {}  # Sum of all contributions between files towards each individual curve
    commit_history = {}  # How many lines of a commit (by SHA) still exist at a given time
    last_file_hash = {}  # File SHAs when they were last seen
    blamer = BlameDriver(repo_dir, procs, last_file_y, cur_y, blame_kwargs, commit2cohort, commit2timestamp, quiet)

    desc = '{:<55s}'.format('Analyzing commit history with {:d} processes'.format(procs))
    with tqdm(desc='{:<55s}'.format('Entries Processed'), total=entries_total, unit=' Entries', position=1, **tqdm_args) as bar:
        for commit in tqdm(master_commits, desc=desc, unit=' Commits', position=0, **tqdm_args):
            t = datetime.datetime.utcfromtimestamp(commit.committed_date)
            ts.append(t)  # x axis

            # START: Fast diff, to reduce no. of files checked via blame.
            # File hashes are checked against previous iteration
            entries = get_entries(commit)

            check_entries = []
            cur_file_hash = {}
            for entry in entries:
                cur_file_hash[entry.path] = entry.binsha
                if entry.path in last_file_hash:
                    if last_file_hash[entry.path] != entry.binsha:  # Modified file
                        for key_tuple, count in last_file_y[entry.path].items():
                            cur_y[key_tuple] -= count
                        check_entries.append(entry)
                    else:  # Identical file
                        bar.update()
                    del last_file_hash[entry.path]  # Identical/Modified file deleted, leaving deleted behind
                else:  # Newly added file
                    check_entries.append(entry)
            for deleted_path in last_file_hash.keys():  # Deleted files
                for key_tuple, count in last_file_y[deleted_path].items():
                    cur_y[key_tuple] -= count
            last_file_hash = cur_file_hash
            # END: Fast diff

            # Multiprocess blame checker, updates cur_y
            blamer.fetch(commit, check_entries, bar)

            for key_tuple, count in cur_y.items():
                key_category, key = key_tuple
                if key_category == 'sha':
                    commit_history.setdefault(key, []).append((commit.committed_date, count))

            for key_tuple in curve_key_tuples:
                curves.setdefault(key_tuple, []).append(cur_y.get(key_tuple, 0))

    def dump_json(output_fn, key_type, label_fmt=lambda x: x):
        key_items = sorted(k for t, k in curve_key_tuples if t == key_type)
        fn = os.path.join(outdir, output_fn)
        if not quiet:
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
    dump_json('dirs.json', 'dir')

    # Dump survival data
    fn = os.path.join(outdir, 'survival.json')
    f = open(fn, 'w')
    if not quiet:
        print('Writing survival data to %s' % fn)
    json.dump(commit_history, f)
    f.close()


def analyze_cmdline():
    parser = argparse.ArgumentParser(description='Analyze git repo')
    parser.add_argument('--cohortfm', default='%Y', type=str, help='A Python datetime format string such as "%%Y" for creating cohorts (default: %(default)s)')
    parser.add_argument('--interval', default=7 * 24 * 60 * 60, type=int, help='Min difference between commits to analyze (default: %(default)ss)')
    parser.add_argument('--ignore', default=[], action='append', help='File patterns that should be ignored (can provide multiple, will each subtract independently)')
    parser.add_argument('--only', default=[], action='append', help='File patterns that can match (can provide multiple, will match any one)')
    parser.add_argument('--outdir', default='.', help='Output directory to store results (default: %(default)s)')
    parser.add_argument('--branch', default='master', type=str, help='Branch to track (default: %(default)s)')
    parser.add_argument('--ignore-whitespace', default=[], action='store_true', help='Ignore whitespace changes when running git blame.')
    parser.add_argument('--all-filetypes', action='store_true', help='Include all files (if not set then will only analyze %s' % ','.join(default_filetypes))
    parser.add_argument('--quiet', action='store_true', help='Disable all console output (default: %(default)s)')
    parser.add_argument('--procs', default=2, type=int, help='Number of processes to use. There is a point of diminishing returns (default: %(default)s)')
    parser.add_argument('--opt', action='store_true', help='Generates git commit-graph; Improves performance at the cost of some (~80KB/kCommit) disk space (default: %(default)s)')
    parser.add_argument('repo_dir')
    kwargs = vars(parser.parse_args())

    try:
        analyze(**kwargs)
    except KeyboardInterrupt:
        exit(1)
    except:
        raise


if __name__ == '__main__':
    analyze_cmdline()
