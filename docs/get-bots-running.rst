Get Bots Running
================

Main components of bots
-----------------------

#. Bots-monitor: 
    * The user interface or the GUI. 
    * This is a web interface and runs in a web browser like Firefox, Chrome, or Internet Explorer.
    * Bots uses web technology for the interface - but bots does NOT communicate to the internet for this. All is on your local computer.
    * Bots-monitor can be accessed from all workstations in your LAN.

    .. warning::

        out-of-the-box bots-monitor uses plain HTTP and is not secure. Advised is either:
            * do not use bots-monitor over a public network (such as Internet)
            * secure the connection using :doc:`HTTPS/SSL <advanced-deployment/bots-https>`.
#. Bots-webserver: 
    * Program that serves web pages to bots-monitor. 
    * The bots-webserver has to run in order to use bots-monitor.
#. Bots-engine: 
    * This program does the actual edi communication and translation.
    * Bots-engine does the communications and translations (of eg edifact or x12).
    * Bots-engine has no user interface (is a batch process).
    * To view the results of bots-engine, use bots-monitor.
    * After performing its actions bots-engine stops.

Start bots-monitor (using bots-webserver)
-----------------------------------------

#. Start bots-webserver (several options):
    * When bots is installed using with Windows installer use the 'shortcut' to Bots-webserver in your 'Programs' menu.
    * (\*nix) Command line: ``bots-webserver.py``
    * (Windows, python 2.7) go to command line and: ``c:\python27\python c:\python27\Scripts\bots-webserver.py``
#. Bots-webserver should stay running (and not disappear). If not, see `Start-up FAQ <get-bots-running.html#faq>`_.
#. View using your Internet browser
    * When bots-webserver runs on the same computer, use address: http://localhost:8080
    * use Firefox, Chrome, Opera or Internet Explorer. Bots does NOT support Internet Explorer 6. Issues have been reported with IE8, but for some IE8 does work.
    * When accessing bots-monitor over your LAN (bots-webserver runs on another computer) the IP address or DNS name of that computer, e.g.: ``http://192.168.10.10:8080``.
#. Default login: user name ``bots``, password ``botsbots``.
#. Tip: add ``bots`` to your favorites/bookmarks.

Start bots-engine
-----------------

There are several ways to start bots-engine:

#. (windows, \*nix) Start from bots-monitor: ``bots-monitor->Run->Run (only new)``
#. (\*nix) Command line: ``bots-engine.py``
#. (Windows, python 2.7) go to command line and: ``c:\python27\python c:\python27\Scripts\bots-engine.py``

The results of what bots-engine has done can be viewed in the bots-monitor.

.. note::
    if you did not configure of bots to do something, the bots-engine will run but will not do much. To get bots to do something see Tutorial.

FAQ
---

* When starting bots-webserver the window disappears after a few seconds?
    * Start the bots-webserver from the command line; you will be able to see what goes wrong. (Windows, python 2.7) go to command line and: ``c:\python27\python c:\python27\Scripts\bots-webserver.py``
    * For the most common cause for the problem see the next question.
* Bots-webserver gives error: IOError: Port 8080 not free on 'x.x.x.x' (or similar).
    * Another program already uses this 'port'.
    * Adapt the port bots uses: in configuration file bots/config/bots.ini look for 'port'.
    * Change port to eg 8090
    * Start bots-webserver again.
    * In your browser you will have to indicate another port eg: http://localhost:8090
* Can I run multiple instances of bots-engine in parallel?
    * No, this is not possible.
    * Instead bots >= 3.0 has better control of running the engine: `jobqueue-server <deployment/run-botsengine.html#job-queue-server-bots-3-0>`_.
