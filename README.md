# impscan

> Command line tool to identify minimal imports list and
> repository sources by parsing package dependency trees

Scan imports in a directory, determine which are non-standard library,
and then (tentatively) determine the package dependency tree and
prune the requirements accordingly, as well as determining which
can be obtained from Conda (and on which channels) and which from PyPi.

Unlike some other refactoring tools, `impscan` does not
need to operate on a package (e.g. it can just be scripts)

## Output

Since many packages (e.g. [numpy](https://docs.anaconda.com/mkl-optimizations/index.html))
have optimised builds available via conda, it is desirable to
mix conda and PyPi packages in an environment, for which
[recommended best practice](https://www.anaconda.com/blog/using-pip-in-a-conda-environment)
is to install PyPi packages afterwards.

Identifying this accurately is important to save time for software developers:

- repeated "just one more..." installations delaying first run of a package,
- avoiding multiple iterations of tearing down and recreating development environments
  when they are done incorrectly

Two types of output are therefore required:

- `CONDA_SETUP.md`, a human-readable markdown file opening with a shell code block
  describing the commands to run to create (or re-create) a given development environment,
  into which any modifications can be added.

  - This kind of artifact is helpful at reducing iteration time when you can't recall
    quite how you achieved a particularly tricky environment setup.

- `requirements.txt`, a machine-readable text list of packages imported by the code in question
  (note: out of simplicity, no distinction is made between dev and release requirements)

  - The purpose of this file is for each package to be verified as installed upon package setup.
    It is not necessary for this to be used for the installation of packages!

  - This is often misused (in my opinion) when versions are simply pinned (which is
    a somewhat arbitrary decision by the package manager, and does not comprise "reproducibility")

## Workflow

- Identify imports
- Identify total dependency tree
- Prune dependency tree
- Identify sources (obeying source preferences if specified)
- Save `CONDA_SETUP.md` and `requirements.txt`
