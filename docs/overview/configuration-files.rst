Configuration Files
===================

* Bots has two configuration files.
* Mostly the defaults will be OK to get started, but you may need to customize these to your own needs.
* Settings are documented in the files.
* Open these files in your :doc:`text editor <../useful-tools>`.
* The configuration files are located in the ``bots/config`` directory (except when using :doc:`multiple environments <../deployment/multiple-environments>`).
* The original default versions can be found in the ``bots/install`` directory.

bots.ini
--------

    * How long to keep edi files and their registration
    * Some GUI customisation settings
    * Timeouts and time limits
    * Logging options
    * Debugging options
    * Webserver settings (eg port)
    * Directory settings

settings.py
-----------

    * Mail server settings for error reports
    * Database settings (eg. to use another database)
    * Security / auto-logout
    * Localization (time zone!)
