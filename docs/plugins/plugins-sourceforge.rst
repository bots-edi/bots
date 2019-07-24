Plugins at SourceForge
======================

Downloads at `the bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_

* my_first_plugin
    * This plugin is used in the the :doc:`tutorial <../quick-start-guide/index>`.
    * edifact ORDERS to fixed records.
* edifact2xml_ordersdesadvinvoice
    * The most used edifact messages in one package.
    * edifact ORDERS to xml
    * ASN/shipping list: edifact2xml_ordersdesadvinvoice to edifact DESADV.
    * Invoice: xml to to edifact INVOIC.
* x12toxml_supplier_version_850-856-810-997
    * The most used x12 messages in one package.
    * translate x12 850 -> xml orders.
    * Generates 997's for the received orders.
    * translate xml ASN's -> x12 856; including partner specific translation to 856.
    * translate xml invoices -> x12 810.
* x12toxml_retailer_version_850-856-810-997
    * The most used x12 messages in one package.
    * translate xml orders -> x12 850.
    * translate x12 856 -> xml ASN's
    * translate x12 810 -> xml invoices
* x12toxml_one-on-one_835-837
    * translate x12 835 > xml and reverse (xml->x12 835)
    * translate x12 837 > xml and reverse (xml->x12 837)
    * one-on-one mapping: structure of xml is similar to structure of x12
    * x12 envelopes are included in mapping
* demo_composite_route
    * demonstrates the use of composite routes.
    * 2 different sources are used for incoming edifact files
    * convert edifact orders to fixed format.
    * also converts these orders to print format (html).
    * convert edifact SLSRPT to csv format.
    * all outgoing messages go to different destination using filtered outchannels
* edifact2fixed_orders-desadv-invoic
    * The most used edifact messages in one package.
    * Suited for Dutch non-food retailers; probably for a lot of other retailers as well.
    * edifact ORDERS to fixed file format.
    * generate a edifact APERAK message (if requested in the order).
    * fixed format ASN/shipping list to a edifact DESADV.
    * fixed format invoice to edifact INVOIC.
* demo_working_with_partners demonstrates the use of partner dependent functionalities in bots:
    * parter dependent translations.
    * user of 'default translation'  and imports.
    * partner dependent syntax.
    * use of partner-lookup in the database.
    * use of partner groups.
    * different destinations/outchannels for partners.
    * advanced usage of ISA qualifiers/partnerID. Your partnerID is used to lookup the ediID and ISA qualifier in database (and of course vice versa).
* demo_sap_idoc_orders_WPPLU
    * edifact D96A ORDERS to idoc ORDERS01.
    * edifact D96A PRICAT to idoc WP_PLU02.
    * idoc ORDERS01 to edifact D96A ORDERS.
    * idoc WP_PLU02 to edifact D96A PRICAT.
* demo_communicationscript
    * Demonstrates user communication scripting.
    * Incoming edi-messages can be passed one by one or as one batch.
* demo_databasecommunication
    * Demonstrates database communication scripts; both reading and writing (in separate routes).
    * A test database comes with the plugin.
* demo_mdn_confirmations
    * Demo configuration for MDN (email confirmations)
    * See also documentation about confirmations.
* demo_one-on-one_edifactorder2xml
    * Translates a edifact ORDERS D96A message to xml-message using edifact tags as xml-elements and vice versa.
    * For those who like processing xml instead of edifact.
    * It is quite easy to add other edifact messages types for similar translations.
* edifact2json_invoic
    * Translates edifact D96A invoice to JSON en vice versa.
* edifact_ordertoprint
    * Translates a edifact ORDERS D96A message into a readable format (HTML).
    * Of course you can print the order, so it is like a (edi)fax.
* edifact_orders2csv_and_vv
    * Translates edifact D96A orders to csv en vice versa.
    * There a 2 variants: csv with or without record tags (csv from eg excel is often without records tags).
* edifact_pricat-slsrpt
    * Csv to edifact PRICAT.
    * Edifact SLSRPT to csv.
* demo_preprocessing
    * This plugin demonstrate preprocessin: the incoming edifact-files start with an number of '#' and '@'. These characters are removed by preprocessing the files.


.. rubric::
    Contributed plugins at SourceForge

* alto_seperate_headers_details
    * input: 2 csv files, one with headers, one with details lines.
    * this is processed into one idoc (so the headers and details are merged).
    * Same technique is also usable for fixed format.
* x12_837_4010_to_x12_837_5010
    * converts (physician) insurance claims (x12 837) in the version 4010 to the new, upcoming, 5010 version.          
    * The mapping file is rudimentary, but I believe the conversion is OK.          
    * I found that removing the one REF file creates a version 5010 file that is accepted and processed properly by Anvicare, the clearing house for my commercial claims.          
    * I have included anonymized input edi transactions for Medicare, Blue Shield and commercial insurers.          
    * My approach is to try the translation as is, and to make corrections in the mapping file only if I get errors from the clearing house.          
    * Medicare and Blue Shield provide comprehensive error checking function.  However, they do not yet accept 5010 transactions, even for testing purposes.          
    * The clearing house accepts 5010 transactions, and they work.
* x12_fixed_2_810
    * converts fixed inhouse to x12 810 including calculation of invoice totals etc and partner specific seperators.
