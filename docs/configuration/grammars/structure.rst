Structure
=========

.. epigraph::
    Definition: the structure section in a grammar defines the sequence of records in a message.

A structure is required in a grammar except for template grammars.
Example of a simple structure:

.. code-block:: python

    structure = [
    {ID:'ENV',MIN:1,MAX:999, LEVEL:[        #envelope record
        {ID:'HEA',MIN:1,MAX:9999,LEVEL:[    #header record
            {ID:'LIN',MIN:0,MAX:9999},      #line record
            ]},
        ]}
    ]

The example above should be read as:

    * ENV-record is required; max 999 repeats.
    * 'Nested' under the ENV-record: HEA-record; per ENV max 9999 HEA-records; min is 1, so required.
    * Per HEA-record max 9999 LIN-records; the LIN-record is not required (MIN=0).

Example of a more elaborate structure:

.. code-block:: python

    structure = [
    {ID:'ENV',MIN:1,MAX:1, LEVEL:[        #envelope record: max one per file
        {ID:'HEA',MIN:1,MAX:9999,LEVEL:[  #header record of messageat least one message per ENV, max 9999 messages
            {ID:'PAR',MIN:2,MAX:10},      #party record
            {ID:'ALC',MIN:0,MAX:9},       #allowances/charges per message
            {ID:'LIN',MIN:0,MAX:9999},    #line record
            ]},
        {ID:'TRL',MIN:1,MAX:1},           #each ENV record has a trailer record
        ]}
    ]

.. rubric::
    A structure consists of

#. A structure is a nested list of records.
#. Each record is a python dict.
#. Per Record:
    * **ID**: tag of record.
    * **MIN**: minimum number of occurrences.
    * **MAX**: maximum number of occurrences.
    * **LEVEL** (optional): indicate nested record. The nested records are in a list of records.
    * **QUERIES** (optional)
    * **SUBTRANSLATION** (optional). Very advanced. Purpose: identify separate messages within within a standard envelope.

QUERIES
-------

QUERIES in a structure are used to extract values from edi files before the mapping script starts.
Example of an structure with QUERIES:

.. code-block:: python

    structure = [
    {ID:'ENV',MIN:1,MAX:999,                #envelope record
        QUERIES:{
            'frompartner':  {'BOTSID':'ENV','sender':None},   #extract sender from ENV record.
            'topartner':    {'BOTSID':'ENV','receiver':None}, #extract receiver from ENV record.
            'testindicator':({'BOTSID':'ENV'},{'BOTSID':'MESSAGE','test':None}), #extract testindicator from 'deeper' level; note that this is in tuple (with brackets).
            },
        LEVEL:[         
        {ID:'HEA',MIN:1,MAX:9999,LEVEL:[    #header record
            {ID:'LIN',MIN:0,MAX:9999},      #line record
            ]},
        ]}
    ]

Use cases of the information extracted by QUERIES: Think of frompartner, topartner, reference, testindicator etc.

#. To choose the right translation (QUERIES can extract frompartner, topartner, alt)
#. Update the database.
#. In a mapping script this information is inn.ta_info'.
#. Data in the envelope can be accessed in the mapping.
#. One of the most import uses is the extraction of **botskey**.
#. Typical information extracted by QUERIES:
    * frompartner
    * topartner
    * reference
    * testindicator
    * botskey
    * alt

.. rubric::
    QUERIES using multiple values (concatenated)

Pass a list into the QUERIES, and the values returned will be concatenated.

.. code-block:: python

    QUERIES:{
        'botskey': [ ({'BOTSID':'UNH'},'BOTSID':'BGM','C002.1001':None}), ({'BOTSID':'UNH'},'BOTSID':'BGM','1004':None})],
    }

.. rubric:: 
    QUERIES using a function

Sometimes you might need something more complex, eg. to extract a substring or do partner lookup and transformation. You can add a function in the grammar to do this and call it in QUERIES.

.. code-block:: python

    # frompartner needs some transformation...
    import bots.transform as transform
    def get_frompartner(thisnode):
         partner = thisnode.get({'BOTSID':'invoice','supplier':None})
         new_partner = transform.partnerlookup(partner,'attr1',safe=True)
         return new_partner

    structure = [
    {ID:'envelope',MIN:0,MAX:99999,LEVEL:[
         {ID:'invoice',MIN:0,MAX:99999,
             QUERIES:{
                 'frompartner': get_frompartner,
                 },
             LEVEL:[
                 {ID:'line',MIN:0,MAX:99999}, 
