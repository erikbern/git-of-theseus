from distutils.core import setup

setup(name='git-of-theseus',
      version='0.1.4',
      description='Plot stats on Git repositories',
      author='Erik Bernhardsson',
      author_email='mail@erikbern.com',
      url='https://github.com/erikbern/git-of-theseus',
      packages=['git_of_theseus'],
      scripts=['scripts/git-of-theseus-analyze', 'scripts/git-of-theseus-stack-plot', 'scripts/git-of-theseus-survival-plot'],
      install_requires=[
          'gitpython',
          'numpy',
          'progressbar2',
          'pygments',
          'matplotlib',
          'seaborn',
      ]
)
