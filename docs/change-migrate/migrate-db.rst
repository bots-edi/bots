Migrate Database
================

If you choose to use :doc:`another database <../advanced-deployment/use-mysql>` rather than SQLite, you may want to migrate some or all of your data. You may also migrate data between development and production environments. There are several approaches to this, depending on your needs.

* Migrate all configuration and transactional data
* Migrate only the configuration, start fresh with transactional data
* Migrate only partial configuration (eg. adding a new route, channels and translation)

Depending on the approach and the amount of data, several methods could be used.

* Using bots :doc:`plugin <../plugins/index>` mechanism (write plugin, read plugin)
    * Simple, good for configuration
    * Works independently of underlying database in use
    * **Disadvantage**: very slow (or fails with memory error) for large volumes of transactional or code-conversion data.
* Using bots :doc:`plugin <../plugins/index>` mechanism, and "editing" the plugin
    * Plugins are just zip files, you can open them with any zip tool
    * Use a tool that allows you to edit files within the zip and re-save them (eg. `IZArc <http://www.izarc.org/>`_ works for this)
    * Alternatively, unzip the whole directory structure, make your changes, then zip it again. Make sure the same structure is kept.
    * Plugin contains all configuration, you can remove files that are not required (eg. usersys files)
    * The file ``botsindex.py`` contains all of the database configuration. You can edit this file and delete records not required. Be careful to keep linked records (eg. channels used by a route). The layout of this file is not very user-friendly, you will need to use "find" in your editor a lot! Records are grouped by type, do not re-arrange their sequence.
* Using SQL (dump, insert)
    * If you have a large volume of data to migrate, this will probably be faster.
    * add details of how to do this here (I am testing this)
    * Additional information here http://www.redmine.org/boards/2/topics/12793.
