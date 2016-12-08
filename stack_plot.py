import sys, seaborn, dateutil.parser, numpy, json, argparse
from matplotlib import pyplot

parser = argparse.ArgumentParser(description='Plot stack plot')
parser.add_argument('--display', action='store_true', help='Display plot')
parser.add_argument('--outfile', default='stack_plot.png', help='Output file to store results (default: %(default)s)')
parser.add_argument('inputs')
args = parser.parse_args()

data = json.load(open(args.inputs[0]))
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
