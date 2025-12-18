Key Exchange
============

PaymentChannel
--------------

* :class:`cfxdb.xbrmm.PaymentChannel`
* :class:`cfxdb.xbrmm.PaymentChannels`
* :class:`cfxdb.xbrmm.IndexPaymentChannelByDelegate`
* :class:`cfxdb.xbrmm.PaymentChannelBalance`
* :class:`cfxdb.xbrmm.PaymentChannelBalances`

-------

.. autoclass:: cfxdb.xbrmm.PaymentChannel
    :members:
    :undoc-members:
        channel,
        market,
        sender,
        delegate,
        recipient,
        amount,
        timeout,
        state,
        open_at,
        closing_at,
        closed_at
    :member-order: bysource

.. autoclass:: cfxdb.xbrmm.PaymentChannels
    :members:
    :show-inheritance:

.. autoclass:: cfxdb.xbrmm.IndexPaymentChannelByDelegate
    :members:
    :show-inheritance:

.. autoclass:: cfxdb.xbrmm.PaymentChannelBalance
    :members:
    :undoc-members:
        remaining,
        inflight
    :member-order: bysource

.. autoclass:: cfxdb.xbrmm.PaymentChannelBalances
    :members:
    :show-inheritance:


Offer
-----

* :class:`cfxdb.xbrmm.Offer`
* :class:`cfxdb.xbrmm.Offers`
* :class:`cfxdb.xbrmm.IndexOfferByKey`

-------

.. autoclass:: cfxdb.xbrmm.Offer
    :members:
    :undoc-members:
        timestamp,
        offer,
        seller,
        seller_session_id,
        seller_authid,
        key,
        api,
        uri,
        valid_from,
        signature,
        price,
        categories,
        expires,
        copies,
        remaining
    :member-order: bysource

.. autoclass:: cfxdb.xbrmm.Offers
    :members:
    :show-inheritance:

.. autoclass:: cfxdb.xbrmm.IndexOfferByKey
    :members:
    :show-inheritance:
