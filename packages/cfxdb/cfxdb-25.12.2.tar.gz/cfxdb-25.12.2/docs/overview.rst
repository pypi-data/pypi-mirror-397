Introduction
============

**cfxdb** is a Crossbar.io Python support package with core database access
classes written in native Python.

What is cfxdb?
--------------

The package allows direct in-memory data access from Python programs
(including Jupyter notebooks) to CrossbarFX edge node data:

* Persisted WAMP event history
* Persisted router tracing data
* XBR market maker transactions database
* XBR network backend database
* WAMP session cache
* Custom user, embedded object databases

Built on zLMDB
--------------

cfxdb is built on top of `zLMDB <https://zlmdb.readthedocs.io/>`_, which provides
the object-relational mapping layer for LMDB, the lightning memory-mapped database.

Key Features
------------

* **High Performance**: Direct memory-mapped access to data
* **FlatBuffers Serialization**: Efficient binary serialization
* **Schema Definitions**: Typed database schemas for Crossbar.io
* **Python Native**: Pure Python implementation for CPython and PyPy

.. note::

    For the underlying database concepts and LMDB details, see the
    `zLMDB documentation <https://zlmdb.readthedocs.io/>`_.
