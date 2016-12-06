Some scripts to analyze Git repos. Produces cool looking graphs like this (running it on [git](https://github.com/git/git) itself):

How to run
----------

1. Run `pip install gitpython seaborn numpy progressbar2` to install dependencies
2. Run `python analyze.py <path to repo>` (see `python analyze.py --help` for a bunch of config)
3. Run `python stack_plot.py cohorts.json` which will write to `stack_plot.png`
4. Run `python survival_plot.py survival.json` which will write to `survival_plot.png`


Some pics
---------

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git.png)

Survival of a line of code in a set of interesting repos:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/projects-survival.png)

Exponential fit:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/projects-survival-exp-fit.png)
