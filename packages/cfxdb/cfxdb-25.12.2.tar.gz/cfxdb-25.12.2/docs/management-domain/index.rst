Management Domain
=================

.. toctree::
    :maxdepth: 3

    user
    mrealm

---------

The domain controller running on the master node stores its configuration and run-time
information in an embedded database

All database tables and indexes can be accessed using the type information and
schema definitions from a single database schema class:

.. autoclass:: cfxdb.globalschema.GlobalSchema
    :members:
        attach,
        nodes,
        idx_nodes_by_pubkey,
        idx_nodes_by_authid,
        organizations,
        idx_organizations_by_name,
        idx_users_by_pubkey,
        idx_users_by_email,
        activation_tokens,
        idx_act_tokens_by_authid_pubkey,
        mrealms,
        idx_mrealms_by_name,
        users,
        users_mrealm_roles,
        usage

.. note::

    There exists only one domain controller database per master node. This database is separate
    from all managament realm controller databases, and only used to book keep users, Management
    realms and paired nodes. All configuration and management within a given management realm is
    then stored in the management realm controller database dedicated to the respective realm.

.. autoclass:: cfxdb.common.ConfigurationElement
    :members:
    :show-inheritance:
