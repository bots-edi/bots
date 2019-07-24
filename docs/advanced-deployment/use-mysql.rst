Use MySQL or PostgreSQL as Database
===================================

* Default bots uses a SQLite database. This is included in the standard installation and works out-of-the-box. Performance of SQLite is good!
* Bots always uses ``utf-8`` in the database communication.
* Database tables are installed using ``django-machinery``. See django docs.
* After installation, you may want to :doc:`migrate some data <../change-migrate/migrate-db>`.
* You might have to manually add a database trigger if using :doc:`persist <../configuration/mapping-scripts/persist>` functions.

PostgreSQL
----------

#. Install PostgreSQL.
#. Install ``psycopg2`` as python database adapter.
#. Login in command line client of database.
#. Create database (CLI) : ``CREATE DATABASE botsdb WITH ENCODING 'UTF8';``
#. Create user (CLI): ``CREATE USER bots WITH PASSWORD 'botsbots';``
#. Give user rights (CLI): ``GRANT ALL PRIVILEGES ON DATABASE botsdb TO bots;``
#. make sure database accepts connections over (non-local) TCP/IP: change parameter ``listen_addresses`` in ``postgresql.conf``; add/change setting for user in ``pg_hba.conf``.
#. Set connection parameter in bots configuration in ``bots/config/settings.py``. Examples are provided - see comments in ``settings.py``
#. Create the required tables (CLI):
    * <CLI>: ``django-admin syncdb --settings='bots.config.settings``
    * Or when bots is not installed in the default directory <CLI>: ``django-admin syncdb --pythonpath='path to bots' --settings='bots.config.settings'``
    * Django asks for name etc of default user.

MySQL
-----

#. Install MySQL.
#. Install ``mysql-Python`` as python database adapter.
#. Login in command line client of database.
#. Create database (CLI): ``CREATE DATABASE botsdb DEFAULT CHARSET utf8;``
#. Create user (CLI): ``CREATE USER 'bots' IDENTIFIED BY 'botsbots';``
#. Give user rights (CLI): ``GRANT ALL PRIVILEGES ON botsdb.* TO 'bots';``
#. Make sure database accepts connections over (non-local) TCP/IP: change parameter ``binds`` in ``/etc/mysql/my.cfg``.
#. Set connection parameter in bots configuration in ``bots/config/settings.py``. Examples are provided - see comments in ``settings.py``
#. Create the required tables:
    * <CLI>: ``django-admin syncdb --settings='bots.config.settings'``
    * Or when bots is not installed in the default directory <CLI>: ``django-admin syncdb --pythonpath='path to bots' --settings='bots.config.settings'``
    * Django asks for name etc of default user.

MySQL on Windows
----------------

#. Download `MySQL community server <http://www.mysql.com/downloads/mysql/>`_ msi installer. (tested version 5.5.20)
#. Run the installer, do a **typical** installation and follow the prompts. On the final screen, make sure *Launch the MySQL Instance Configuration Wizard* box is ticked.
#. When the configuration wizard starts, make the following selections:
    * Detailed configuration
    * Server machine (you may choose developer for your bots test environment)
    * Transactional database
    * DSS/OLAP (20 connections)
    * Enable TCP/IP and Strict mode (defaults)
    * Best support for multilingualism (**UTF8**)
    * Install as Windows service (default)
    * Modify security settings; enter a root password and write it down.
    * Execute configuration
    * Create a shortcut to ``C:\Program Files\MySQL\MySQL Server 5.5\bin\MySQLInstanceConfig.exe`` in case you want to modify any of these settings later.
#. Go to ``Start > Programs > MySQL > MySQL Server > MySQL Command Line Client``. Enter your root password when prompted. You should now have a ``mysql>`` command prompt.
#. Enter the following MySQL commands at the prompt:

    .. code::

        mysql> CREATE DATABASE botsdb DEFAULT CHARSET utf8;
         Query OK, 1 row affected (0.01 sec)

        mysql> CREATE USER 'bots' IDENTIFIED BY 'botsbots';
         Query OK, 0 rows affected (0.00 sec)

        mysql> GRANT ALL ON botsdb.* TO 'bots';
         Query OK, 0 rows affected (0.03 sec)

#. Download and install `MySQL-python for Windows <http://www.codegood.com/downloads>`_ to suit your python version (tested ``MySQL-python-1.2.3.win32-py2.7.exe``)
#. Set connection parameters in bots configuration in ``bots/config/settings.py``. MySQL example is provided, I only changed HOST.

    .. code:: python

        #MySQL:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'botsdb',
                'USER': 'bots',
                'PASSWORD': 'botsbots',
                'HOST': 'localhost',  #database is on same server as Bots
                'PORT': '3306',
                'OPTIONS': {'use_unicode':True,'charset':'utf8','init_command': 'SET storage_engine=INNODB'},
                }
            }

#. Create the required tables from a command prompt. Django asks for name etc of superuser. (enter user: bots, password: botsbots)

    .. code:: console

        > D:\python27\python.exe D:\Python27\lib\site-packages\django\bin\django-admin.py syncdb 
          --settings=bots.config.settings

        Creating tables ...
        Creating table auth_permission
        Creating table auth_group_permissions
        Creating table auth_group
        Creating table auth_user_user_permissions
        Creating table auth_user_groups
        Creating table auth_user
        Creating table auth_message
        Creating table django_content_type
        Creating table django_session
        Creating table django_admin_log
        Creating table confirmrule
        Creating table ccodetrigger
        Creating table ccode
        Creating table channel
        Creating table partnergroup
        Creating table partner
        Creating table chanpar
        Creating table translate
        Creating table routes
        Creating table filereport
        Creating table mutex
        Creating table persist
        Creating table report
        Creating table ta
        Creating table uniek

        You just installed Django's auth system, which means you don't have any superusers defined.
        Would you like to create one now? (yes/no): yes
        Username (Leave blank to use 'mike'): bots
        E-mail address: bots@bots.com
        Password: botsbots
        Password (again): botsbots
        Superuser created successfully.
        Installing custom SQL ...
        Installing indexes ...
        No fixtures found.

#. Now start bots-webserver and log in as bots.

.. note::

    The database is stored in C:/ProgramData/MySQL/MySQL Server 5.5/Data/ by default (on Windows 7). To move the database, do the following

    #. Stop the MySQL service
    #. Move the ``/Data/`` folder only to your required location (eg. ``D:/MySQL Server 5.5/Data/``)
    #. Make sure the permissions are moved with it. ``NETWORK SERVCE`` must have full control
    #. Change the setting ``datadir`` in ``C:/ProgramData/MySQL/MySQL Server 5.5/my.ini`` to indicate the new folder location
        
        .. code::

            # Path to the database root
            datadir=D:/MySQL Server 5.5/Data

    #. Restart the MySQL service. If it will not start, check permissions!
