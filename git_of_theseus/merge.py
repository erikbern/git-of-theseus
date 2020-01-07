# Copyright 2020 Priit Parmakson
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

# This script merges authors.json files produced by 
# git-of-theseus-analyze, so that authors chart can be produced
# over multiple repos. Output is written to file mergedAuthors.json
# by default.
#
# Usage:
#     python merge [--outfile <output file>] <authors.json file>...
#
# e.g.:
#     python merge --outfile chart.png authors1.json authors2.json

import argparse, json, os
from collections import defaultdict

def merge(input_fns, outfile='mergedAuthors.json'):

    loc = {}  # Helper data structure
    authors = set()  # All authors
    tss = set()  # All timestamps
    for fn in input_fns:
        print('Reading %s' % fn)
        data = json.load(open(fn))
        locr = defaultdict(defaultdict)
        for i, a in enumerate(data['labels']):
            authors.add(a)
            locr[a] = {}
            for j, t in enumerate(data['ts']):
                tss.add(t)
                locr[a][t] = data['y'][i][j]
        loc[fn] = locr

    authorss = sorted(authors)  # Authors, sorted
    tsss = sorted(tss)  # Timestamps, sorted

    merged = [[0 for j in range(len(tsss))] for i in range(len(authorss))]

    for i, r in enumerate(loc):
        # print("repo: ", r)
        for j, a in enumerate(authorss):
            # print("  ", a)
            l = 0
            for k, t in enumerate(tsss):
                # print(r, a, t)
                if a in loc[r].keys():
                    if t in loc[r][a].keys():
                        l = loc[r][a][t]
                        # print("l = ", l)
                merged[j][k] = merged[j][k] + l

    print('Writing merged authors data to %s' % outfile)
    f = open(outfile, 'w')
    json.dump(
        {
            'y': merged,
            'ts': [t for t in tsss],
            'labels': [a for a in authorss]
        }, f)
    f.close()

def merge_cmdline():
    parser = argparse.ArgumentParser(description='Merge author stats files')
    parser.add_argument('--outfile', default='mergedAuthors.json', type=str, help='Output file to store results (default: %(default)s)')
    parser.add_argument('input_fns', nargs='*')
    kwargs = vars(parser.parse_args())

    merge(**kwargs)

if __name__ == '__main__':
    merge_cmdline()