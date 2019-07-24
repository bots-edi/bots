Next Message Block
==================

* The ``nextmessageblock`` section in a grammar is mostly used for csv-files consisting of one record-type.
* Think of excel, where every row has the same layout.
* Via nextmessageblock all subsequent records with eg the same ordernumber are passed as one message to the mapping script.
* This is best understood by an example, consider the below CSV file:

.. code:: 

    ordernumber1,buyer1,20120524,1,article1,24
    ordernumber1,buyer1,20120524,2,article2,288
    ordernumber1,buyer1,20120524,3.article3,6
    ordernumber2,buyer2,20120524,1,article5,124
    ordernumber3,buyer1,20120524,1,article1,24
    ordernumber3,buyer1,20120524,2,article4,48

which will have the grammer:

.. code-block:: python

    from bots.botsconfig import *

    syntax = { 
        'field_sep' : ',',               #specify field separator
        'noBOTSID'   : True,             #does not have record-ID's
        }

    nextmessageblock = ({'BOTSID':'HEADER','order number':None})   #feed mapping script with separate orders (where ordernumber is different)

    structure = [             
    {ID:'HEADER',MIN:1,MAX:9999}         #only 1 record-type
    ]

    recorddefs = {
    'HEADER':[    
        ['BOTSID','M',6,'A'],            #Note: BOTSID is ALWAYS needed!
        ['order number', 'M', 17, 'AN'],
        ['buyer ID', 'M', 13, 'AN'],
        ['delivery date', 'C', 8, 'AN'],
        ['line number', 'C', 6, 'N'],
        ['article number', 'M', 13, 'AN'],
        ['quantity', 'M', 20, 'R'],
        ],
    }

The mapping script in the translation receives 3 separate orders (so mapping script will run 3 times):

.. code::

    order with number 1:
    ordernumber1,buyer1,20120524,1,article1,24
    ordernumber1,buyer1,20120524,2,article2,288
    ordernumber1,buyer1,20120524,3.article3,6

    order with number 2:
    ordernumber2,buyer2,20120524,1,article5,124

    order with number 3:
    ordernumber3,buyer1,20120524,1,article1,24
    ordernumber3,buyer1,20120524,2,article4,48

.. note::
    Use multiple fields for splitting up (bots > 3.1); Example:
    ``nextmessageblock = ([{'BOTSID':'HEADER','order number':None},{'BOTSID':'HEADER','buyer ID':None}])``

.. note::
    ``nextmessageblock`` works for fixed files with one type of records (bots > 3.1)
