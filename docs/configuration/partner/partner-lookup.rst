Partner look-up
===============

Works with bots>=3.0. Often there is a need to retrieve data from a partner, using a ``IDpartner``. Think of:

* check if partner is active
* get name/address of partner
* get senderID for partner

**Recipe**

Get the value in field ``attr1`` for the ``IDpartner``.
See partners in ``bots-monitor->Configuration->Partners`` for possible fields.

``transform.partnerlookup('buyer1','attr1',safe=True)``

Check if a partner exists, and is active. If not, raise an exception.

``transform.partnerlookup('buyer1','active')`` 

.. csv-table:: 
    :header: "Value for safe", "If a record matching your lookup does not exist, or the requested field is empty"

    "safe=False (default)","An exception is raised. You can check for this in your script if required and take action"
    "safe=True","No exception is raised, just returns the lookup value. eg: to lookup a user defined field for partner translation on some partners"
    "safe=None (Bots>=3.2)","No exception is raised, returns None. eg: to get address lines where not all partners have addresses, but this is not an error:"

.. rubric::
    Lookup using a field other than IDpartner

This is similar to reverse code conversion, but can look up any partner field and return any other partner field. Beware of performance issues if you have a large number of partners. Also there may be multiple matches if the lookup is not unique, only one is returned.

Get the value in field ``name`` by looking up value in ``attr2``.

``transform.partnerlookup('my attribute','name','attr2',safe=True)``

.. note::

    * In bots<3.0 this was possible using code conversion. But this could lead to situations where partners where both in bots-monitor->Configuration->Partners & groups and in code conversions.
    * Partners have more fields in bots>=3.0 like name, address, ``free`` fields.

Email addresses
---------------

* For email channels, you need to configure partners with their email addresses.
* Configure partners: ``bots-monitor->Configuration->Partners``.
* A partner can have a different email address per channel, if not the default eail addres is used.
* Is it needed to configure the partners because:

    * for incoming messages, to determine whether an email is from a valid sender. Email from unknown partners are errors (think of spam).
    * for outgoing message, to determine the destination address.

* Configuring a partner for email:

    * Configure a partner: ``bots-monitor->Configuration->Partners``.

