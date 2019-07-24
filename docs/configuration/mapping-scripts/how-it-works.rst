How Mapping Works
=================

**Explained in the below example**

.. code-block:: python

    #this mapping script maps an incoming edifact message to a fixed record file.
    #bots calls the 'main' function in this mapping script

    def main(inn,out):
        #inn: the object for the incoming message; via get() and getloop() the content of the message can be accessed.
        #out: the object for the outgoing message; via put() and putloop() content is written for this message.

        ordernumber = inn.get({'BOTSID':'UNH'},{'BOTSID':'BGM','1004':None})  #get the order-number. 
                                                                              #The order-number is in field '1004' of record BGM. 
                                                                              #Record BGM is nested under record UNH.
        out.put({'BOTSID':'HEA','ORDERNUMBER':ordernumber})                   #put the order-number in the outgoing fixed message, field 'ORDERNUMBER' in record HEA.


        #We first did a get(), than a put(). This can be done in one line:
        out.put({'BOTSID':'HEA','ORDERTYPE':inn.get({'BOTSID':'UNH'},{'BOTSID':'BGM','C002.1001':None})})


        #There can be several dates, all in a DTM record. 
        #The 'qualifier' determines the type of date. 
        #Fetch the dates like this: 
        out.put({'BOTSID':'HEA','ORDERDATE':inn.get({'BOTSID':'UNH'},{'BOTSID':'DTM','C507.2005':'137','C507.2380':None})})     #get statement ONLY looks for DTM with qualifier 137
        out.put({'BOTSID':'HEA','DELIVERY_DATE':inn.get({'BOTSID':'UNH'},{'BOTSID':'DTM','C507.2005':'2','C507.2380':None})})
        #please note: no looping over the DTM-records, just get the data!

        #The orderlines are in a LIN-recordgroup; so we want each line in its own fixed LIN-record.
        #start looping the lines (LIN-segments) in the incoming message:
        for lin in inn.getloop({'BOTSID':'UNH'},{'BOTSID':'LIN'}):
            #write a fixed LIN record:
            lou = out.putloop({'BOTSID':'HEA'},{'BOTSID':'LIN'})
            #Note: in this loop get() is used on the lin-object, and put() is used for the lou-object!
            lou.put({'BOTSID':'LIN','LINENUMBER':lin.get({'BOTSID':'LIN','1082':None})})
            lou.put({'BOTSID':'LIN','ARTICLE_GTIN':lin.get({'BOTSID':'LIN','C212.7140':None})})
            lou.put({'BOTSID':'LIN','QUANTITY':lin.get({'BOTSID':'LIN'},{'BOTSID':'QTY','C186.6063':'21','C186.6060':None})})

        #OK, we did the lines, but forgot to map the party's - the parties are before the lines  in the incoming message.
        #No problem, get/put can be done anywhere in the mapping - we are NOT looping the incoming or outgoing message:
    
        out.put({'BOTSID':'HEA','BUYER_ID':inn.get({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'BY','C082.3039':None})})
        out.put({'BOTSID':'HEA','SUPPLIER_ID':inn.get({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'SU','C082.3039':None})})
        out.put({'BOTSID':'HEA','DELIVERYPLACE_ID':inn.get({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'DP','C082.3039':None})})

**MPATH: Query the edi data**

In the examples above the data in the edi messages is queried using eg 
``{'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'BY','C082.3039':None}``.
This **thing** is called a mpath (just a name). Mpath is quite important in building a mapping.

More about mpath:

* An mpath consists of one or more python 'dicts' (dictionaries), separated by commas: *dict1,dict2, dict3*
* ``BOTSID`` is the record identifier.
* In get(): ``None`` indicates that the value of this field should be returned. All others fields are interpreted as: if field==value.
* In put(): all name-values are written, but not if one of the values is ``None``. If one of the values is None no values at all are written to outgoing message. This is used in the combined out.put(...inn.get(...)...)-statements.

Detailed information about get, getloop, put, putloop is :doc:`here <mapping-functions>`

.. warning::
    Never do this (use 2 inn.get's in one out.put):

    .. code-block:: python

        out.put({'BOTSID':'ADD','7747':inn.get('BOTSID':'HEA','name1':None),'7749':inn.get('BOTSID':'HEA','name2':None)})}

    **Reason**: if either name1 or name2 is not there (empty, None) nothing will be written in this statement.

**Another Mapping Example**

.. code-block:: python

    def main(inn,out):
        #The incoming message object (inn) has a dict 'ta_info'. 
        #ta_info contains information from the QUERIES in the grammar;
        #mostly  envelope data like sender, reciever etc.about the message as specified in the grammar (queries, SUBTRANSLATION). 
        out.put({'BOTSID':'HEA','SENDER':inn.ta_info['frompartner']})

        #The outgoing message object (out) also has a dict ta_info. 
        #You can change it if required. eg. to set topartner:
        BuyerID = inn.get({'BOTSID':'HEA','BUYER_ID':None})
        inn.ta_info['topartner'] = BuyerID       #use BuyerID as topartner (when eveloping)

        #Inn-get() either return a value, or 'None'. Look at the next line:
        out.put({'BOTSID':'UNH'},{'BOTSID':'DTM','C507.2005':'137','C507.2380':inn.get({'BOTSID':'HEA','ORDERDATE':None})})    
        #if there is no ORDERDATE in the HEA record, put() receives a 'None'-value. 
        #Nothing will be written to the outgoing message! 

        #in the next lines 2 values from the inhouse record are written to the same record:
        out.put({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'DP','C082.3055':'9','C082.3039':inn.get({'BOTSID':'HEA','DELIVERYPLACE_ID':None})})
        out.put({'BOTSID':'UNH'},{'BOTSID':'NAD','3035':'DP','C058.3036':inn.get({'BOTSID':'HEA','DELIVERYPLACE_NAME':None})})
        #both the deliveryplace_id and deliveryplace_name are written to a NAD-record with qualifier 'BY .
