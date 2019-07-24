Document View
=============

Bots focuses mostly on edi files. Another useful way of looking at edi is to view at **business documents**: orders, asn's, invoices etc.

Bots support this, but to have this work satisfactory some configuration needs to be done. Essential is the use of document numbers (eg order number, shipment number, invoice number); in bots this is called ``botskey``.

.. rubric::
    Usage

Once ``botskey`` is set correct for your documents, it can be used for:

* Viewing and searching business documents:
    * View last run: ``bots-monitor->Last run->Document``
    * View all runs: ``bots-monitor->All run->Document``
    * Select/search for documents: ``bots-monitor->Select->Document``
* Set output :doc:`file name in a channel <channel/filenames>` or in a :doc:`communicationscript <channel/channel-scripting>`


.. rubric::
    Configure botskey

This can be done in two ways:

#. Using QUERIES in the :doc:`grammar <grammars/index>` of the incoming edi file.

    .. code-block:: python

        # Example: botskey in a simple csv grammar
        structure = [
            {ID:'LIN',MIN:1,MAX:99999,
                QUERIES:{
                    'frompartner': ({'BOTSID':'LIN','AccountCode':None}),
                    'topartner':   ({'BOTSID':'LIN','CustomerCode':None}),
                    'botskey':     ({'BOTSID':'LIN','PurchaseOrderNo':None}),
                },
            }
        ]

#. In your :doc:`mapping script <mapping-scripts/index>` 

    .. code-block:: python

        out.ta_info['botskey'] = inn.get({'BOTSID':'LIN','PurchaseOrderCode':None})
