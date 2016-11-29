import sys, seaborn, dateutil.parser, numpy, json
from matplotlib import pyplot

data = json.load(open(sys.argv[1]))
y = numpy.array(data['y'])
pyplot.figure(figsize=(13, 8))
pyplot.stackplot([dateutil.parser.parse(t) for t in data['ts']],
                  numpy.array(y),
                  labels=data['labels'])
pyplot.legend(loc=2)
pyplot.ylabel('Lines of code')
pyplot.savefig('stack_plot.png')
pyplot.show()
