Archiving of Files 
==================

* Bots always uses the ``current archive``.
* The current archive is what can be seen in the bots-monitor: incoming files, outgoing files, document view etc.
* Edi-files are kept 30 days in the current archive (by default, can be set via parameter maxdays in ``bots/config/bots.ini``).
* After this time the edi-files and data about their processing (like runs, incoming files, etc) are discarded.


.. rubric::
    Discussion about long term archiving

How long should edi-files be archived? There is no fixed rule about this.
Some argue that the edi-files are temporary information carriers and that the real data is processed and archived in the ERP software of you and your edi-partner.
But:

* for eg invoices there might be legal issues about keeping the 'original invoice'. Check this! (OTOH I get a big smile thinking of legal/tax people wading though these EDI-files. ;-))
* it might be needed to  keep the original in case there are any errors or discrepancies that need to be investigated later.

The (default) 30 days of the current archive is a compromise between **keep all data always** and performance. If all data are kept, performance will degrade in the long run.


The long term archive
---------------------
Bots has an option for a long term archive. This is how it works:

* Per channel: if you specify the 'Archive path' in a channel, all files coming in or going out for that channel are archived.
* for incoming files: archived as received (unchanged); for emails the (un-mimified) attachments are saved.
* for outgoing files: archived as send (unchanged).  If outgoing communication fails: nothing is send,  so nothing is archived.
* The long term archive contains copies of the files only. Once bots has cleaned details from it's database you will need to use tools like 'grep' to find what you need.
* Bots creates a sub-directory per date, eg. myarchive_path/20131202, myarchive_path/20131203, etc. The sub-directories contains the edi-files archived in that day.
* Within this daily directory, Bots uses unique numeric filenames by default.
* Edi-files are kept 180 days in the long term archive (by default, can be set via parameter maxdaysarchive in bots/config/bots.ini). Keeping files longer will not affect performance significantly. Of course the files will occupy disc space.


.. rubric::
    Example of archiving

* Archive path for channel ``my_inchannel`` is set to C:/edi/archive/my_inchannel.
* Archive path for channel ``my_outchannel`` is set to C:/edi/archive/my_outchannel.

After a few days this will looks someting like:

.. code::

    C:/edi/archive/
                  my_inchannel/
                              20131202/
                                      13892848
                                      13892872
                                      13892876
                              20131203/
                                      13892991
                                      13893009
                              20131204/
                                      13893421
                  my_outchannel/
                              20131202/
                                      13892861
                                      13892886
                              20131203/
                                      13893123
                              20131204/
                                      13893479

.. note::
    It is strongly advised to archive the file outside of the bots directories!

.. rubric::
    Additional options for long term archive
    
* archiveexternalname (setting in ``bots/config/bots.ini``). If set to True, name of archived file is the name of the incoming/outgoing file. If this name already exists in the archive: a timestamp is added to the filename; eg. order.txt becomes order_112506.txt. External filenames are only used for some channel types where the channel defines the filename (file, ftp, ftps, ftpis, sftp, mimefile, communicationscript). Default setting in bots.ini is False. New in version 3.0.
* archivezip (setting in ``bots/config/bots.ini``). If set to True, each archive folder will be a zip file.  If you keep archives for a long time, zipping them can save a lot of disc-space;  most EDI files compress to just a few percent of original size. Disadvantage: harder to search. Default setting is False. New in version 3.0.
* user scripting for archive path. See :doc:`communicationscript <../configuration/channel/channel-scripting>`. Note: please archive within the archive path as set in channel, else the cleanup routines for parameter maxdaysarchive will not function.
* user scripting for name of archive file. See :doc:`communicationscript <../configuration/channel/channel-scripting>`.
