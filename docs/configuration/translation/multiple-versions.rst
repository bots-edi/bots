Multiple EDI Versions
=====================

There are several situations where you need to send different versions of messages and receive different versions of an EDI standard. 
In real world versions are often so similar that the same mapping script can be used (or a simple if-then can cater for the differences).
We can handle such requirements using any of the below solutions:

**Send multiple versions using partners**

    Use the ``topartner`` to determine the right version to send.

    * One grammar for in-house message:
        * myinhouseorder.py
        * This grammar uses QUERIES to extract 'topartner'.
    * Grammars for both the EDI versions:
        * ORDERSD93AUN
        * ORDERSD96AUN
    * 2 translation rules:
        * fixed-myinhouseorder to edifact-ORDERSD93AUN using mapping script ordersfixed2edifact93.py for topartner=XXX
        * fixed-myinhouseorder to edifact-ORDERSD96AUN using mapping script ordersfixed2edifact93.py for topartern=YYY

**Send multiple versions using ``alt``**
    
    Information about the version is in in-house-message: a field that contains either '93' or '96'.

    * one grammar for in-house message:
        * myinhouseorder.py
    * Grammars for both the EDI versions:
        * ORDERSD93AUN
        * ORDERSD96AUN
    * 2 translation rules
        * fixed-myinhouseorder to edifact-ORDERSD93AUN using mapping script orders_fixed2edifact93.py for alt=93
        * fixed-myinhouseorder to edifact-ORDERSD96AUN using mapping script orders_fixed2edifact93.py for alt=96

**Receive Multiple Versions**

    * Grammars for both the EDI versions:
        * ORDERSD93AUN
        * ORDERSD96AUN
    * one grammar for in-house message:
        * myinhouseorder.py
        * This grammar uses QUERIES to extract 'alt'-value.
    * 2 translation rules
        * edifact-ORDERSD93AUN to fixed-myinhouseorder using mapping script orders_edifact93_2_fixed.py
        * edifact-ORDERSD6AUN to fixed-myinhouseorder using mapping script orders_edifact96_2_fixed.py

