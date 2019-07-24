Confirmations/Acknowledgements
==============================

In edi often a confirmation (or acknowledgement) is needed. Bots has a built-in confirmation framework that supports:

* 997 (x12)
* CONTRL (edifact)
* MDN (email)
* APERAK (edifact)

Confirmations have 3 aspects:

* Bots sends a confirmation for an incoming edi-file.
* Bots asks a confirmation for an outgoing edi-file.
* Bots processes an incoming confirmation.

You can view the results of asked or send confirmations in ``bots-monitor->All runs->Confirmations``. 
All send or asked confirmations are registered in bots if configured correct. 

.. rubric::
    Examples in plugins

* plugin ``x12-850-856-810-997``
    * generates a 997 for incoming orders, and dispatches this via a composite route.
    * inbound route is configured to process 997's.
* plugin ``demo_mdn_confirmations`` sends and receives email-confirmations (MDN)
* plugin ``edifact_ordersdesadvinvoic`` sends APERAK for incoming orders - if indicated in incoming order.

.. rubric::
    Send Confirmation

#. First configure correct processing of incoming edi-files.
#. Configure confirmrules in ``bots-monitor->Configuration->Confirmrules``. You can use several confirmation rules, bots looks at all rules. Per rule:
    * Indicate the kind of confirmation to send (997, CONTRL, etc).
    * Indicate how the rules works - per route, channel, messagetype, etc. (prior to bots 3.0, frompartner and topartner where swapped :-(
    * An option is to include first and than exclude using 'negativerule'. Bots first checks the positive rules, than the negative rules. Eg: send 997 for all incoming x12-files in a route, and exclude partner XXX.
#. Use a :doc:`composite route <route/composite-routes>` to send the confirmations to the right destination.

.. rubric::
    Ask Confirmation

#. First configure correct processing of outgoing edi-files.
#. Then configure ``bots-monitor->Configuration->Confirmrules`` You can configure several confirmation rules, bots looks at all rules. Per rule:
    * Indicate the kind of confirmation to ask (997, CONTRL, etc).
    * Indicate how the rules works - per route, channel, messagetype, etc. (prior to bots 3.0, frompartner and topartner where swapped :-(
    * An option is to include first and than exclude using 'negativerule'. Bots first checks the positive rules, than the negative rules. Eg: ask 997 for all outgoing x12-files in a route, and exclude partner XXX.
#. You will need to process the incoming confirmation.

.. rubric::
    Process incoming confirmation

* 997 (x12): an additional translation and mapping script is needed.
* CONTRL (edifact): an additional translation and mapping script is needed.
* MDN-confirmations: no additional comfiguration is needed.

.. rubric::
    Send 997/Acknowledgement for Incoming X12 Orders

* Before attempting to configure confirmations create and test a route for a typical X12 message e.g. 850. 
* Once that is working correctly, confirmations can be configured for the route. 
* Bots will now generate a 997 message for each 850 recipient. Notice that the 997 is in the same Route as the 850. 
* Probably you will want the 997 to go back out to the partner that sent the 850. Use a :doc:`composite route <route/composite-routes>` for this. 
* Tell bots to send confirmations (997 message) in ``bots-monitor->Configuration->Confirmrules``. Note that in the route established for the 850, there is a sequence number next to the routeID. 
* The ``seq`` for the 850 is probably **1**. A new route-part must now be created to handle the 997 that bots has generated. 
* The new route-part has the same routeID but a higher ``seq`` number (e.g. **2**). Now configure to route the 997 message that bots will generate. 
* The 997 is an internally generated file. The user will have very little to do with its creation but everything to do with where the file goes (i.e. its route). 
* Route with seq 2 will have ``none`` as its incoming channel, and does not translate. Its outgoing channel will most likely be to FTP or a VAN. 
* The key to success is in using the "Filtering for outchannel" at the bottom of the "Change Route" page. 
* In "Filtering for outchannel" for 'seq' 1, set toeditype and tomessagetype so that only the translated 850 file will take this part of the Composite Route. 
* Now for seq 2 set toeditype to X12. This will cause only the X12 997 message to follow this part of the composite route.

