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

.. automodule:: impscan.conda_meta.archive_types
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.conda_meta.async_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.conda_meta.formats
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.conda_meta.so_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.conda_meta.tar_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.conda_meta.url_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.conda_meta.zip_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.conda_meta.zstd_utils
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


.. automodule:: impscan.db.db_utils
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.db.generate_db
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.db.version_utils
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


.. automodule:: impscan.lookup.conda_util
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.lookup.listings_xref
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.lookup.pypi_util
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.lookup.req_spec
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


.. automodule:: impscan.scanner.ast_parsing
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.scanner.ast_utils
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.scanner.build_utils
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.scanner.import_utils
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.scanner.module_utils
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.scanner.requirement
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.scanner.sanitiser
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: impscan.scanner.scan
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

.. automodule:: impscan.share.http_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: impscan.share.multiproc_utils
   :members:
   :undoc-members:
   :show-inheritance:

Streaming
=========

Stream handling.

----


.. automodule:: impscan.streams.conda_unbox
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
