from distutils.core import setup

setup(name='Git of Theseus',
      version='0.0.1',
      description='Plot stats on Git repositries',
      author='Erik Bernhardsson',
      author_email='mail@erikbern.com',
      url='https://github.com/erikbern/git-of-theseus',
      packages=['git_of_theseus'],
      scripts=['scripts/git-of-theseus-analyze', 'scripts/git-of-theseus-stack-plot', 'scripts/git-of-theseus-survival-plot'],
      install_requires=[line.strip() for line in open('requirements.txt')]
)
