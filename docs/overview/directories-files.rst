Directories and Files
=====================

**Where can I find bots on my system?**

* Windows (depends upon python version used):
    * eg. ``C:\python27\Lib\site-packages\bots``
* Linux, Unix:
    * ``/usr/lib/python2.7/site-packages/bots``
    * ``/usr/local/lib/python2.7/dist-packages/bots (Debian, Ubuntu)``

.. note::
    In the main screen (home) of bots-monitor (GUI) you can see where the bots-directories are. 

**Where are the programs/executable scripts?**

* Where installed
    * Windows (depends upon python version used): ``C:\python27\Scripts``
    * Linux, Unix eg in ``/usr/bin/`` or ``/usr/local/bin/``
* Overview of executables:
    * ``bots-webserver.py`` - serves the html-pages for the bots-monitor.
    * ``bots-engine.py`` - does the actual edi communication and translation.
    * ``bots-jobqueueserver.py`` - the jobqueue-server maintains a queue with (job-engine) jobs and fires these asap.
    * ``bots-job2queue.py`` - to send jobs to the jobqueueserver
    * ``bots-dirmonitor.py`` - monitors/watches directoriess; if a file is placed in a directory, bots-engine stats (via jobqueueserver)
    * ``bots-grammarcheck.py`` - utility to check a grammar.
    * ``bots-xml2botsgrammar.py`` - utility to generate an xml-grammar from an xml file.
    * ``bots-updatedb.py`` - for version migrations: updates the database to new definition/schema
    * ``bots-plugoutindex.py`` - for version control systems: generate a file with the configuration (routes, channels, etc). (configuration as in the database).

.. note::
    For the usage instructions of the executables use ``help``, eg:

    ``bots-engine.py --help``

**Where are the edi files?**

* Incoming and outgoing
    * Set this per channel, using 'path' and 'filename'.
    * Relative path is relative to bots directory, absolute paths are OK.
    * In the plugins the edi-files are in ``bots/botssys/infile``
* The archive/backup.
    * each communication channel of bots CAN archive the incoming or outgoing edi messages.
    * Set this per channel, using 'archivepath'.
    * The place of the archive can be 'anywhere'. We mostly use ``botssys/archive``.
* Relative path is relative to bots directory, absolute paths are OK.
    * Internal storage of edi data.
    * in subdirectories of ``bots/botssys/data``.
    * this is where the edi files are fetched from by the bots-monitor (the 'filer' module).
* Cleanup of old files
    * bots manages cleanup of archive and internal storage, based on configuration settings for number of days to keep.
    * Incoming files are (usually, unless testing) removed by the channel setting "remove".
    * Outgoing files are never removed by bots

**The directory structure within bots directory**

* ``bots``: source code (\*.py, \*.pyc, \*.pyo)
    * ``bots/botssys``: data file, database, etc
        * ``bots/botssys``: when installing a plugin bots makes a backup of configuration here.
        * ``bots/botssys/data``: internal storage of edi data.
        * ``bots/botssys/sqlitedb``: database file(s) of SQLite.
        * ``bots/botssys/logging``: log file(s) for each run of bots-engine.
        * ``bots/botssys/infile``: plugins place here example edi data
        * ``bots/botssys/outfile``: plugins place here translated edi data
    * ``bots/config``: configuration files. See also multiple environments.
    * ``bots/install``: contains an empty sqlite database and default configuration files.
    * ``bots/installwin``: (windows) python libraries used during installation.
    * ``bots/locale``: translation/internationalisation files for use of another language.
    * ``bots/media``: static data for bots-webserver (CSS, html, images, JavaScript)
    * ``bots/sql``: sql files for initialising a new database.
    * ``bots/templates``: templates for bots-webserver
    * ``bots/templatetags``: custom template-tags for use in django.
    * ``bots/usersys``: user scripts.
        * ``bots/usersys/charsets``: e.g. edifact uses its own character-sets.
        * ``bots/usersys/communicationscripts``: user scripts for communication (inchannel, outchannel).
        * ``bots/usersys/envelopescripts``: user scripts for enveloping.
        * ``bots/usersys/grammars``: grammars of edi-messages; directories per editype (x12, edifact, tradacoms, etc).
        * ``bots/usersys/mappings``: mappings scripts; directories per editype (incoming).
        * ``bots/usersys/partners``: partner specific syntax for outgoing messages; directories per editype.
        * ``bots/usersys/routescripts``: user scripts for running (part of) route.
        * ``bots/usersys/codeconversions``: for conversions of codes (deprecated).
        * ``bots/usersys/dbconnectors``: user scripts for communication from/to database (old database connector, deprecated).

