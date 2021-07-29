=============
API Reference
=============

.. automodule:: impscan
   :members:
   :undoc-members:
   :show-inheritance:

Conda metadata
==============

This class represents a file being streamed as a sequence of non-overlapping
ranges.

----


.. automodule:: impscan.conda_meta
   :members:
   :undoc-members:
   :show-inheritance:


Database handling
=================

Set up a database to store the package archive listings in.

----


.. automodule:: impscan.db
   :members:
   :undoc-members:
   :show-inheritance:


Lookup
======

?

----


.. automodule:: impscan.lookup
   :members:
   :undoc-members:
   :show-inheritance:


Scanning
========

The :mod:`~impscan.scanner` subpackage handles import module name identification

----


.. automodule:: impscan.scanner
   :members:
   :undoc-members:
   :show-inheritance:


Miscellaneous shared utils
==========================

These are the commonly used parts of the library.

----


.. automodule:: impscan.share
   :members:
   :undoc-members:
   :show-inheritance:

Streaming
=========

Stream handling.

----


.. automodule:: impscan.streams
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

CLI
===

The command-line tool ``impscan`` is made available as an entrypoint to
:func:`impscan.__main__.main`, in turn a thin interface to :mod:`impscan.cli`.

---

.. automodule:: impscan.cli
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:


Config
======

Configuration handling.

---

.. automodule:: impscan.config
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:
