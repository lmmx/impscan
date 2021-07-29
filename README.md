# impscan

> Command line tool to identify minimal imports list and
> repository sources by parsing package dependency trees

Scan imports in a directory, determine which are non-standard library,
and then (tentatively) determine the package dependency tree and
prune the requirements accordingly, as well as determining which
can be obtained from Conda (and on which channels) and which from PyPI.

Unlike some other refactoring tools, `impscan` does not
need to operate on a package (e.g. it can just be scripts)

Currently, requirements (AKA "root packages"), imported module name
("site packages" name) and other features are computed for one build
for every package on conda's `anaconda` and `conda-forge` channels
(over 20,000 packages).

## System requirements

- Python 3.8+
  - If you want to target an earlier version of Python for dependency checks,
    specify it with the `-v`/`--version` flag.

The detection of imported names relies on `site-packages` paths which
Linux and macOS both have but Windows does not, so that functionality
won't work on Windows. Feel free to open an issue to discuss developing this
if interested.

## Usage

```
usage: impscan [-h] [-q] [-e EXCLUDE] [-b] source_path

Scan imports and produce summary files for environment setup

positional arguments:
  source_path           Input path to scan Python files in

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Don't print to STDOUT
  -e EXCLUDE, --exclude EXCLUDE
                        Manually exclude a module name
  -b, --build           Produce dev build requirements (do not drop requirements marked
                        'build-system')
```

e.g.

```sh
impscan ./my_package_dir/
impscan ./one_module.py
```

and add `-e foo` to exclude the name "foo" from going into any requirements lists.

## Output

Since many packages (e.g. [numpy](https://docs.anaconda.com/mkl-optimizations/index.html))
have optimised builds available via conda, it is desirable to
mix conda and PyPI packages in an environment, for which
[recommended best practice](https://www.anaconda.com/blog/using-pip-in-a-conda-environment)
is to install PyPI packages afterwards.

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
