Configuration Change Management
===============================

Having different environments for at least test and production is a sound IT practice.
But having different environments also brings problems:

* push changes in a controlled way to production-environment
* are changes done right, and does the existing configuration still run right?
* keep test-environment in line with production-environment

To handle these problems bots has some features called *configuration change management*.

**Bots configuration change management**

Configuration change management in bots has 2 aspects:

#. Use `tools <../useful-tools.html#compare-and-merge>`_ for:
    * Comparing differences in configuration of environments
    * Pushing the changes from test->production environment in a controlled, automated way
#. Use of `isolated acceptance test <#isolated-acceptance-testing>`_ to:
    * check if acceptance test runs OK in test
    * check if acceptance test runs OK in production
    * make the test-environment (very) equal to production-environment

Configuration change management works best if both aspects are combined!. See `recipe <#recipe-to-push-test-production>`_ for this.

Isolated Acceptance Testing
---------------------------

    This is a *mode* for testing which is **isolated**:

        * No external communication: all I/O is from/to file system
        * System state does not change (eg no increased counters, no test runs in system, etc)

    Idea is to run an acceptance test without affecting your system (or the system of your edi-partner).

    .. note::
        all plugins since 20130101 are suited for isolated acceptances tests.

    **Advantages**

    #. Isolated acceptance tests are 'repeatable' (because same counters are used, same time is used etc). This is great for testing: each run of a test gives the same results. This makes it easy to compared the results automatically.
    #. By using isolated acceptance tests your test-environment can be equal to production-environment. So you can use standard directory comparison tools to push changes test->production.
    #. As the acceptance tests are isolated, this means an acceptance test can be run in a production-environment without affecting this environment. This way you can verify that after a change, all still runs as before in your production environment.

    **Running isolated acceptance tests**

    * In all channels set ``testpath``. Testpath should point to a directory with test-files.
    * Set option ``runacceptancetest`` in bots.ini to ``True``.
    * Run ``new``
    * Check results of run with what you expect
    * Delete runs/files from acceptance test (menu: ``Systasks->Bulk delete``; select **only** ``Delete transactions in acceptance testing``.)

    **Acceptance tests in plugins**

    Plugins since 20130101 can be run as acceptance tests.
    About the plugins with build-in acceptance test:

    * ``testpath`` for incoming files are in ``botssys\infile``
    * ``testpath`` for outgoing files go to ``botssys\outfile``
    * Each plugin also contains the the expected outgoing files (``botssys\infile\outfile``); these are used to compare the results.
    * Included is a route script (``bots/usersys/routescripts/bots_acceptancetest.py``):
        * **before run**: discard directory ``botssys\outfile``.
        * **after run**: global run results are compared with expectation (#in, #out. #errors, etc)
        * **after run**: compare files in ``botssys\outfile`` with expected files in ``botssys\infile\outfile``
        * the output of these comparisons can be seen in terminal (``dos-box``)

    **Implementation Details**

    * channel-type is set to ``file``.
    * channel-path is set to the value in ``testpath``. if testpath is empty: use path.
    * channel-remove is set to ``off``: no deletion of incoming files.
    * error-email: not send.
    * Fixed date/time in envelopes and in mappings (if function transform.strftime() is used)
    * Counters/references: fixed; counters are not incremented
    * Incoming files are always read in same order.
    * outgoing-filename options: date/time is fixed
    * No archiving
    * Additional user exits are run. User exits are in file ``usersys/routescripts/botsacceptancetest.py``:
        * **before run**: function pretest. use eg to empty out-directories etc
        * **after run**: function post-test. This can be used to check results, compare files etc

    After running an isolated acceptance test, the ``reports/filereports/data-files/etc`` generated during acceptance-testing can be deleted via: ``menu:Systasks->Bulk delete``; select only ``Delete transactions in acceptance testing``.

    .. note::
            * GUI does not have the results of post-test script (runs after automaticmaintanance); view this in terminal/dos-box.
            * Communication scripts: script should check explicitly if in acceptance test and act accordingly.
            * Database communication: script should check explicitly if in acceptance test and act accordingly.


Recipe to push *test->production*
---------------------------------

    Recipe to use a standard `directory comparison tool <../useful-tools.html#compare-and-merge>`_ to manage the differences in configuration between test and production:

    #. For both environments, make configuration index file (``menu->Systasks->Make configuration index``)
    #. Compare both environments using a `directory comparison tool <../useful-tools.html#compare-and-merge>`_. What you should compare is:
        * All files in ``bots/usersys``.
        * Note that the file ``bots/usersys/index.py`` contains the configuration as in the database (routes, channels, partners).
    #. Push changes using the tool.
    #. And read the configuration index file (``menu->Systasks->Read configuration index``) to the database.

    **Details**

    #. If the configuration index file is generated all configuration is in usersys (routes, mappings, partners etc).
    #. By using the *isolated acceptance test* both environments can be **very equal**.
    #. The configuration index file can also be generated by command line tool but cannot be read by command line tool.
    #. Look like it is possible to use a version control system. I have not tried it, but recipes and experiences are welcome!

Build a good test-set
---------------------

    When you do changes in your edi environment, you want to know that every *ran as before*. What can be helpful for this is to use a `isolated acceptance test <#isolated-acceptance-testing>`_ for this.

    This is easy to demonstrate:

    * Download a plugin from `bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_ and install it (not on your production environment;-))
    * In ``config/bots.ini`` set ``runacceptancetest`` to True
    * Run bots-engine via command-line

    **How this works**: in acceptance tests an extra script ``usersys/routescripts/bots_acceptancetest.py`` runs when all routes are finished. This script does 2 things:

    * It compares the results (#files received, errors, send, etc) with the expected results. If results are different you'll see this (on command-line window).
    * The files in ``botssys/infile/outfile`` are compared with files as generated by the run in ``botssys/outfile``. If results are different you'll see this (on command-line window).

    Some things to look at when you build a test-set:

    * Use the ``acceptance test path`` in the channels to point to your file system for incoming and outgoing channels (prevents using communication methods like pop3, ftp, etc).
    * Test file in ``botssys/infile`` are added to plugins (I find this very convenient).
    * Counters (for message numbers, file names etc (via unique()) are the same in every run, so results are the same every run.
    * If date/times need to made, use ``transform.strftime()`` for this; it is like pythons ``time.strftime()`` but gives always the same date/time in acceptance testing.
