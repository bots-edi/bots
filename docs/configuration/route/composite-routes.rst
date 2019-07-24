Composite routes
================

A simple route reads the edi files from one inchannel, translates, and sends the translated files to one outchannel.
More flexibility is offered by the use of composite routes.
In a composite route there are several entries in the routes screen, each with the same **idroute** but a different **seq**
(sequence number within route). Each entry (with different **seq**) is called **route-part**.
Best way to use this is to have each route-part do any one of the things:

* Fetch incoming files; you can fetch files from multiple sources
* Translate (typically once per route)
* Send outgoing files to different destinations/partners using `filtering <#filtering-for-different-outchannels>`_

It is advised to set up composite routes this way (using at least 3 route-parts).

**Use cases**

* Send edi files via ftp where each partner has its own ftp-server.
* Confirmations/acknowledgements: acknowledgements for incoming edi-files are routed back to the sender (filter by editype/messagetype).
* Fetch from multiple sources, eg ftp-servers of different partners..
* Route to different internal destinations: invoices to another system than ASN's (filter by messagetype)
* Use a VAN, but one partner uses AS2 (filter by partner)
* Incoming files are translated multiple times, each message-type goes to different destination. Eg: translate orders both to in-house file (import ERP) and an HTML-email (for viewing).

**Example plugin**

Download the plugin `demo_composite_route <http://sourceforge.net/projects/bots/files/plugins/>`_
This plugin has one composite route consisting of:

* 2 input parts
* Translate part
* 3 output parts, using `filtering <#filtering-for-different-outchannels>`_

Detailled description here.

**Filtering for different outchannels**

* You can filter per outchannel; eg send only asn's through this outchannel.
* In route-screen (``bots-monitor->Configuration->Routes``) the fields used for filtering under **Filtering for outchannel**.
* If eg toeditype=csv, only csv-files will be send over the outchannel.

.. note::
    If filtering is not specified, all outgoing files in the route are send through the outchannel. 

**Schematic**

Schematic overview of a route consisting of 5 parts: 

.. image:: ../../images/RouteDiagramComp.png

.. note::

    * If no inchannel in route-part nothing comes in for that route-part.
    * If 'translate' in a route-part is off, no translation in that route-part.
    * If no outchannel in route-part nothing goes out for that route-part.
