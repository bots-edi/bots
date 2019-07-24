User Scripting
==============

Bots has many places (exit points) where user scripting can be used. These user scripts are optional; bots will work without them but they provide great control over functionality for advanced users.

* Channels can have a :doc:`communicationscript <channel/channel-scripting>`
* Routes can have a :doc:`routescript <route/route-scripting>`
* Bots-engine can also have `it's own routescript <#route-script-for-bots-engine>`_.
* Enveloping can be modified with an `envelopescript <split-merge.html#envelope-scripting>`_.

Route Script for Bots-engine
----------------------------

A special routescript called botsengine.py can be added. This is called by the bots-engine at various points. You may wish to use this for your own logging, reporting or cleanup routines.

In Bots v3.2+ There are **pre** and **post** exit points for all runs, and for each type of run (command).

* pre (before any run)
* prenew
* preresend
* prerereceive
* preautomaticretrycommunicationcommunication
* precleanup
* postnew
* postresend
* postrereceive
* postautomaticretrycommunicationcommunication
* postcleanup
* post (after any run)

.. code-block:: python

    # user script example for some bots-engine exit points,
    # showing the passed args.

    # before any run
    def pre(commandstorun,routestorun):
        print 'pre',commandstorun,routestorun

    # before "new" run
    def prenew(routestorun):
        print 'prenew',routestorun

    # after "cleanup" run
    def postcleanup(routestorun):
        print 'postcleanup',routestorun

    # after any run
    def post(commandstorun,routestorun):
        print 'post',commandstorun,routestorun

.. rubric::
    Example of doing something useful with exit points

The **postcleanup** exit point can be used to add your own daily tasks (eg. cleanup, backup or reporting capabilities). 
By default, bots runs a cleanup **once per day** at the end of the first run that day. (setting whencleanup=daily in bots.ini)

This example automatically activates or deactivates partners on the dates you configure for the partner (startdate, enddate)

.. code-block:: python

    import bots.botslib as botslib
    import datetime

    def postcleanup(routestorun):

            # activate any partners with a "start date" of today
            botslib.changeq(u'''UPDATE partner
                                SET active = 1
                                WHERE startdate = %(today)s''',
                                {'today':datetime.datetime.today().strftime('%Y-%m-%d')})

            # deactivate any active partners with an "end date" before today
            botslib.changeq(u'''UPDATE partner
                                SET active = 0
                                WHERE active = 1
                                AND  enddate is not null
                                AND enddate < %(today)s''',
                                {'today':datetime.datetime.today().strftime('%Y-%m-%d')})
