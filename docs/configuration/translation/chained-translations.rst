Chained Translations
====================

.. epigraph::

    Definition: chained translations translate one incoming format to multiple outgoing formats.

Example: Translate edi-order to in-house format AND send an email to inform sales representative.
To use this bots uses the ``alt``. How this works:

* receive incoming file
* do a translation (using mapping script)
* mapping script returns alt-value
* do another translation using the alt-value.

Background information: :doc:`TranslationRules how bots determines what to translate <whatwhen>`

**By example**

* Set up first translation rule (to csv-format) as usual:
    * Translate x12-850 to csv-orders using mapping script 850_2_csv
* At end of mapping script 850_2_csv:
  ``return 'do_email_translation'        #alt-value is returned``
* Set up the second translation rule:
  * translate x12-850 to csv-orders using mapping script 850_2_email **where alt=do_email_translation**

By returning the alt-value ``do_email_translation`` mapping script 850_2_csv triggers the 2nd translation (with mapping script 850_2_email).

**Plugin**

In plugin edifact_ordersdesadvinvoic on bots sourceforge site:

#. incoming is edifact orders.
#. translate fixed inhouse format.
#. translate to edifact APERAK/acknowledgement (if acknowledgement is asked).

**Details**

* Of course it is possible to 'chain' more than one translation.
* I have used this to do complex 'sorts' on incoming documents, eg:
    * write/sort to multiple outgoing messages sorting for destination of goods
    
.. note::    
    In this type of set-up multiple formats are outgoing, you'll want to use a composite route.

Special Chained Translations
----------------------------

You can also return an alt value that is a python dict. The dict must contain 'type' and 'alt' strings; there are several special types available for different processing requirements.

**out_as_inn**

Do chained translation: use the out-object as inn-object, new out-object.
Use cases:

#. Detected error in incoming file; use out-object to generate warning email.
#. Map inputs to standard format, also map standard format to human readable version (eg. html template)

Both out-objects are output by Bots and can be sent to same or different channels using channel filtering.

.. code-block:: python

    # if the first output is not needed to send somewhere, discard it
        # omit this step and you will get both outputs
        from bots.botsconfig import *
        out.ta_info['statust'] = DONE

        # use output of first mapping as input of second mapping
        return {'type':'out_as_inn','alt':'do_email_translation'}

**no_check_on_infinite_loop**

Do chained translation: allow many loops with same alt-value. 
Normally, Bots will detect and prevent this, by stopping after 10 iterations of the loop. You are disabling this safety feature, so your mapping script will have to handle this correctly to ensure the looping is not infinite.

.. code-block:: python

    # we MUST have a way to exit the loop!
    if (some condition):
        return

    # loop through this mapping multiple times...
    return {'type':'no_check_on_infinite_loop','alt':'repeat'}



