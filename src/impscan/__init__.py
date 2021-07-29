r"""
impscan
=======

Command line tool to identify minimal imports list and
repository sources by parsing package dependency trees

---

Scan imports in a directory, determine which are non-standard library,
and then (tentatively) determine the package dependency tree and
prune the requirements accordingly, as well as determining which
can be obtained from Conda (and on which channels) and which from PyPI.

Unlike some other refactoring tools, ``impscan`` does not
need to operate on a package (e.g. it can just be scripts)

Currently, requirements (AKA "root packages"), imported module name
("site packages" name) and other features are computed for one build
for every package on conda's ``anaconda`` and ``conda-forge`` channels
(over 20,000 packages).

Workflow
--------

- Identify imports
- Identify total dependency tree
- Prune dependency tree
- Identify sources (obeying source preferences if specified)
- Save artifacts: ``CONDA_SETUP.md`` and ``requirements.txt``
"""

from . import conda_meta, db
from .cli import *

__author__ = "Louis Maddox"
__license__ = "MIT"
__description__ = """Command line tool to identify minimal imports list \
and repository sources by parsing package dependency trees"""
__url__ = "https://github.com/lmmx/impscan"
__uri__ = __url__
__email__ = "louismmx@gmail.com"
