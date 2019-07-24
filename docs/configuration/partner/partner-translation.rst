Partner Specific Translation
============================

**Explain by example**

You receive edifact ORDERSD96AUNEAN008 from several partners. Partner ``retailer-abroad`` fills the orders in a different way; the difference is so big that it is better to have a separate mapping script.
Configure this like:

* one grammar for incoming edifact ORDERSD96AUNEAN008 message. (It is a standard message, isn't it?)
* one grammar for the inhouse import format. (We definitely want one import for all orders!)
* note that the incoming edifact grammar uses QUERIES to determine the from-partner and to-partner before the translation.
* make the 2 mapping scripts:
    * mapping script ``ordersedi2inhouse_for_retailerabroad.py`` (specific for partner ``retailer-abroad``) .
    * mapping script ``fixed-myinhouseorde``' (for all other retailers).
* add ``retailer-abroad`` to partners (via bots-monitor->Configuration->Partners & groups).
* Use 2 translations rules:
    * edifact-ORDERSD96AUNEAN008 to fixed-myinhouseorder using mapping script ``ordersedi2inhouse.py``
    * edifact-ORDERSD96AUNEAN008 to fixed-myinhouseorder using mapping script ``ordersedi2inhouse_for_retailerabroad.py`` for from-partner ``retailer-abroad``

Often there are lots of similarities between the mappings - the 'many similar yet different mappings' problems. This can be :doc:`handled in bots <organize-partner-translation>` in a nice way.

**Plugin**

Plugin 'demo_partnerdependent' at the `bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_ demonstrates partner-groups.

