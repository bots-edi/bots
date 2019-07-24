Useful Tools
============

These are programs you can use in bots development and deployment. (**please add more**)

Text Editors
------------

Any text editor you use should have syntax colouring/highlighting. This makes it much easier to spot any mistakes. It is also good to be able to run python to do syntax checks. Also a good search/replace function (eg to add extra CR/LF in edifact or x12 files).

* `EditPlus <http://www.editplus.com/index.html>`_ (Windows) is the editor I have used for many years and so continued to use it with Python. There are no python syntax files in the default installation but you can easily `download <http://www.editplus.com/javacpp.html>`_ and add them, several versions are available. You can also add a "user tool" option to run a python syntax check directly in the editor, and one to run the bots grammar check.
* `Scite <http://www.scintilla.org/SciTE.html>`_ (Windows, Linux) provides Python syntax highlighting and python syntax check directly in the editor to check the correctness of Python scripts.
* `Geany <http://www.geany.org/>`_ (Windows, Linux) provides Python syntax highlighting and python syntax check directly in the editor to check the correctness of Python scripts. Quite similar to scite, but more fancy eg with spell checking. Web site calls it an IDE.
* `TextWrangler <http://www.barebones.com/products/textwrangler/>`_ (Mac) provides Python syntax highlighting and python syntax check directly in the editor to check the correctness of Python scripts. Also quite similar to Scite, very interesting access to remote scripts via SSH/SFTP.


IDE (Integrated Development Environment)
----------------------------------------

These are a **step up** from just using a text editor. Please add more if you have anny experience with these.

* `Eclipse <http://www.eclipse.org/downloads/packages/eclipse-ide-java-ee-developers/indigosr2>`_ with `PyDev <http://marketplace.eclipse.org/node/114>`_. You just create a project in the bots directory and edit everything from that folder.

Compare and merge
-----------------

Tool for comparing files and directories, analyse changes and copy code changes eg between test and production environments.

* `Winmerge <http://winmerge.org/>`_ (Windows)
* `Meld <http://meldmerge.org/>`_ (linux)
* `Tkdiff <http://sourceforge.net/projects/tkdiff/>`_ (windows,linux)
* `KDiff3 <http://kdiff3.sourceforge.net/>`_ (linux)

Database
--------

* `SQLite Expert <http://www.sqlite.org/>`_ (Windows, Linux) is a database browser tool for SQLite. Useful for advanced troubleshooting or learning more about Bots internal workings. You can use SQL commands to do quick updates or create reports. Note: I use an old version (1.7) as the newer versions are much larger and slower and offer nothing more useful.
* `HeidiSQL <http://www.heidisql.com/download.php>`_ (Windows) can be used similarly to the above for bots installations using the MySQL database. A lightweight interface for managing MySQL and Microsoft SQL databases. It enables you to browse and edit data, create and edit tables, views, procedures, triggers and scheduled events. Also, you can export structure and data either to SQL file, clipboard or to other servers.
* `MySQL Workbench <http://dev.mysql.com/downloads/workbench/>`_ (multiple platforms) is the full blown MySQL management toolset. It provides an integrated tools environment for Database Design & Modeling, SQL Development (replacing MySQL Query Browser) and Database Administration (replacing MySQL Administrator). The Community (OSS) Edition is available from this page under the GPL.

Other tools
-----------

* `IZArc <http://www.izarc.org/>`_ (Windows) is an archive tool that allows you to open bots plugins (zip files) and easily modify their contents.
* `BareTail <http://www.baremetalsoft.com/baretail/>`_ (Windows) is a free real-time log file monitoring tool. It is useful for watching Bots log files (engine.log, webserver.log etc). Multiple tabbed interface, colour highlighting, single small program, no installer.
