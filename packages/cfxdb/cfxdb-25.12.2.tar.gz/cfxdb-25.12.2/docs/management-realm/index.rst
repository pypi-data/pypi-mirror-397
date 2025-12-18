Management Realms
=================

.. toctree::
    :maxdepth: 3

    arealm
    routercluster
    webcluster
    logs

---------

Each management realm controller running on the master node stores its configuration and run-time
information in an embedded database.

All database tables and indexes can be accessed using the type information and
schema definitions from a single database schema class:

.. autoclass:: cfxdb.mrealmschema.MrealmSchema
    :members:
    :undoc-members:

.. note::

    Each management realm has its own dedicated management realm controller database. This database
    is separate for each management realm and not accessed by any other management realm controller.
