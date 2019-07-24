Put Data in Outgoing Message
============================

Use any of these functions to put data into an outgoing message:

put(mpath)
----------

* Places the field(s)/record(s) as specified in mpath in the outmessage.
* **Returns**: if successful, True, otherwise False.
* If mpath contains None-values (typically because a get() gave no result) nothing is placed in the outmessage, and put() returns False.

.. code-block:: python

    #put a message date in a edifact message
    out.put({'BOTSID':'UNH'},{'BOTSID':'DTM','C507.2005':'137','C507.2380':'20070521'}) 

**Explanation**: put date ``20070521`` in field C507.2380 and code ``137`` in field C507.2005 of DTM-record; DTM-record is nested under UNH-record.

putloop(mpath)
--------------

* Used to generate repeated records or record groups.
* **Recommended**: only use it as in: line = putloop(mpath)
* Line is used as line.put()
* Typical use: generate article lines in an order.
* **Note**: do not use to loop over every record, use put() with the right selection.

.. code-block:: python

    #loop over lines in edifact-order and write them to fixed in-house:
    for lin in inn.getloop({'BOTSID':'UNH'},{'BOTSID':'LIN'}):
        lou = out.putloop({'BOTSID':'HEA'},{'BOTSID':'LIN'})
        lou.put({'BOTSID':'LIN','REGEL':lin.get({'BOTSID':'LIN','1082':None})})
        lou.put({'BOTSID':'LIN','ARTIKEL':lin.get({'BOTSID':'LIN','C212.7140':None})})
        lou.put({'BOTSID':'LIN','BESTELDAANTAL':lin.get({'BOTSID':'LIN'},
                                    {'BOTSID':'QTY','C186.6063':'21','C186.6060':None})})

.. warning::

    Never use 2 inn.get's in one out.put (unless you really know what you are doing ;-)

    .. code-block:: python

        out.put({'BOTSID':'ADD','7747':inn.get('BOTSID':'HEA','name1':None),'7749':inn.get('BOTSID':'HEA','name2':None)})}

    **Because**: if either name1 or name2 is not there (empty, None) nothing will be written in this statement.
