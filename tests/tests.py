# Tests for stack_plot
#
# To run tests:
#   (1) ensure that git-of-theuseus in installed
#   (2) go to folder tests and
#   (3) python tests.py 

import json
from git_of_theseus import stack_plot

print('Testing stack_plot...')

print('Test 1 - Run stack_plot for repos 1 and 2')
out_fn = 'stack_plot.png'
in_fns = ['test_data_repo_1.json', 'test_data_repo_2.json']

stack_plot(outfile=out_fn, input_fns=in_fns, outmerged=True)

# merged.json and test_data_merged.json must have equal JSON contents.
if json.load(open('merged.json')) == json.load(open('test_data_merged_1_2.json')):
    print('Test succeeded')
else:
    print('Test failed')

print('Test 2 - Run stack_plot for repo 1')
out_fn = 'stack_plot.png'
in_fns = ['test_data_repo_1.json']

stack_plot(outfile=out_fn, input_fns=in_fns, outmerged=True)

# merged.json and test_data_merged.json must have equal JSON contents.
if json.load(open('merged.json')) == json.load(open('test_data_repo_1.json')):
    print('Test succeeded')
else:
    print('Test failed')
