Plugins
=======

* A plugin is a file with predefined configuration for bots. It includes routes, channels, grammars, mappings etc.
* Plugins are installed via ``bots-monitor-Systasks->Read plugin``.
* In order to run the routes in a plugin you first have to activate the routes.
* There are useful plugins on `the bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_.
* :doc:`Documentation <plugins-sourceforge>` for these plugins.

.. note::
    grammars for edifact and x12 are NOT plugins, and can not be installed.

.. rubric::
    For what is a bots plugin useful?

* An easy way to distribute and share edi configurations for bots.
* Learn from existing configurations
* Backup your configuration.
* Share your configuration with others (It would be nice if you want to share your configuration; other can use and/or learn from what you have done!).
* Do another install of the same configuration.
* Transfer your environment from test to production.
* Plugins are used to update to a new version of bots (only between minor versions).

.. note::
    All bots 3.0.0 plugins are suited to use in `acceptance test mode <../advanced-deployment/change-management.html#isolated-acceptance-testing>`_.

.. rubric::
    Index

.. toctree::
    :maxdepth: 2

    install-plugin
    make-plugin
    plugins-explained
    plugins-sourceforge
