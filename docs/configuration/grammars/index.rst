Grammars
========

.. epigraph::

    Definition: A grammar is a description of an edi-message.

* A grammar describes the records, fields, formats etc of an edi file.
* Bots uses grammars to parse, check and generate edi files.
* Grammars files are independent of the editype: a grammar for a csv files looks the same as a grammar for a x12 file.
* Grammar files are in: usersys/grammars/editype/grammar name.py

.. rubric::
    Learn grammar by example

Best way to get the idea of a grammar is to look at the (simple) example in the chapter. Consider the below CSV file:

.. code:: 

    HEADER,ordernumber1,buyer1,20120524
    LINE,1,article1,24,description1
    LINE,2,article2,288,
    LINE,3.article3,6,description3

The corresponding grammer for this file would be:

.. code-block:: python

    from bots.botsconfig import *        #always needed
 

    syntax = {                           #'syntax' section
         'field_sep' : ',',               #specify field separator
         'charset'   : 'utf-8',           #specify character-set
         }
 

    structure = [                        #'structure' section
     {ID:'HEADER',MIN:1,MAX:999,LEVEL:[   #each order starts with a HEADER record     
         {ID:'LINE',MIN:1,MAX:9999},      #nested under the HEADER record are the LINE records, repeat up to 9999 times
         ]}
     ]
 

    recorddefs = {                       #'recorddefs' section
     'HEADER':[                           #specify the fields in the HEADER record
         ['BOTSID','M',6,'A'],            #BOTSID is for the HEADER tag itself 
         ['order number', 'M', 17, 'AN'], #for each field specify the format, max length, M(andatory) or C(onditional)
         ['buyer ID', 'M', 13, 'AN'],
         ['delivery date', 'C', 8, 'AN'],
         ],
     'LINE':[
         ['BOTSID','M',6,'A'],
         ['line number', 'C', 6, 'N'],
         ['article number', 'M', 13, 'AN'],
         ['quantity', 'M', 20, 'R'],
         ['description', 'C', 70, 'R'],
         ],
     }

The example above is simple, but fully functional.

.. rubric::
    Sections of a grammar

A grammar file consists of these sections:

* *syntax*: parameters for the grammar like field separator, merge or not, indent xml, etc.
* *structure*: sequence of records in an edi-message: start-record, nested records, repeats.
* *recorddefs*: fields per record.
* *nextmessage*: to split up an edi file to separate messages.
* *nextmessageblock*: to split up a cvs-file to messages.

A section can be reused/imported from another grammar file. Purpose: better maintenance of grammars.
Example: edifact messages from a certain directory use the same recorddefs/segments:

``from recordsD96AUN import recorddefs``

One edifact grammar consists of four parts. Example:

* edifact.py (contains syntax common to all edifact grammars)
* envelope.py (contains envelope structure and recorddefs common to all edifact grammars)
* recordsD96AUN.py (contains recorddefs common to all edifact D96A grammars)
* ORDERSD96AUN.py (contains structure specifically for ORDERS D96A)

.. rubric::
    Problems for some edifact grammars on sourceforge site

Sometimes you might meet this error for a grammar:

``GrammarError: Grammar "...somewhere...", in structure: nesting collision detected at record "etc etc".``

* This is the case eg with INVRPT D96A.
* UN says about this that you have to make additional choices in message; either you make some segments mandatory or leave out some segment groups.
* EANCOM did make such choices in their implementation guidelines.
* So: you can not the grammar directly, edit it according to your needs. This is according to what UN-edifact wants...

.. rubric::
    Index

.. toctree::
    :maxdepth: 2

    get-grammars
    syntax-params
    structure
    recorddefs
    nextmessage
    nextmessageblock
    edifact-charsets
    xml-namespaces


