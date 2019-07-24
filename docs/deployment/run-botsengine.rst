Running Bots-Engine
===================

Options for running bots-engine:

#. Run automatic or manual
    * Manual runs by using the ``run`` options in the menu.
    * `Schedule <#scheduling-bots-engine>`_ Bots-Engine.
    * Use the `directory monitor/watcher <#directory-monitor-bots-3-0>`_.
    * This can be combined; eg
        * schedule ``new`` every 15minutes
        * manually ``rereceive`` and ``resend``
#. Direct or via `jobqueue-server <#job-queue-server-bots-3-0>`_.
#. Specify the routes to run:
    * Run all routes. Default way of running (nothing specified).
    * Run all routes with excludes. Indicate in route if routes ought not to run in a default run.
    * Run specific routes: include route as parameters. Eg (command-line): ``bots-engine.py myroute1 myroute2``
#. Run new or other
    * **new**: Via run-menu or command-line: ``bots-engine.py``
    * **rereceive**: rereceive user indicated edi files. Via run-menu or command-line: ``bots-engine.py --rereceive``
    * **resend**: resend user indicated edi-files. Via run-menu or command-line: ``bots-engine.py --resend``
    * **automaticretrycommunication**: resend edi-files where out-communication failed. Command-line: ``bots-engine.py --automaticretrycommunication``

Scheduling Bots-Engine
----------------------

* Bots does not have a built-in scheduler. Scheduling is done by the scheduler of your OS.
    * Windows: use eg `Windows Task Scheduler <http://support.microsoft.com/kb/308569>`_.
    * Linux/unix: use eg `cron <http://www.linuxhelp.net/guides/cron/>`_. 
* Bots-engine does not run concurrently (in parallel). If a previous run is still in progress, a new run will not start. From version 3.0 onwards, Bots includes an optional `job queue server <#job-queue-server-bots-3-0>`_ to use when scheduling Bots engine. Using this is recommended, to prevent discarding runs that overlap.
* **Strong advice**: when scheduling bots-engine, activate the sending of :doc:`automatic email-reports <email-notifications>` for errors.

.. rubric::
    Possible scheduling scenarios

(command lines below are for Windows):

* If all (or most) routes can be run on the same schedule, then just schedule bots-engine "new" run as often as you need, Eg. every 5 minutes. To exclude some routes from this run, tick the Notindefaultrun box in the route advanced settings. These can then be scheduled separately by specifying route names on the command line.

    .. code-block:: bat

        c:\python27\python c:\python27\Scripts\bots-engine.py --new

        c:\python27\python c:\python27\Scripts\bots-engine.py "my hourly route"

* If you have few routes but with varying schedules, then schedule them individually (by putting route names on the command line). Disadvantage: newly added routes are not automatically run, you must adjust your schedule.

    .. code-block:: bat

        c:\python27\python c:\python27\Scripts\bots-engine.py "my orders route" "my invoice route"

        c:\python27\python c:\python27\Scripts\bots-engine.py "my daily route"

* Consider whether you need to schedule retries periodically. Particularly with accessing remote servers, sometimes there may be communication errors that would be ok next time bots tries. Otherwise you will need to retry these yourself. File errors are not retried automatically because the same error will just come up again!

    .. code-block:: bat

        c:\python27\python c:\python27\Scripts\bots-engine.py --automaticretrycommunication


.. rubric::
    My Setup (Mike)

I am using Windows task scheduler and Bots `job queue <#job-queue-server-bots-3-0>`_ is enabled. I have five scheduled tasks:

#. Bots-engine (every 5 minutes, 24x7)
#. Bots-engine-hourly (every hour on the hour)
#. Bots-engine-daily (1am daily)
#. Bots-engine-weekly (1am every Monday morning)
#. Bots-engine-monthly (1am first of the month)

Each task has a corresponding batch file in the scripts directory. This makes task configuration and changes easier; the scheduled tasks simply call the batch files. Within the batch files I use job2queue.py for adding jobs. Some add only a single job, while some add multiple jobs. (You could also put the command lines directly into Windows task scheduler, each one as a separate task). I use appropriate priorities for each job, as some times of the day Bots can get very busy. Several examples are shown below.

.. code-block:: bat

    :: bots-engine.bat

    :: Regular run of bots engine (eg. every 5 minutes, highest priority)
    C:\python27\python.exe C:\python27\scripts\bots-job2queue.py -p1 C:\python27\python.exe C:\python27\scripts\bots-engine.py --new

