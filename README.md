# impscan

Scan imports in a directory, determine which are non-standard library,
and then (tentatively) determine the package dependency tree and
prune the requirements accordingly, as well as determining which
can be obtained from Conda (and on which channels) and which from PyPi.

Unlike some other refactoring tools, `impscan` does not
need to operate on a package (e.g. it can just be scripts)
