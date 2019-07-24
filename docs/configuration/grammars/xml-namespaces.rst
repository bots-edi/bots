XML Namespaces
==============

Dealing with xml namespaces can be a bit difficult in Bots. They can greatly complicate grammars and mappings. Often your EDI partner will want to send or receive XML with namespaces, but actually Bots does not need (or want) them as there are rarely any naming conflicts within a single XML file!

Where an XML file has only one namespace, usually the "default" namespace is used.
eg. ``xmlns="schemas-hiwg-org-au:EnvelopeV1.0"``

If the file has multiple namespaces, then namespace prefixes are used. These prefixes can be any value.
eg. ``xmlns:ENV="schemas-hiwg-org-au:EnvelopeV1.0"``

There are several ways to deal with namespaces in Bots:

#. **Ignore incoming XML namespace**

    For incoming XML files that are to be mapped into something else, you probably don't need the namespaces at all. In my opinion this is the "best" way. See an :doc:`example preprocessing script <../route/route-scripting>` to achieve this.

#. **Use incoming XML namespace**

    When a namespace must be used, it is needed in many places (structure, recorddefs, mapping) but you want to specify the namespace string, 
    which can be quite long, only in one place (`DRY principle <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_). This has several benefits:

    * If it needs to change, this is easy to do in one place only
    * grammar and mapping will be smaller, and look neater

    For example, the incoming XML file may look like ...

    .. code-block:: xml

        <?xml version="1.0"?>
        <Orders xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             xmlns="http://www.company.com/EDIOrders"
             targetNamespace="http//www.company.com/EDIOrders">
              <Order>
                <OrderNumber>239062415</OrderNumber>
                <DateOrdered>2014-02-24</DateOrdered>
                <LineCount>10</LineCount>
        etc...
    
    If you created your grammar with ``xml2botsgrammar``, it probably has the namespace repeated over and over in structure and recorddefs, like this:

    .. code-block:: python

        structure=    [
        {ID:'{http://www.company.com/EDIOrders}Orders',MIN:1,MAX:1,LEVEL:[
            {ID:'{http://www.company.com/EDIOrders}Order',MIN:1,MAX:99999,
                QUERIES:{
                     'botskey':      {'BOTSID':'{http://www.company.com/EDIOrders}Order','{http://www.company.com/EDIOrders}OrderNumber':None},
                    },
                LEVEL:[
                {ID:'{http://www.company.com/EDIOrders}OrderItems',MIN:0,MAX:1,LEVEL:[
                    {ID:'{http://www.company.com/EDIOrders}OrderLine',MIN:1,MAX:99999},
                    ]},
                ]},
            ]}
        ]

        recorddefs = {
           '{http://www.company.com/EDIOrders}Orders':[
                    ['BOTSID','M',256,'A'],
                    ['{http://www.company.com/EDIOrders}Orders__targetNamespace','C',256,'AN'],
                  ],
           '{http://www.company.com/EDIOrders}Order':[
                    ['BOTSID','M',256,'A'],
                    ['{http://www.company.com/EDIOrders}OrderNumber','C', 20,'AN'],
                    ['{http://www.company.com/EDIOrders}DateOrdered','C', 10,'AN'],
                    ['{http://www.company.com/EDIOrders}LineCount','C', 5,'R'],

        # etc...

    So, we want to improve this. In your grammar, first add the namespace as a string constant. This is the only place it should be specified, and everywhere else refers to it.

    .. note:: 
        If the XML has multiple namespaces, you can use the same technique and just add more constants (xmlns1, xmlns2, etc). Also include it in the syntax dict. This allows us to reference it later in mappings.

         .. code-block:: python

            xmlns='{http://www.company.com/EDIOrders}'
            syntax = {
                'xmlns':xmlns,
            }
    
    In your grammar, replace all instances of the namespace string with the constant, so it looks like this:
    
    .. code-block:: python

        structure=    [
        {ID:xmlns+'Orders',MIN:1,MAX:1,LEVEL:[
            {ID:xmlns+'Order',MIN:1,MAX:99999,
                QUERIES:{
                     'botskey':      {'BOTSID':xmlns+'Order',xmlns+'OrderNumber':None},
                    },
                LEVEL:[
                {ID:xmlns+'OrderItems',MIN:0,MAX:1,LEVEL:[
                    {ID:xmlns+'OrderLine',MIN:1,MAX:99999},
                    ]},
                ]},
            ]}
        ]

        recorddefs = {
           xmlns+'Orders':[
                    ['BOTSID','M',256,'A'],
                    [xmlns+'Orders__targetNamespace','C',256,'AN'],
                  ],
           xmlns+'Order':[
                    ['BOTSID','M',256,'A'],
                    [xmlns+'OrderNumber','C', 20,'AN'],
                    [xmlns+'DateOrdered','C', 10,'AN'],
                    [xmlns+'LineCount','C', 5,'R'],

        # etc...

    Now in the mapping script, read the xmlns value from grammar.
    
    .. code-block:: python

        import bots.grammar as grammar
        xmlns = grammar.grammarread('xml',inn.ta_info['messagetype']).syntax['xmlns']
    
    Then use it wherever needed in the mapping, like this:

    .. code-block:: python

        # Get OrderNumber from XML with namespace
        OrderNumber = inn.get({'BOTSID':xmlns+'Order',xmlns+'OrderNumber':None})

#. **Outgoing XML with only a default namespace**

    This can be done by defining xmlns as a tag, and setting it in mapping. It eliminates the need to use namespace prefix on every record and field. example grammar

    .. code-block:: python

        recorddefs = {
            'shipment':
                [
                ['BOTSID', 'M', 20, 'AN'],
                ['shipment__xmlns', 'C', 80, 'AN'],   # xmlns is added as a tag (note double underscore)
                ['ediCustomerNumber', 'M', 12, 'N'],
                ['ediParm1', 'M', 1, 'N'],
                ['ediParm2', 'M', 1, 'AN'],
                ['ediParm3', 'M', 1, 'AN'],
                ['ediReference', 'M', 35, 'AN'],
                ['ediFunction1', 'M', 3, 'AN'],
                ['ediCustomerSearchName', 'M', 20, 'AN'],
                ],
        }

    Example Mapping

    .. code-block:: python

        # xmlns tag for shipment
        out.put({'BOTSID':'shipment','shipment__xmlns':'http://www.company.com/logistics/shipment'})

    Example Output

    .. code-block:: xml

        <?xml version="1.0" encoding="utf-8" ?>
        <shipment xmlns="http://www.company.com/logistics/shipment">
            <ediCustomerNumber>191</ediCustomerNumber>
            <ediParm1>4</ediParm1>
            <ediParm2>s</ediParm2>
            <ediParm3>d</ediParm3>
            <ediReference>SCN1022164911</ediReference>
            <ediFunction1>9</ediFunction1>
            <ediCustomerSearchName>SCHA</ediCustomerSearchName>
        </shipment>

#. **Outgoing XML with default namespace prefixes (ns0, ns1, etc)**

    **This is the default behaviour of the python elementtree module used in Bots**.The actual prefix used is not important to XML meaning, so in theory your EDI partners should not care what prefixes you use.

    Example Grammar:
    
    .. code-block:: python

        xmlns_env='{schemas-hiwg-org-au:EnvelopeV1.0}'
        xmlns='{schemas-hiwg-org-au:InvoiceV3.0}'

        syntax = {
                'xmlns_env':xmlns_env,
                'xmlns':xmlns,
                'merge':False,
                'indented':True,
        }

        nextmessage = ({'BOTSID':xmlns_env+'Envelope'},{'BOTSID':'Documents'},{'BOTSID':xmlns+'Invoice'})

        structure = [
        {ID:xmlns_env+'Envelope',MIN:0,MAX:99999,
            QUERIES:{
                'frompartner':{'BOTSID':xmlns_env+'Envelope',xmlns_env+'SenderID':None},
                'topartner':{'BOTSID':xmlns_env+'Envelope',xmlns_env+'RecipientID':None},
                },
            LEVEL:[
            {ID:'Documents',MIN:0,MAX:99999,LEVEL:[
                {ID:xmlns+'Invoice',MIN:0,MAX:99999,
                    QUERIES:{
                        'botskey':({'BOTSID':xmlns+'Invoice',xmlns+'DocumentNo':None}),
                        },
                    LEVEL:[
                    {ID:xmlns+'Supplier',MIN:0,MAX:99999},
                    {ID:xmlns+'Buyer',MIN:0,MAX:99999},
                    {ID:xmlns+'Delivery',MIN:0,MAX:99999},
                    {ID:xmlns+'Line',MIN:0,MAX:99999},
                    {ID:xmlns+'Trailer',MIN:0,MAX:99999},
                ]},
            ]},
        ]},
        ]

    Example Output

    .. code-block:: xml

        <?xml version="1.0" encoding="utf-8" ?>
        <ns0:Envelope xmlns:ns0="schemas-hiwg-org-au:EnvelopeV1.0" xmlns:ns1="schemas-hiwg-org-au:InvoiceV3.0">
            <ns0:SenderID>sender</ns0:SenderID>
            <ns0:RecipientID>recipient</ns0:RecipientID>
            <ns0:DocumentCount>1</ns0:DocumentCount>
            <Documents>
                <ns1:Invoice>
                    <ns1:TradingPartnerID>ID1</ns1:TradingPartnerID>
                    <ns1:MessageType>INVOIC</ns1:MessageType>
                    <ns1:VersionControlNo>3.0</ns1:VersionControlNo>
                    <ns1:DocumentType>TAX INVOICE</ns1:DocumentType>

#. **Outgoing XML with specific namespace prefixes**

    Your EDI partner may request a specific namespace prefix be used; This is technically un-necessary and bad design, but they may insist on it anyway!

    Example Grammar

    .. code-block:: python

        xmlns_env='{schemas-hiwg-org-au:EnvelopeV1.0}'
        xmlns='{schemas-hiwg-org-au:InvoiceV3.0}'

        syntax = {
                'xmlns_env':xmlns_env,
                'xmlns':xmlns,
                'namespace_prefixes':[('ENV',xmlns_env.strip('{}')),('INV',xmlns.strip('{}'))], # use ENV, INV instead of ns0, ns1
                'merge':False,
                'indented':True,
        }

        structure = [
        {ID:xmlns_env+'Envelope',MIN:0,MAX:99999,
            QUERIES:{
                'frompartner':{'BOTSID':xmlns_env+'Envelope',xmlns_env+'SenderID':None},
                'topartner':{'BOTSID':xmlns_env+'Envelope',xmlns_env+'RecipientID':None},
                },
            LEVEL:[
            {ID:'Documents',MIN:0,MAX:99999,LEVEL:[
                {ID:xmlns+'Invoice',MIN:0,MAX:99999,
                    QUERIES:{
                        'botskey':({'BOTSID':xmlns+'Invoice',xmlns+'DocumentNo':None}),
                        },
                    LEVEL:[
                    {ID:xmlns+'Supplier',MIN:0,MAX:99999},
                    {ID:xmlns+'Buyer',MIN:0,MAX:99999},
                    {ID:xmlns+'Delivery',MIN:0,MAX:99999},
                    {ID:xmlns+'Line',MIN:0,MAX:99999},
                    {ID:xmlns+'Trailer',MIN:0,MAX:99999},
                ]},
            ]},
        ]},
        ]

    Example Output
 
    .. code-block:: xml

        <?xml version="1.0" encoding="utf-8" ?>
        <ENV:Envelope xmlns:ENV="schemas-hiwg-org-au:EnvelopeV1.0" xmlns:INV="schemas-hiwg-org-au:InvoiceV3.0">
            <ENV:SenderID>sender</ENV:SenderID>
            <ENV:RecipientID>recipient</ENV:RecipientID>
            <ENV:DocumentCount>1</ENV:DocumentCount>
            <Documents>
                <INV:Invoice>
                    <INV:TradingPartnerID>ID1</INV:TradingPartnerID>
                    <INV:MessageType>INVOIC</INV:MessageType>
                    <INV:VersionControlNo>3.0</INV:VersionControlNo>
                    <INV:DocumentType>TAX INVOICE</INV:DocumentType>

