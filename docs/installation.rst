Installation
============

Bots works on operating systems with python installed. Confirmed is:

* windows (2000, XP, Vista, windows7, Server 2008, Server 2012, etc)
* apple OS.X
* linux debian (ubuntu, mint, etc)
* linux Red hat (Centos. Fedora)
* OpenSolaris
* FreeBSD
* AIX

Let us know if it runs (or not) on another OS.

Dependencies
------------

Always needed
    * Needs: python 2.6/2.7. Python 2.5 works but extra dependencies are needed. Python >= 3.0 does not work.
    * Needs: django >= 1.4.0, django <= 1.7.0
    * Needs: cherrypy > 3.1.0, cherrypy < 9.0

Optional
    * Genshi (when using templates/mapping to HTML).
    * SFTP needs paramiko and pycrypto. Newer versions of paramiko also need ecdsa.
    * Cdecimals speeds up bots. See `website <http://www.bytereef.org/mpdecimal/index.html>`_
    * bots-dirmonitor needs:
    * pyinotify on ``*nix``
    * Python for Windows extensions (pywin) for windows
    * xlrd (when using incoming editype 'excel').
    * mysql-Python >= 1.2.2, MySQL (when using database MySQL).
    * psycopg2, PostgreSQL (when using database PostgreSQL).

Windows installation
--------------------

#. Install Python
    #. Check if Python is already installed.
    #. Use python version 2.6 or 2.7; Python >= 3.0 does not work.
    #. Download Python installer `here <http://www.Python.org>`_.
    #. Install python (double-click).
#. Install bots
    #. Download `bots installer <http://sourceforge.net/projects/bots/files/bots%20open%20source%20edi%20software/>`_.
    #. Install bots (double-click).
    #. Installation takes some time; be patient. During the installation the libraries bots needs are installed.
    #. You will be notified if the installation went OK.
    #. If not: contact us via the `mailing list <http://groups.google.com/group/botsmail/topics>`_.

.. note::

    #. Mind your rights. Both Python and Bots need to be installed as admin (windows vista/7/8).
    #. The windows installer includes all dependencies for standard installation. Some extra dependencies are needed for less used functions (eg. extracting data from excel or pdf files).

\*nix installation
------------------

There is no ``*.deb`` or ``*.rpm`` for bots - would be great if you have experience with this and want to give some help.
So a standard python source code install is done.

#. Install Python
    #. Check if Python is already installed - most of the time python is already installed on ``*nix``. Use python 2.6 or 2.7. (not python >= 3.0).
    #. If not: use package manager or see python web site.
#. Install dependencies/libraries
    * See `list of dependencies <installation.html#dependencies>`_.
    * Easiest is to use your package manager for installing.
#. Install bots
    #. Download `bots installer <http://sourceforge.net/projects/bots/files/bots%20open%20source%20edi%20software/>`_ (e.g. bots-3.1.0.tar.gz)
    #. Unpack (command-line): ``tar bots-3.1.0.tar.gz``
    #. Go to created directory (command-line): ``cd bots-3.1.0``
    #. Install (command-line): ``python setup.py install``    
    #. Postinstall: depending on what do want: change rights for directories botssys, usersys and config or place these elsewhere and make symbolic links in the bots installation directories.

.. note::
    Place the directories botssys, usersys and config somewhere else (out of /usr), change the owner/rights and make symbolic links in the bots installation to these directories.

**Installation from scratch**

Installation on amazon EC2, looks like red hat version of linux 
(Note that versions might not be correct anymore)

    .. code-block:: console

        #install django
        $ wget -O django.tar.gz https://www.djangoproject.com/download/1.4.13/tarball/
        $ tar -xf django.tar.gz
        $ cd Django-1.4.13
        $ sudo python setup.py install
        $ cd ..      
        #install cherrypy
        $ wget http://download.cherrypy.org/CherryPy/3.2.2/CherryPy-3.2.2.tar.gz
        $ tar -xf CherryPy-3.2.2.tar.gz
        $ cd CherryPy-3.2.2
        $ sudo python setup.py install
        $ cd ..      
        #install Genshi
        $ wget http://ftp.edgewall.com/pub/genshi/Genshi-0.7.tar.gz
        $ tar -xf Genshi-0.7.tar.gz
        $ cd Genshi-0.7
        $ sudo python setup.py install
        $ cd ..      
        #install bots
        $ wget -O bots-3.1.0.tar.gz http://sourceforge.net/projects/bots/files/bots%20open%20source%20edi%20software/3.1.0/bots-3.1.0.tar.gz/download
        $ tar -xf bots-3.1.0.tar.gz
        $ cd bots-3.1.0
        $ sudo python setup.py install
        $ cd .. 
        #set rigths for bots directory to non-root:
        $ sudo chown -R myusername /usr/lib/python2.6/site-packages/bots
 
        #start up bots-webserver:
        $ bots-webserver.py

**Installation from scratch (bots2.2)**

Installation on vanilla CentOS6.2 (logged in as root)
(Note that versions might not be correct anymore):

    .. code-block:: console

        #install django
        wget http://www.djangoproject.com/download/1.3.1/tarball/
        tar -xf Django-1.3.1.tar.gz
        cd Django-1.3.1
        python setup.py install
        cd ..      
        #install cherrypy
        wget http://download.cherrypy.org/CherryPy/3.2.2/CherryPy-3.2.2.tar.gz
        tar -xf CherryPy-3.2.2.tar.gz
        cd CherryPy-3.2.2
        python setup.py install
        cd ..      
        #install Genshi
        wget http://ftp.edgewall.com/pub/genshi/Genshi-0.6.tar.gz
        tar -xf Genshi-0.6.tar.gz
        cd Genshi-0.6
        python setup.py install
        cd ..      
        #install bots
        wget http://sourceforge.net/projects/bots/files/bots%20open%20source%20edi%20software/2.2.1/bots-2.2.1.tar.gz/download
        tar -xf bots-2.2.1.tar.gz
        cd bots-2.2.1
        python setup.py install
        cd .. 
     
        #start up bots-webserver:
        bots-webserver.py

FAQ
---

1. I try to install bots at Windows Vista/7, but.....
    * Probably a rights problem - you'll have to have administrator rights in order to do a proper install.
    * Right click the installer program, and choose 'Run as Administrator'.
    * Bots works on Vista/7/8!
    * sometimes the shortcut is not installed in the menu, and you will have to make this manually. See StartGetBotsRunning
2. Does bots have edifact and x12 messages installed out-of-the-box?
    * No. But this can be downloaded on the sourceforge site either as part of a working configuration (plugin) of separate (grammars).
3. Bots is not working on linux - rights problems.
    * Start bots-webserver and bots-engine with sufficient rights - e.g. as root.
    * Change the owner/rights of the files in botssys, usersys and config; run bots-webserver/bots-engine without root rights.
4. **During windows installation; Error**:

    .. code-block:: console 

        close failed in file object destructor:
        sys.excepthook is missing
        lost sys.stderr

    * seems to happen when UAC is turned off.
    * Actually bots just seems to be installed OK, and works OK.....
    * Fixed this in version 3.2
