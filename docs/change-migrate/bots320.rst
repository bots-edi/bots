Bots 3.2.0
==========

* Bots 3.2.0rc was released 2014-03-22.
* Bots 3.2.0rc2 was released 2014-05-27.
* Bots 3.2.0 was released 2014-09-02.

Migration notes
---------------
    * bots 3.2.0 is suited for django 1.4, 1.5, 1.6 and 1.7. Support for Django 1.3 is dropped.

    * In existing settings.py django requires parameter 'ALLOWED_HOSTS'. Add this as eg:

        .. code-block:: python

            ALLOWED_HOSTS = ['*']

    * For SQLite no database migration is needed. For MySQL and PostgreSQL: in table unique, field 'domein' should be changed to 70 positions (was: 35) if using option to have in-communication connect failures reported after xx times (field 'Max failures' in channels).
    * Python 2.5 is not supported anymore. use 2.6, preferably 2.7.
    * Bots does not support python > 3 (yet). Reason is that python MySQL connector is not suited for python 3 (yet).

Changes
-------

    **Highlights**

    #. Added http(s) communication to communication methods (using 'requests' library).
    #. Better reporting of partnerID for incoming files with errors.
    #. File rename after outcommunication using tmp filenames to avoid 'reading before writing'.
    #. Updated edifax (print to html); is much easier to use now (edifax plugin will be updated).

    **Interface (GUI)**

    #. In run-screen: show used command for bots-engine, show if acceptance test.
    #. Search by filename for incoming and outgoing files.
    #. *strange characters* like ``ëë`` in routeID, channelID, etc will work now.
    #. Option to have automaticretrycommunication in menu.
    #. Option to add only routes that are not in default run to menu.
    #. Added bulk delete for persists data.
    #. Use 'rereceive' and 'resend' in screens (instead of 'retransmit').
    #. Simpler making bots suited for touchscreen.
    #. Filter routes for (not) in default run.
    #. Improved edifact indenting in file viewer.
    #. Div small layout improvements in GUI.

    **Smaller changes**

    #. unicode handling is improved. This is about use of unicode in route-names, grammars, correct errors, etc
    #. set maxdaysarchive per channel.
    #. email validation in django was too strict for certain email addresses.
    #. check CC-address when validating incoming email-addresses.
    #. improve reporting on in-communication failures (give process-error after x time failure).
    #. suited for django 1.4, 1.5, 1.6and 1.7. Django 1.3 support is dropped.
    #. add incoming filename in email-report.
    #. option to use user script entries at start/end of a run and command.
    #. added option 'parse and passthrough' for routes. Useful for eg generating 997/CONTROL.
    #. added explicit enveloping indication (this indication can be set in mapping).
    #. making of plugin could take take a long time (better performance for large plugins).
    #. improve processing of repeat separator in ISA version above 00403.
    #. xml2botsgrammar: order of elements is preserved now; all xml entities as records.
    #. xml2botsgrammar: added option to have all xml entities as 'record'.
    #. added option to have function 'transform.partnerlookup' return 'None' if not found.
    #. improve xmlrpc communication.
    #. for persist: change timestamp on update.
    #. used new definitions for UNOA and UNOB. Definitions are clearer and easier to change, no change in functionality.
    #. better performance for one-on-one translations.
    #. bots-engine uses less memory.
    #. better reporting for import errors.

    **Bug fixes**

    #. preprocessing not working for rereceive.
    #. fixed bug in windows installer (occurred when when UAC is disabled).
    #. routeid did not always show up correct in error.
    #. rights problem: viewer can delete incoming files.
    #. show filesize for passthrough files.
    #. MySQLdb version 1.2.5 gave error.
    #. change password for non-staff user did not work.
    #. found query's in GUI not using index (better performance).
    #. error could not be displayed: <unprintable MessageError? object>.
    #. multiple email-addresses were not used in sending emails.
    #. transform.concat erroneously added spaces between elements.
    #. callable in QUERIES should have 'node' as parameter.
    #. when received x12 message can not be parsed correctly, GS08 might not be found.
    #. routeid did not show up correct in some errors.
    #. incoming tab-delimited file not parsed correct (for nobotsID & first field Conditional).
    #. via incoming/outgoing screen: button 'confirm (same selection)' did not work.
    #. in forms.py: reference was an..35, should be an..70
