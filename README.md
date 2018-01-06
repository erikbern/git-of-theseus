[![travis badge](https://img.shields.io/travis/erikbern/git-of-theseus/master.svg?style=flat)](https://travis-ci.org/erikbern/git-of-theseus)
[![pypi badge](https://img.shields.io/pypi/v/git-of-theseus.svg?style=flat)](https://pypi.python.org/pypi/git-of-theseus)

Some scripts to analyze Git repos. Produces cool looking graphs like this (running it on [git](https://github.com/git/git) itself):

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-git.png)

Installing
----------

Run `pip install git-of-theseus`

Running
-------

First, you need to run `git-of-theseus-analyze <path to repo>` (see `git-of-theseus-analyze --help` for a bunch of config). This will analyze a repository and might take quite some time.

After that, you can generate plots! Here are some ways you can do that:

1. Run `git-of-theseus-stack-plot cohorts.json` which will write to `stack_plot.png`
1. Run `git-of-theseus-survival-plot survival.json` which will write to `survival_plot.png` (run it with `--help` for some options)

If you want to plot multiple repositories, have to run `git-of-theseus-analyze` separately for each project and store the data in separate directories using the `--outdir` flag. Then you can run `git-of-theseus-survival-plot <foo/survival.json> <bar/survival.json>` (optionally with the `--exp-fit` flag to fit an exponential decay)

Help
----

`AttributeError: Unknown property labels` – upgrade matplotlib if you are seeing this. `pip install matplotlib --upgrade`
  
Some pics
---------

Survival of a line of code in a set of interesting repos:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-projects-survival.png)

This curve is produced by the `git-of-theseus-survival-plot` script and shows the *percentage of lines in a commit that are still present after x years*. It aggregates it over all commits, no matter what point in time they were made. So for *x=0* it includes all commits, whereas for *x>0* not all commits are counted (because we would have to look into the future for some of them). The survival curves are estimated using [Kaplan-Meier](https://en.wikipedia.org/wiki/Kaplan%E2%80%93Meier_estimator).

You can also add an exponential fit:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-projects-survival-exp-fit.png)

Linux – stack plot:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-linux.png)

This curve is produced by the `git-of-theseus-stack-plot` script and shows the total number of lines in a repo broken down into cohorts by the year the code was added.

Node – stack plot:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-node.png)

Rails – stack plot:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-rails.png)

Plotting other stuff
--------------------

`git-of-theseus-analyze` will write `exts.json`, `cohorts.json` and `authors.json`. You can run `git-of-theseus-stack-plot authors.json` to plot author statistics as well, or `git-of-theseus-stack-plot exts.json` to plot file extension statistics. For author statistics, you might want to create a [.mailmap](https://git-scm.com/docs/git-check-mailmap) file to deduplicate authors. For instance, here's the author statistics for [Kubernetes](https://github.com/kubernetes/kubernetes):

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-kubernetes-authors.png)

You can also normalize it to 100%. Here's author statistics for Git:

![git](https://raw.githubusercontent.com/erikbern/git-of-theseus/master/pics/git-git-authors-normalized.png)

Other stuff
-----------

[Markovtsev Vadim](https://twitter.com/tmarkhor) implemented a very similar analysis that claims to be 20%-6x faster than Git of Theseus. It's named [Hercules](https://github.com/src-d/hercules) and there's a great [blog post](https://blog.sourced.tech/post/hercules/) about all the complexity going into the analysis of Git history.
