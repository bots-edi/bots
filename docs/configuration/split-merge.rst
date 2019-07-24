Split, Merge and Envelope
=========================

* The advised way of working with bots is to have a translation work with a message (x12: transaction).
* In edi an incoming file will often have multiple messages.
* And often you will have to have multiple outgoing messages in one edi-file (merging, enveloping).

Splitting EDI files
-------------------

One edi-file can contain several edi-message. Eg:

* one edifact file, multiple ORDERs.
* one x12 file, multiple 850's.
* export routine of your ERP software puts all exported invoices in one file
* email with multiple edi-attachments

A bots mapping works best for one message (one order, one invoice).
So Bots splits up edi-files:

* Incoming email: different attachments are saved as a separate edi-files.
* Receiving zipped edi files: the files in the zip-file as saved as separate edi-files.
* For edifact, x12, tradacoms: interchanges are being split up to separate files.
* Incoming edi-files are being fed to the mapping-script as messages. This is done by :doc:`nextmessage <grammars/nextmessage>` in the grammar syntax.
* Spit within a mapping script. Think of eg splitting up a shipment to the different orders. There are 2 ways of doing this:
    #. Write multiple message to the same file .
    #. Write each generated message to the same file, using alt translations.

Merge/Envelope EDI message
--------------------------

Reasons to merge/envelope edi files:

* Your ERP-system expects one file (message-queue) with fixed records
* Your edi-partners wants to limit the number of edi-files/interchanges received.
* costs: this can reduce transmission costs for some VAN's
* It is better to have one file with outgoing invoices than 165 separate files ;-)

Merge options:

* **Merging**: if the 'merge' parameter is set in the syntax of the outgoing message, bots will try to merge seperate messages to one file. Messages are only merged if: same from-partner, same to-partner, same editype, same messagetype, same testindicator, same characterset, same envelope.
* **Enveloping**: (edifact, x12, tradacoms) bots will envelope these messages (add UNB-UNZ for edifact, ISA-GS-GE-IEA for x12). Enveloping is independent from merging: bots can envelope without merging, or merge without enveloping.
* Write to a message-queue in outgoing channel: if you use a fixed filename in an outgoing channel, bots will append all messages to this file. This is often used in eg a configuration where all orders go to one file containing all incoming orders in fixed file format.

Envelope Scripting
------------------

You can use an envelopescript to do custom enveloping for edifact, x12, tradacoms, xml. Exit points that can be used:

#. ta_infocontent(ta_info)
    * At start of enveloping process. ta_info cotains the values that are used to write the envelope; you can change these values.
#. envelopecontent(ta_info,out)
    * after bots has built the envelope tree you can make changes to the envelope tree by using put(), change() etc.

Functions should be in ``bots/usersys/envelopescripts/<editype>/<editype>.py``, eg:

* ``bots/usersys/envelopescripts/edifact/edifact.py``
* ``bots/usersys/envelopescripts/x12/x12.py``

**Example 1**

Note that this affects all outgoing edifact documents. Add conditional logic if needed. In file ``bots/usersys/envelopescripts/edifact/edifact.py``:

.. code-block:: python

    def envelopecontent(ta_info,out,*args,**kwargs):
        ''' Add extra fields to the edifact envelope.'''
        out.put({'BOTSID':'UNB','S002.0008': 'PARTNER1'}) #Interchange sender internal identification
        out.put({'BOTSID':'UNB','S003.0014': 'PARTNER2'}) #Interchange recipient internal identification
        out.put({'BOTSID':'UNB','0029': 'A'})             #Processing priority code
        out.put({'BOTSID':'UNB','0032': 'EANCOM'})        #Interchange agreement identifier

**Example 2**

In file ``bots/usersys/envelopescripts/edifact/edifact.py``:

.. code-block:: python

    def ta_infocontent(ta_info,*args,**kwargs):
        ''' function is called before envelope tree is made.
            values in ta_info will be used to create envelope.
        '''
        if ta_info['topartner'] == '1111111111111':
            ta_info['topartner'] = 'XXXXXXXXXXXXXXXXX'
            ta_info['UNB.S003.0014'] = '012345'

**Example 3**

In file ``bots/usersys/envelopescripts/edifact/edifact.py``:

.. code-block:: python

    def envelopecontent(ta_info,out,*args,**kwargs):
        ''' function is called after envelope tree is made, but not written yet.
            manipulate envelope tree itself.
        '''
        if ta_info['topartner'] == '1111111111111':
            out.change(where=({'BOTSID':'UNB'},),change={'S003.0010': 'XXXXXXXXXXXXXXXXX'}) #field S003.0010 (receiver) is written to envelope tree
            out.put({'BOTSID':'UNB','S003.0014': '012345'}) #field S003.0014 is written to envelope tree
            ta_info['topartner'] = 'XXXXXXXXXXXXXXXXX'      #takes only care of changing the partnerID in bots interface (does not change envelope itself)
