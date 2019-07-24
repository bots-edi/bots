What Translation When?
======================

Bots figures out what translation to use via the translation rules. Best is to think of the translation rules as a ``lookup`` table:

    look-up with (from-editype, from-messagetype, alt, frompartner and topartner) to find mappingscript, to-editype and to-messagetype

How the input values for the look-up are determined:

#. editype
    * configured in the route
    * if you configure editype=mailbag, bots will figure out if editype is x12, edifact or tradacoms.
#. messagetype can be:
    * configured in the route, eg for editype csv
    * for edifact, x12 and tradacoms: bots figures out the detailed messagetype. Example:
    * in route: editype: edifact, messagetype: edifact
    * in incoming edi file bots finds detail messagetype **ORDERSD96AUN**.
#. frompartner can be:
    * configured in the route
    * determined by the grammar using `QUERIES <../grammars/structure.html#queries>`_
#. topartner can be:
    * configured in the route
    * determined by the grammar using `QUERIES <../grammars/structure.html#queries>`_
#. alt can be:
    * configured in the route
    * determined by the grammar using `QUERIES <../grammars/structure.html#queries>`_
    * set by mapping script in a :doc:`chained translation <chained-translations>`

.. note::

    * For frompartner and topartner: bots finds the most specific translation.
        * Eg example with 2 translation rules:
            * fromeditype = edifact, frommessagetype = ORDERSD96AUNEAN008
            * fromeditype = edifact, frommessagetype = ORDERSD96AUNEAN008, frompartner=RETAILERX
        * If bots receives an ORDERS message from RETAILERX, the 2nd translation is used.
        * For other partners the first translation is used.
    * for alt-translations: only find the translation with that specific **alt**.
