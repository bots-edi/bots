Change and Delete Functions
===========================

**delete(mpath)**

* Delete(s) the record(s) as specified in mpath in the outmessage (and the records **under** that record).
* After deletion, searching stops (if more than one records exists for this mpath, only the first one is deleted). 
* For deleting all records (repeating records) use getloop() to access the loop, and delete within the loop.

**Returns**: if successful, True, otherwise False.

.. code-block:: python

    #delete a message date in a edifact INVOICD96AUNEAN008:
    out.delete({'BOTSID':'UNH'},{'BOTSID':'DTM','C507.2005':'137'}) 
    #delete DTM record where field C507.2005 = '137' ; DTM-record is nested under UNH-record.

.. code-block:: python

    #delete all ALC segments in edifact message:
    while message.delete({'BOTSID':'UNH'},{'BOTSID':'ALC'}):
        pass

.. note::
    If you want to delete a field, you can use the change option and put as value **None**

    .. code-block:: python

        lot = lin.get({'BOTSID':'line','batchnumber':None})
        if not lot == None:
            lin.change(where=({'BOTSID':'line','batchnumber':lot},),change={'batchnumber':None})
        #In this case I want to remove a wrong batchnumber from a specific supplier

**change(where=(mpath),change=mpath)**

* Used to change an existing record. 'where' identifies the record, 'change' are the values that will be changed (or added is values do not exist) in this record.
* Only one record is changed. This is always the last record of the where-mpath
* After change, searching stops (if more than one records exists for this mpath, only the first one is changed). 
* For changing all records (repeating records) use getloop() to access the loop, and change within the loop.

.. code-block:: python

    inn.change(where=({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'DP'}),change={'3035':'ST'}) 
    #changed qualifier 'DP' in NAD record to 'ST'

.. note::
    ``where`` must be a tuple; if you want to change the root of document, add a comma to make it a tuple.

    .. code-block:: python

        inn.change(where=({'BOTSID':'UNH'},),change={'S009.0054':'96A'})
        #                                 ^ note comma here
