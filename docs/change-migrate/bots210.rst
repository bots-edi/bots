Bots 2.1.0
==========

* This version is the first version in one-and-a-half year.
* Bots 2.0.2 proved to be quite stable.
* This version adds a lot of new functionality; quite some bugs have been fixed.
* This new verson is very upward compatible with version 2.0.2

Migration Notes
---------------

    **Procedure**

    * Get the plugin at `sourceforge <http://sourceforge.net/projects/bots/files/bots%20open%20source%20edi%20software/>`_.
    * Mind there are 2 version of the plugin, depending upon the version of django you use.
    * Read like a normal plugin (bots-monitor->systasks->read plugin).
    * Stop the web-server.
    * Restart bots-webserver.

    **Compatibility**

    Version 2.1.0 is upward compatible with previous versions in 2.*.*-series:

    * no data migration needed
    * grammars, translations etc mostly will work as before

    **Compatibility notes**

    After upgrading, some (eg. older edifact) grammars can give errors. This is due to stricter checking of grammars. The records in a grammar are now checked for unique field-names: the same field name is not allowed in a record. This was never OK, but was not checked). Typical error:

    .. code-block:: python

        GrammarError: Grammar "...usersys/grammars/edifact.ORDERSD96AUNEAN008", record "FII": field "C078.3192" appears twice. Field names should be unique within a record.

    The culprit is the file D96Arecords (or similar), the FII segment has an error in it.

        * Solution 1: adapt grammar manually; change FII segment:

            .. code-block:: python

                ['C078.3192','C',35,'A'],
                ['C078.3192','C',35,'A'],

            to

            .. code-block:: python

                ['C078.3192','C',35,'A'],
                ['C078.3192#2','C',35,'A'],

        * Solution 2: use plugin ``update_edifact_recorddefs.zip`` (same directory as update-plugins. this plugin only contains edifact records for D93A and D96A).


Changes
-------

    Detailed changes in version 2.1.0 are `here <http://bots.sourceforge.net/en/botsversion210.shtml>`_.
 
    **Changes in bots.ini**

    You can use your old bots.ini with no problem, reasonable defaults have been used. Following are the new options added.

    .. code-block:: ini

        [settings]

        #adminlimit: number of lines displayed on one screen for configuration items; default is value of 'limit'
        #adminlimit = 30

        #for incoming channels: limit the time in-communication is done (in seconds). Default is 60. This is the global parameter, can also be limited per channel (in GUI)
        maxsecondsperchannel = 60

        #sendreportifprocesserror : do not send a report by mail if only process errors occurred. useful if outcommunication often gives error. default= True (send if there is a process error)
        sendreportifprocesserror = True

        #imap4debug: print detailed information about imap4 session(s). Default 0 (no debug) (can use 0,1,2,3,4,5)
        imap4debug=0

        [webserver]

        #the server_name. Used to distinguish different bots-environments. defaults: bots-webserver
        name = bots-webserver

        #in order to use ssl/https:
        #    - indicate here the file for the ssl_certificate and ssl_private_key. (both can be in the same file)
        #    - uncomment the lines
        #(and of course you will have to make the certificate and private key yourself)
        #self-signed certificates are allowed.
        #ssl_certificate = /path/to/filename
        #ssl_private_key = /path/to/filename


