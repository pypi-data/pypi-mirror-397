Crossbar.io Database Library
============================

|PyPI| |Python| |CI| |Docs| |License| |Downloads|

.. |PyPI| image:: https://img.shields.io/pypi/v/cfxdb.svg
   :target: https://pypi.python.org/pypi/cfxdb
.. |Python| image:: https://img.shields.io/pypi/pyversions/cfxdb.svg
   :target: https://pypi.python.org/pypi/cfxdb
.. |CI| image:: https://github.com/crossbario/cfxdb/workflows/main/badge.svg
   :target: https://github.com/crossbario/cfxdb/actions?query=workflow%3Amain
.. |Docs| image:: https://readthedocs.org/projects/cfxdb/badge/?version=latest
   :target: https://cfxdb.readthedocs.io/en/latest/
.. |License| image:: https://img.shields.io/pypi/l/cfxdb.svg
   :target: https://github.com/crossbario/cfxdb/blob/master/LICENSE
.. |Downloads| image:: https://img.shields.io/pypi/dm/cfxdb.svg
   :target: https://pypi.python.org/pypi/cfxdb

--------------

**cfxdb** is a Crossbar.io Python support package with core database access classes
written in native Python. The package allows direct in-memory data access from
Python programs (including Jupyter notebooks) to CrossbarFX edge node data:

* persisted WAMP event history
* persisted router tracing data
* XBR market maker transactions database
* XBR network backend database
* WAMP session cache
* custom user, embedded object databases

Contents
--------

.. toctree::
   :maxdepth: 2

   overview
   installation
   getting-started
   programming-guide/index
   releases
   changelog
   contributing
   OVERVIEW.md
   ai/index

--------------

*Copyright (c) typedef int GmbH. Licensed under the* `MIT License <https://github.com/crossbario/cfxdb/blob/master/LICENSE>`__.
*WAMP, Autobahn, Crossbar.io and XBR are trademarks of typedef int GmbH (Germany).*
