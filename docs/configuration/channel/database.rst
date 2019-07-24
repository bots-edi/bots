Database Communication
======================

Bots can read and write from a database. See plugin ``demo_databasecommunication`` on the `bots sourceforge site <https://sourceforge.net/projects/bots/files/plugins/>`_.

**Discussion: Direct Database Communication or Not**

In most edi setups there is no direct database communication, but an intermediate file is used:

* Inbound edi: bots translates edi files to your import format
* Outbound edi: the export files of your application are translated by bots to the wished edi format.

Reasons to set up edi using an intermediate file:

* It is better to do the import/export with the tools you are familiar with, and not to use a new tool (knowledge, maintenance).
* Different edi partners do use different standards (dialects of the standards, different interpretations, different countries, different sectors, edi standards are not that good). Try to use one import/export format; let the edi software handle the differences between partners.

Reasons to use direct database format:

* Import/Exports are very simple/straightforward
* Your system does not (yet) have good functionality for handling the incoming edi data. Example: receive sales reports, but what to do with this? This data is quite simple, just import this in one (new) table. The users can query this table for information.

**Inbound edi (write to database)**

* Translation rule should be to edi-type ``db``
* In the mapping script: out.root should be a python object (dict, list, class, etc); this object is passed to the actual database connector.
* Outgoing channel should be type 'db'.
* Use a communication script for the outgoing channel ``usersys/communicationscripts/channelname.py``. This communication script does the actual communication with the database.
* In the communication script should be 3 functions:
    * connect - build database connection.
    * out-communicate - put the data in the database using the data as received from the mapping script.
    * disconnect - close database connection.
* Use the database connector as needed, eg: python provides by default the sqlite3 connector, mysql-Python as MySQL database connector, psycopg2 as PostgreSQL database connector, etc

**Outbound edi (read from database)**

* Incoming channel should be type ``db``.
* Use a communication script for the incoming channel ``usersys/communicationscripts/channelname.py``. This communication script does the actual communication with the database.
* In the communication script should be 3 functions:
    * connect - build database connection.
    * incommunicate - fetch the data from the database, send it to the mapping script.
    * disconnect - close database connection.
* Use the database connector as needed, eg: python provides by default the sqlite3 connector, mysql-Python as MySQL database connector, psycopg2 as PostgreSQL database connector, etc
* Translation should be from edi-type ``db``
* In the mapping script: inn.root is the data as received from the database connector.

.. note:: 
    The data passed from the communication-script can be any python object (eg dict, list). If a list (or tuple) is return from the communication script, bots passes each member of the list as a separate edi-message to the mapping script.
