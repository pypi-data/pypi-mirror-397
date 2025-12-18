Installation
============

This guide covers installing **cfxdb** in your Python environment.

Requirements
------------

* Python 3.9 or later
* CPython or PyPy

Installing from PyPI
--------------------

The recommended way to install cfxdb is from PyPI:

.. code-block:: bash

    pip install cfxdb

This will install cfxdb and its dependencies including zLMDB.

Installing from Source
----------------------

To install the latest development version:

.. code-block:: bash

    git clone https://github.com/crossbario/cfxdb.git
    cd cfxdb
    pip install -e .

Verifying Installation
----------------------

Verify the installation by checking the version:

.. code-block:: python

    import cfxdb
    print(cfxdb.__version__)

Dependencies
------------

cfxdb depends on:

* **zLMDB**: Object-relational database layer for LMDB
* **FlatBuffers**: Efficient serialization library
* **txaio**: Async networking compatibility layer
