Mapping Functions
=================

Bots provides a set of helper functions out of the box to ease the map development. Let us see the available functions:

sort(mpath)
-----------

Sorts the incoming message according to certain value.
Sorts alphabetically.

.. code-block:: python

    inn.sort({'BOTSID':'UNH'},{'BOTSID':'LIN','C212.7140':None}) 
    #sort article lines by EAN article number (GTIN).

transform.useoneof(first get, second get, etc)
----------------------------------------------

Use for default values or when data can be in different places in a message.

.. code-block:: python

    value = transform.useoneof(inn.get({'BOTSID':'IMD','C960.4294':None}),inn.get({'BOTSID':'IMD','7078':None})) 
    #returns the result of the first get() that is succesful.
    #remarked was that this is simular to:
    value = inn.get({'BOTSID':'IMD','C960.4294':None}) or inn.get({'BOTSID':'IMD','7078':None})
    #Usage for default values (if field not there, use default): 
    value = inn.get({'BOTSID':'IMD','C960.4294':None}) or 'my value'

transform.datemask(value,frommask,tomask)
-----------------------------------------

* Does format conversions based upon pattern matching.
* Especially useful for date/time conversion.
* **Note**: only simple pattern matching, without 'intelligence' about date/time.

.. code-block:: python

    transform.datemask('09/21/2011','MM/DD/CCYY','YY-MM-DD') 
    #returns '11-09-21'

* Funny trick with datamask:

.. code-block:: python

    print transform.datemask('201512312359','YYYYmmDD0000','YYYYmmDD0000')
    print transform.datemask('201512310000','YYYYmmDD0000','YYYYmmDD0000')
    print transform.datemask('20151231','YYYYmmDD0000','YYYYmmDD0000')
    #returns date always in CCYYmmDDHHMM, if no tiem in original tiem is '0000'

transform.concat(\*args)
------------------------

Concatenate a list of strings. If argument is None, nothing is concatenated.

.. code-block:: python

    transform.concat('my',None','string') 
    #returns 'mystring'

transform.sendbotsemail(partner,subject,reporttext)
---------------------------------------------------

* Send a simple email message to any bots partner (in partner-table) from a mapping script.
* Mail is sent to all To: and cc: addresses for the partner (but send_mail does not support cc).
* Email parameters are in config/settings.py (EMAIL_HOST, etc).

.. code-block:: python

    transform.sendbotsemail('buyerID1','error in messsge','There is an error in message blahblah')

transform.unique(domain)
------------------------

* Returns counter/unique number.
* For each **domain** separate counters are used.
* Counter start at **1** (at first time you use counter).
* The counter can be changed in ``bots-monitor->SysTasks->view/edit counters``

.. code-block:: python

    transform.unique('my article line counter') 
    #returns a number unique for the domain 'my article line counter'

transform.unique_runcounter(domain))
------------------------------------

* Returns counter/unique number during the bots-run.
* For each **domain** separate counters are used.
* Counter start at **1** (at first time you use counter).
* In a next run the counter will start again at **1**.
* Useful for eg a message-counter per interchange.

transform.inn2out(inn,out)
--------------------------

Use the incoming message as the outgoing message.
Is useful to translate the message one-on-one to another editype.
Examples:

* Edifact to flat file. This is what a lot of translators do.
* x12 to xml. x12 data is translated to xml syntax, semantics are of course still x12
* Another use: read a edi message, adapt, and write (to same editype/messagetype including changes).
