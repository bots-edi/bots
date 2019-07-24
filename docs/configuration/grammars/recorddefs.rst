Recorddefs
==========

.. epigraph::
    Definition: Recorddefs defines the layout of each record.

* Recorddefs is required, except for grammars for editypes ``templatehtml``, ``xmlnocheck``, ``jsonnocheck``.
* Recorddefs is a dictionary; key is record ID/tag, value is list of fields.
* There is **always** a field ``BOTSID`` in a record; mostly BOTSID is the first field (fixed format is the exception).

.. rubric::
    Some specifics for different editypes

* **edifact**: record ID is edifact tag (DTM, BGM, etc).
* **X12**: record ID is the segment identifier
* **Xml**: record ID is xml-tag (without angle brackets).
* **Fixed**: bots has to know where record ID is. Default: first three positions in record; this can be set with syntax parameters
* **Csv**: Csv/Excel does not always have a record ID (all records in an edi-file are of the same type). Bots uses the name of the record as BOTSID if you use syntax parameter: ``'noBOTSID':True``

.. rubric::
    Each field is a list of:

#. **field ID**: has to be unique (bots checks for this).
#. **M/C**: mandatory or conditional.
#. **length**: Examples:
    .. code-block:: python

        ['field name','C', 9, 'A'],       #max length
        ['field name','C', (3,9), 'A'],   #min length, max length. Use eg as:
        ['field name','C', (9,9), 'A'],   #field length should always be 9
        ['field name','C', 8.3, 'N'],     #length max 8 field, must have 3 decimals. 
#. format: Different per editype. Especially edifact, x12 and tradacoms have their own formatting codes, just use these. For csv, fixed, xml etc no standard formats exists, so bots uses these formats:
    * **A** (or AN): alphanumeric.
    * **AR**: right aligned alphanumeric (fixed only)
    * **N**: fixed decimals
        * Numeric
        * Fixed numbers of decimals. If no decimals are indicated: integer
        * Incoming: format is checked.
        * Outgoing: bots formats this (rounding if needed, add leading zeros)
    * **NL**: (for fixed only) as fixed decimals, left aligned, trailing blancs
    * **NR**: (for fixed only) as fixed decimals, right aligned, leading blancs
    * **R**: floating point
        * Numeric
        * May have any number of decimals
        * Bots does no checking of formatting.
    * **RL**: (for fixed only) as floating point, left aligned, trailing blancs
    * **RR**: (for fixed only) as floating point, left aligned, leading blancs
    * **I**: fixed decimals implicit. Example:
            * Numeric
            * Fixed number of decimals. Is converted from/to 'normal' amount; rounded if outgoing.
            * There is no decimal sign in the field, the number of decimals is implicit from the definition. Eg:
            * Can be negative
            * Example:
                .. code-block:: python

                    ['field name','C', 8.2, 'I'],   #max 8 long, last 2 positions are decimals; eg for an amount.
                                                    #Valid is eg:  12345
                                                    #Bots converts this to 123.45 (and vice versa)

    * **D** (or DT): date. Either 6 or 8 positions; format YYMMDD or CCYYMMDD. Bots checks for valid dates both in- en outgoing.
    * **T** (or TM): time. Either 4 or 6 positions; format HHMM or HHMMSS. Bots checks for valid times both in- en outgoing.

.. rubric::
    Composite fields

Edifact, x12 and tradacoms have composite fields. Example:

.. code-block:: python

    ['S005', 'C',                      #composite field
        [
        ['S005.0022', 'M', 14, 'AN'],  #subfield nr1
        ['S005.0025', 'C', 2, 'AN'],   #subfield nr2
        ]],

A composite has:

* field ID; has to be unique (bots checks for this).
* M/C (mandatory/conditional).
* A list of subfields.

.. note::
    Bots requires that each composite ID and sub-field has an unique ID. If a composite occurs more than once, do eg like:

    .. code-block:: python

        ['C090', 'C', [                        #composite contains 2 subfields with same ID
            ['C090.3286#1', 'M', 70, 'AN'],
            ['C090.3286#2', 'C', 70, 'AN'],
            ]],
        ['C542#1', 'M', [                      #composite occurs twice 
            ['C542.9425#1', 'M', 3, 'AN'],
            ['C542.9424#1', 'C', 35, 'AN'],
            ]],
        ['C542#2', 'C', [                      #composite occurs twice
            ['C542.9425#2', 'M', 3, 'AN'],
            ['C542.9424#2', 'C', 35, 'AN'],
            ]],

.. rubric::
    Details of field format handling

* M/C of fields are always checked.
* min/max length of field are always checked.
* numerical:
    * '-' is accepted both at beginning and end. Bots outputs only leading '-'
    * '+' is accepted at beginning. Bots does not output '+'
    * Thousands separators are removed if specified in syntax-parameter 'triad' (see above).
    * Bots does not output thousands separators
    * default decimal separator is '.'; use syntax-parameter 'decimaal' to change this ('decimaal' is Dutch, sorry about that. Noticed to late to change ;-)). Internally bots only uses/accepts decimal point!
    * (incoming) leading zeros are removed
    * (incoming) trailing zeros are kept
    * '.45' is converted to '0.45'.
    * '4.' is converted to '4'.
    * Note that eg edifact numeric lengths do NOT include decimal sign and negative...

.. rubric::
    Utility for positions in fixed records

A grammar does not contains the position/offset of each field in a fixed record, but it sure is useful to have this. Add this code to the bottom of the grammar and run/execute the code:

.. code-block:: python

    if __name__ == "__main__":
        for key, record in recorddefs.items():
            length = 0
            for field in record:
                print '           ', field, '      #pos',length+1, length + field[2]
                length += field[2]
            print 'Record',key,'  has length ',length, '\n'

Slightly different version - output can be pasted back into grammar

.. code-block:: python

    if __name__ == "__main__":
        space = 0
        for key, record in recorddefs.items():
            for field in record:
                space = max(space,len(str(field))+1)
        for key, record in recorddefs.items():
            length = 0
            print '    \'' + key + '\':['
            for field in record:
                print '           ', (str(field) + ',').ljust(space), ' # pos',length+1, '-', length + field[2]
                length += field[2]
            print '    ],'


