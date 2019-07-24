Configuration
=============

* Out of the box bots does nothing. You have to configure bots for your specific edi requirements. 
* Check out different ways to start your own :doc:`configuration<how-to-configuration>`. 
* See :doc:`debug <../debugging>` overview for info how to debug while making a configuration. 
* Bots also has nice features for :doc:`configuration change management <../advanced-deployment/change-management>` (build test sets for you configuration, easier pushing of changes from test to production).


**Configuration explained in short**

* ``routes`` are edi-workflows.
* ``channels`` do the communication (from file system, ftp, etc).
* each route hs an ``inchannel`` and an ``outchannel``
* Translations rules determine: translate what to what.

**Most asked configuration topics**

* :doc:`composite routes <route/composite-routes>`
* :doc:`passthrough route <route/passthrough>` (without translation)
* :doc:`options for outgoing filenames <channel/filenames>`
* :doc:`direct database communication <channel/database>`
* :doc:`partner specific translations <partner/partner-translation>`
* :doc:`code conversion <mapping-scripts/code-conversion>`
* view :doc:`business documents <document-view>` instead of edi-files.
* :doc:`confirmations/acknowledgements <acknowledgements>`
* :doc:`merging and enveloping outgoing edi files <split-merge>`
* :doc:`partner specific syntax <partner/partner-syntax>` (especially for x12 and edifact)

**Index**

.. toctree::
   :maxdepth: 2

   how-to-configuration 
   route/index
   channel/index
   translation/index
   mapping-scripts/index
   grammars/index
   document-view
   user-scripting
   acknowledgements
   split-merge
   partner/index
   charsets
