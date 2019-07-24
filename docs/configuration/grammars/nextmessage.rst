Next Message
============

The ``nextmessage`` section of a grammar is used to split the messages in an edi-file; this way a mapping script receives one message at a time.
Example:

.. code-block:: python

    structure=    [
    {ID:'ENV',MIN:1,MAX:999,LEVEL:[         #envelope record     
        {ID:'HEA',MIN:1,MAX:9999,LEVEL:[    #header record
            {ID:'LIN',MIN:0,MAX:9999},      #line record
            ]},
        ]}
    ]

    nextmessage = ({'BOTSID':'ENV'},{'BOTSID':'HEA'})

Using this ``nextmessage`` the mapping script receives one HEA-record with the LIN-records under it.
The sender and receiver of the envelope can be accessed via QUERIES.
