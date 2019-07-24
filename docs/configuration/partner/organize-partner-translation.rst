Organize Partner Specific Translations
======================================

Often in edi you need a number of very similar translations for different partners - the **many similar yet different mappings** problems.
You want to organize your mapping scripts so that code is not duplicated many times, creating maintenance problems.
A nice approach is:

#. Create a default mapping.
#. For some partners you can use the default mapping, for others use a :doc:`partner specific translation <partner-translation>`
#. The partner-specific mappings import the default mapping and builds upon that (additional pre- or post-mapping).

.. note::
    Plugin 'demo_partnerdependent' at the `bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_ demonstrates partner-groups.

.. rubric::
    Consider the below example

The **default mapping** script file 'orders2idoc.py', translates edifact ORDERS to idoc ORDERS05)

.. code:: python

    def main(inn,out):
        # Order number
        out.put({'BOTSID':'EDI_DC40'},{'BOTSID':'E1EDK01'},{'BOTSID':'E1EDK02','QUALF':'001',
                                       'BELNR':inn.get({'BOTSID':'UNH'},{'BOTSID':'BGM','C106.1004':None})})

        # Buyer name
        out.put({'BOTSID':'EDI_DC40'},{'BOTSID':'E1EDK01'},{'BOTSID':'E1EDKA1','PARVW':'AG',
                                       'BNAME':inn.get({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'BY','C056.3412':None})})

        # blahblahblah.....lots more complex mapping code for the order

The **partner specific mapping** script file 'customer2_orders2idoc.py' for a **customer 2**.
The default mapping is mostly OK, but a few changes are needed:

.. code:: python

    import orders2idoc             #here the default mapping is imported

    def main(inn,out):
        #*** pre-mapping *******************
        # do partner-specific mapping before the default mapping eg to make the incoming order "more standard" :-)
        # In this example:
        #     customer2 sends RFF+PR:BULK to indicate a stock order. Delete this and change to BGM+120
        #     This must be done pre-mapping because we have complex mapping rules based on BGM order type.
        if inn.get({'BOTSID':'UNH'},{'BOTSID':'RFF','C506.1153':'PR','C506.1154':None}) == 'BULK':
            inn.delete({'BOTSID':'UNH'},{'BOTSID':'RFF','C506.1153':'PR','C506.1154':'BULK'})
            inn.change(where=({'BOTSID':'UNH'},{'BOTSID':'BGM'}),change={'C002.1001':'120'})


        #*** run the default mapping******************
        orders2idoc.main(inn,out)


        #*** post-mapping *******************
        # Post-mapping to adjust or add to the mapped output.
        # Delete unwanted text that is sent on their orders
        out.delete({'BOTSID':'EDI_DC40'},{'BOTSID':'E1EDK01'},{'BOTSID':'E1EDKT2','TDLINE':'TOTAL EXCL. GST AUD'})
        # Additional mapping: map buyer name from NAD+AB:
        out.put({'BOTSID':'EDI_DC40'},{'BOTSID':'E1EDK01'},{'BOTSID':'E1EDKA1','PARVW':'AG',
                'BNAME':inn.get({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'AB','C056.3412':None})})

.. note::
    * Make the default mapping is as generic as possible (eg. checking multiple fields).
    * Do not not put any partner specific implementation mapping in here
    * All mapping scripts are in the same directory (for the incoming editype)