.. code-block:: bat

    :: bots-engine-hourly.bat

    :: Hourly monitoring alerts
    C:\python27\python.exe C:\python27\scripts\bots-job2queue.py -p2 C:\python27\python.exe C:\python27\scripts\bots-engine.py hourly_alerts

    :: Hourly cleanup and low priority routes
    C:\python27\python.exe C:\python27\scripts\bots-job2queue.py -p6 C:\python27\python.exe C:\python27\scripts\bots-engine.py ftp_cleanup ProductionOrders RemitAdvice

    :: automatic retry of failed outgoing communication
    C:\python27\python.exe C:\python27\scripts\bots-job2queue.py -p7 C:\python27\python.exe C:\python27\scripts\bots-engine.py --automaticretrycommunication

.. code-block:: bat

    :: bots-engine-daily.bat

    :: daily housekeeping
    C:\python27\python.exe C:\python27\scripts\bots-job2queue.py -p3 C:\python27\python.exe C:\python27\scripts\bots-engine.py daily_housekeeping

    :: daily reporting &amp; SAP data downloads
    C:\python27\python.exe C:\python27\scripts\bots-job2queue.py -p9 C:\python27\python.exe C:\python27\scripts\bots-engine.py daily_reports SAP_Expired_Contracts

Job Queue Server(bots >= 3.0)
-----------------------------

Purpose of the bots jobqueue is to enable better scheduling of bots engine:

    * ensures only a single bots-engine runs at any time.
    * no engine runs are lost/discarded.
    * next engine run is started as soon as previous run has ended.

Use of the job queue is optional, but is recommended if `scheduling bots-engine <#scheduling-bots-engine>`_.


Details:

* Launch sequence from the queue can be controlled using different priorities when adding jobs.
* Other (non bots-engine) jobs can also be added to the queue if they need to be run **in between** bots-engine runs.
* If you add a duplicate of another job **already waiting on the queue** the request is discarded. This is because the job on the queue will perform the same action when it runs. If that job is already running, the new job **will** be added to the queue.
* Logging in ``bots/botssys/logging/jobqueue.log``
* When using Bots monitor run-menu the job queue will be used if enabled in bots.ini; jobs are added with default priority of 5.
* In production you'll probably want to run bots-jobqueueserver as a :doc:`daemon process/service <run-as-service>`.
* Full command-line usage instructions for bots-job2queue.py and bots-jobqueueserver.py when started up with ``--help``
* The bots job queue server does 3 things
    * maintains a queue of jobs for bots-engine.
    * receives new jobs via the ``bots-job2queue.py`` (or via ``bots-monitor->Run``)
    * launches a new job from the queue as soon as previous job ended.



.. rubric::
    Starting with the job queue

#. First, enabled in `bots.ini <../overview/configuration-files.html#bots-ini>`_ (jobqueue section, ``enabled = True``).
#. Start the bots-jobqueueserver. Command-line: ``bots-jobqueueserver.py``.
#. Put jobs in the job queue:
    * via menu using ``bots-monitor->Run``
    * start from command-line (using ``bots-job2queue.py``).
    * start from scheduler (using ``bots-job2queue.py``).


**Command examples**
    
    Job2queue on windows example 1:

    .. code-block:: bat

        c:\python27\python c:\python27\Scripts\bots-job2queue.py c:\python27\python c:\python27\Scripts\bots-engine.py

    Job2queue on windows example 2:

    .. code-block:: bat 

        c:\python27\python c:\python27\Scripts\bots-job2queue.py -p3 c:\python27\python c:\python27\Scripts\bots-engine.py --new -Cconfigprod

    Job2queue on windows example  3 (Adding other commands to the job queue):

    .. code-block:: bat

        c:\python27\python c:\python27\Scripts\bots-job2queue.py c:\program files\my_program.exe my_parm_1 my_parm_2

    Job2queue on linux example 4:

    .. code-block:: bat

        bots-job2queue.py bots-engine.py

    Job2queue on linux example 5:

    .. code-block:: bat

        bots-job2queue.py -p3 bots-engine.py --new -Cconfigprod

Directory Monitor (bots >= 3.0)
-------------------------------

This provides a method of monitoring specific **local** directories, and running Bots engine when files are ready to be processed.

Use of the directory monitor is optional. It may be useful for processing files that only arrive occasionally and at random times.

**Prerequisites**

* Directory monitor uses the `job queue <#job-queue-server-bots-3-0>`_.
* Monitoring must be configured in `bots.ini <../overview/configuration-files.html#bots-ini>`_ (``dirmonitorX`` sections)
* Directory monitor :doc:`daemon process <run-as-service>` must be started (``bots-dirmonitor.py``)

Return codes for bots engine (bots>=3.0)
----------------------------------------
Bots-engine uses the following return codes:

* 0: OK, no errors.
* 1: (system) errors: could not connect to database, not correct command line arguments, database damaged, unexpected system error etc.
* 2: bots ran OK, but there are errors/process errors in the run.
* 3: Database is locked, but **maxruntime** has not been exceeded. (use the job queue server to avoid this type of errors).

Return code **2** is similar/equivalent to the error reports by email.
