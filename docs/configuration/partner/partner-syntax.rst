Partner Dependent Syntax
========================

* For outgoing messages it is possible to specify a partner dependent syntax.
* This is especially useful for x12 and edifact, for setting envelope values and partner specific separators.
* These parameters override the settings in the message grammar; you only need to specify the partner-specific parameters.

.. note::
    no need to set partner specific separators for incoming messages; bots will figure this out by itself.

To set partner specific syntax parameters, create according to editype used:

* ``bots/usersys/partners/x12/partnerid.py``
* ``bots/usersys/partners/edifact/partnerid.py``

Example file with partner specific setting (x12):

.. code-block:: python

    syntax = {
         'ISA05'                  : 'XX',    #use different communication qualifier for sender
         'ISA07'                  : 'ZZ',    #use different communication qualifier for receiver
         'field_sep'              : '|',     #use different field separator
         }
  
Example file with partner specific setting (edifact):

.. code-block:: python

    syntax = {
              'merge':False,
              'forceUNA':True,
              'UNB.S002.0007':'ZZ',        # partner qualifier
              'UNB.S003.0007':'ZZ',        # partner qualifier
              }
