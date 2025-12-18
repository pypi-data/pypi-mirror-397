Realm Store
===========

.. contents:: :local:

-------------

RealmStore
----------

.. autoclass:: cfxdb.realmstore.RealmStore
    :members:

-------------

Session
-------

* :class:`cfxdb.realmstore.Session`
* :class:`cfxdb.realmstore.Sessions`
* :class:`cfxdb.realmstore.IndexSessionsBySessionId`

-------

.. autoclass:: cfxdb.realmstore.Session
    :members:
    :undoc-members:
        session,
        joined_at,
        left_at,
        realm,
        authid,
        authrole
    :member-order: bysource

.. autoclass:: cfxdb.realmstore.Sessions
    :members:
    :show-inheritance:

.. autoclass:: cfxdb.realmstore.IndexSessionsBySessionId
    :members:
    :show-inheritance:


Publication
-----------

* :class:`cfxdb.realmstore.Publication`
* :class:`cfxdb.realmstore.Publications`

-------

.. autoclass:: cfxdb.realmstore.Publication
    :members:
    :undoc-members:
        timestamp,
        publication,
        publisher,
        topic,
        args,
        kwargs,
        payload,
        acknowledge,
        retain,
        exclude_me,
        exclude,
        exclude_authid,
        exclude_authrole,
        eligible,
        eligible_authid,
        eligible_authrole,
        enc_algo,
        enc_key,
        enc_serializer
    :member-order: bysource

.. autoclass:: cfxdb.realmstore.Publications
    :members:
    :show-inheritance:


Event
-----

* :class:`cfxdb.realmstore.Event`
* :class:`cfxdb.realmstore.Events`

-------

.. autoclass:: cfxdb.realmstore.Event
    :members:
    :undoc-members:
        timestamp,
        subscription,
        publication,
        receiver,
        retained,
        acknowledged_delivery
    :member-order: bysource

.. autoclass:: cfxdb.realmstore.Events
    :members:
    :show-inheritance:
