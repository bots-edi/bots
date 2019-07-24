Quick Start Guide
=================

* Purpose of this tutorial is to get your first edi configuration running.
* This is done by installing plugin ``my_first_plugin``; this plugin provides a working configuration.
* When run, this configuration will read and write example edi messages (provided in the plugin) from your system.
* In this configuration incoming edifact orders are translated to a fixed file format.

**Install plugin ``my_first_plugin``**

    #. Assumed is:
        * You've installed bots, see :doc:`../installation`
        * You've managed to get bots-monitor running, see :doc:`get bots running<../get-bots-running>`.
    #. Now download and install plugin ``my_first_plugin``.
    #. Instructions for installing a plugin are :doc:`here <../plugins/install-plugin>`.
    #. The plugin can be downloaded from the `bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_.

**Activate the route**

    #. go to the routes screen: ``bots-monitor->Configuration->Routes``
    #. note that route ``myfirstroute`` is not active now (indicated by red icon)
    #. select the tick-box in front of the route ``myfirstroute``
    #. select action ``activate/de-activate``
    #. click on the 'Go'-button behind the selected action.
    #. note that route ``myfirstroute`` is active now (indicated by green icon)

**Run the translation**

    #. Run the translation: ``bots-monitor->Run->Run (Only New)``.
    #. You will get notified that the ``bots-engine`` is started.
    #. Bots-engine is the part of bots that does the translations and communications; it runs in the background. Bots-engine will be finished in approximately one second.


**View the results**

    Now let's view the results of the translation:

    #. First look at the results of the run: ``bots-monitor->All runs->Reports (per run)``. Each run of bots is represented by a line; the last run is on top.
    #. View the incoming files via ``bots-monitor->Last run->Incoming``. Click on the incoming file to see its contents.
    #. View the outgoing files (the results of the translation) go to or ``bots-monitor->Last run->outgoing``. Again: click on the file name to see its contents.
    #. Note: this configuration reads the incoming files but does not delete them. So you can run it over and over again.


**More**

.. toctree::
   :maxdepth: 2

   view-results
   walkthrough-setup
   what-happened
