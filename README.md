[![travis badge](https://img.shields.io/travis/erikbern/git-of-theseus/master.svg?style=flat)](https://travis-ci.org/erikbern/git-of-theseus)

Some scripts to analyze Git repos. Produces cool looking graphs like this (running it on [git](https://github.com/git/git) itself):

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-git.png)

How to run
----------

1. Run `git clone https://github.com/erikbern/git-of-theseus` and `cd git-of-theseus`
1. Run `virtualenv .` and then `. bin/activate` (optional, only if you don't want to install the dependencies as root or in your local pip installation folder)
1. Run `pip install -r requirements.txt` to install dependencies
1. Run `python analyze.py <path to repo>` (see `python analyze.py --help` for a bunch of config)
1. Run `python stack_plot.py cohorts.json` which will write to `stack_plot.png`
1. Run `python survival_plot.py survival.json` which will write to `survival_plot.png` (see `python survival_plot.py --help` for some options)

If you want to plot multiple repositories, have to run `python analyze.py` separately for each project and store the data in separate directories using the `--outdir` flag. Then you can run `python survival_plot.py <foo/survival.json> <bar/survival.json>` (optionally with the `--exp-fit` flag to fit an exponential decay)

Help
----

`AttributeError: Unknown property labels` – upgrade matplotlib if you are seeing this. `pip install matplotlib --upgrade`
  
Some pics
---------

Survival of a line of code in a set of interesting repos:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-projects-survival.png)

This curve is produced by the `survival_plot.py` script and shows the *percentage of lines in a commit that are still present after x years*. It aggregates it over all commits, no matter what point in time they were made. So for *x=0* it includes all commits, whereas for *x>0* not all commits are counted (because we would have to look into the future for some of them). ~~That means the total percentage can go up occasionally.~~ The survival curves are estimated using [Kaplan-Meier](https://en.wikipedia.org/wiki/Kaplan%E2%80%93Meier_estimator).

You can also add an exponential fit:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-projects-survival-exp-fit.png)

Linux – stack plot:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-linux.png)

This curve is produced by the `stack_plot.py` script and shows the total number of lines in a repo broken down into cohorts by the year the code was added.

Node – stack plot:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-node.png)

Rails – stack plot:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-rails.png)

Other stuff
-----------

[Markovtsev Vadim](https://twitter.com/tmarkhor) implemented a very similar analysis that claims to be 20%-6x faster than Git of Theseus. It's named [Hercules](https://github.com/src-d/hercules) and there's a great [blog post](https://blog.sourced.tech/post/hercules/) about all the complexity going into the analysis of Git history.
