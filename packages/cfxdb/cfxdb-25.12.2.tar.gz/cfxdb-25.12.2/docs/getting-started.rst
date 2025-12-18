Getting Started
===============

This guide will help you get started with **cfxdb** for accessing
Crossbar.io database schemas.

Prerequisites
-------------

Before you begin, ensure you have:

* Python 3.9 or later installed
* cfxdb installed (see :doc:`installation`)
* Basic familiarity with LMDB concepts

Basic Usage
-----------

Here's a simple example of using cfxdb:

.. code-block:: python

    import cfxdb
    from zlmdb import Database

    # Open a database
    db = Database(dbpath='/path/to/database')

    # Work with cfxdb schemas
    # (specific examples depend on your use case)

Database Schemas
----------------

cfxdb provides database schemas for various Crossbar.io features:

* **Router Database**: Session and message data
* **Management Realm**: Realm configuration
* **Management Domain**: Domain-level settings
* **Management Network**: Network topology data

See the :doc:`programming-guide/index` for detailed information
about each schema.

Next Steps
----------

* Read the :doc:`programming-guide/index` for in-depth coverage
* Explore the API Reference for detailed class documentation
* Check the `zLMDB documentation <https://zlmdb.readthedocs.io/>`_
  for underlying database concepts
