Multiple Environments
=====================

There is more than one way of configuring multiple environments.
Directories relevant for separate environments are:

* ``bots/config``: global configuration; eg values for usersys, botssys, database connection, port number.
* ``bots/botssys``: storage of edi files, database, loggings etc.
* ``bots/usersys``: grammars, mappings, route scripts etc.

Use config parameter
--------------------

    Each bots program *start script* accepts a parameter (-c) that indicates which config directory to use. Within config there are settings for botssys and usersys, so this gives us the ability to have separate environments. The default, if this parameter is not used, is **config**.

    **By example**:

    #. Start with configuration with the default ``config``, ``usersys`` and ``botssys`` directories in bots directory.
    #. Purpose is to create a 2nd environment (env2).
    #. Make copies of 3 directories within bots directory. Advised is to use the same name-suffix:
        * Make copy of ``config``, name it ``config-env2``
        * Make copy of ``botssys``, name it ``botssys-env2``
        * Make copy of ``usersys``, name it ``usersys-env2``
    #. Edit the configuration files in ``config-env2`` and change (at least) the following settings:
        * in bots.ini
    
            .. code::

                botssys = botssys-env2
                usersys = usersys-env2 

        * settings.py

            ``DATABASE_NAME = os.path.join(PROJECT_PATH, 'botssys-env2/sqlitedb/botsdb')``

    #. Start bots scripts using the -c parameter to refer to the new environment, eg:
        
        .. code:: console

            $ bots-webserver.py -cconfig-env2
            $ bots-engine.py -cconfig-env2

    .. note::
        On linux the use of symlinks in bots directory might be useful.

Use different computers
-----------------------

    * Your production environment is on a server.
    * Your development environment is on your desktop/laptop PC.
    * In this way, you can replicate exactly the same setup (same python version etc), and transfer things from one to the other once tested.

Using different python installations
------------------------------------

    * I used this for a long time for windows.
    * I had python2.5 and 2.6 installed; Bots in python 2.6 was my development environment; bots in python 2.5 was production.
    * This is a very simple way to have 2 environments in windows.

Using python virtualenv tool
----------------------------

    * `virtualenv <https://pypi.python.org/pypi/virtualenv>`_ is a tool to create isolated Python environments.
    * Each environment has a separate installation of bots and its dependencies, so different versions can be tested. 
    * You can activate and deactivate the environments as needed. 
    * You can use in combination with method 1 to have *config environments within python environments*.

    **Installation**

    #. Install python: You have probably done this already! Make sure you have the paths of your ``python27`` and ``python27\scripts`` included in the `system path variable <http://en.wikipedia.org/wiki/PATH_%28variable%29>`_.

    #. Install distribute: Download `distribute_setup.py <http://python-distribute.org/distribute_setup.py>`_ and invoke it using python.

        ``>> python C:\Path\to\distribute_setup.py``

    #. Install Pip: Download `get-pip.py <https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_ (right click, save as) and invoke it using python.

        ``>> python C:\Path\to\get-pip.py``

    #. Install Virtualenv: Once Pip is installed, installing any other package (that is available in the Python Package Index) is easy.

        ``>> pip install virtualenv``
    #. Install C and C++ compilers (optional): 

        * Not all python libraries are pure python, some may contain C code that must be compiled to install successfully. 
        * Download `MinGW <http://sourceforge.net/projects/mingw/>`_, run it, and select the C and C++ compilers to install. 
        * When complete, edit the file ``Python27\Lib\distutils\cygwincompiler.py`` and remove ``-mno-cygwin`` from lines ``322-326``. 
        * This flag is no longer supported. 
        * You also need to add a setting to each virtual environment that needs to use the compilers (described in the next section). 
        * Make sure you have the path of your ``MinGW\bin`` included in the `system path variable <http://en.wikipedia.org/wiki/PATH_%28variable%29>`_.

    **Create your environments**

    Technically your virtual environments can be stored and scattered anywhere, but it makes sense to keep them all grouped together. I suggest you create a "root" directory for environments, each environment will be a subdirectory, eg.

    .. code::

        D:\> mkdir PythonEnv
        D:\> cd PythonEnv
        D:\PythonEnv>

    Create as many environments as you need (for ease of use, keep environment names short but meaningful and without spaces), eg. bots310

    .. code::

        D:\PythonEnv> virtualenv bots310
        New python executable in bots310\Scripts\python.exe
        Installing Setuptools...........................................................
        ............................done.
        Installing Pip..................................................................
        .......................done.

        D:\PythonEnv>

    If you installed compilers in the previous section and want to use them for this environment, then edit Lib\distutils\distutils.cfg within the environment folder, and add

    .. code::

        [build]
        compiler=mingw32

    **Activate and deactivate environments**

    To activate an environment, use the activate command in it's script directory. Notice your command prompt changes to show the active environment in brackets. Only one environment can be **activated** at a time, in order to install modules etc.

    .. code::
    
        D:\PythonEnv> bots310\scripts\activate
        (bots310) D:\PythonEnv>
    
    To deactivate the current environment, use the deactivate command. Notice your command prompt changes back to show no active environment in brackets.

    .. code::

        (bots310) D:\PythonEnv> deactivate
        D:\PythonEnv>
    
    Optional; create an ``activate.bat`` file in your environment root directory. This gives you a shortcut to activate environments.

    .. code::

        REM activate.bat gives you a shortcut to activate python environments
        REM eg. activate bots310
        call "%1\scripts\activate"

    **Install Bots in a virtual environment**

    First, activate the required environment.
    Install Bots and dependencies using pip (don't use the Bots Windows installer, because it installs to the default python folder!)

    * Install Bots from local downloaded .tar.gz file
    
        .. code:: console

            (bots310) D:\PythonEnv> pip install .\bots-3.1.0.tar.gz
            Unpacking d:\pythonenv\bots-3.1.0.tar.gz
              Running setup.py egg_info for package from file:///d7C%5Cpythonenv%5Cbots-3.1.0.tar.gz

            Installing collected packages: bots
              Running setup.py install for bots

            Successfully installed bots
            Cleaning up...

            (bots310) D:\PythonEnv>
        
    * Install Django (version 1.4.x)
    
        .. code:: console
    
            (bots310) D:\PythonEnv>pip install Django==1.4.6
            Downloading/unpacking Django==1.4.6
              Downloading Django-1.4.6.tar.gz (7.7MB): 7.7MB downloaded
              Running setup.py egg_info for package Django

            Installing collected packages: Django
              Running setup.py install for Django

            Successfully installed Django
            Cleaning up...

            (bots310) D:\PythonEnv>
        
    * Install cherrypy (latest)
    
        .. code:: console
    
            (bots310) D:\PythonEnv> pip install cherrypy
            Downloading/unpacking cherrypy
              Downloading CherryPy-3.2.4.tar.gz (424kB): 424kB downloaded
              Running setup.py egg_info for package cherrypy

            Installing collected packages: cherrypy
              Running setup.py install for cherrypy

            Successfully installed cherrypy
            Cleaning up...

            (bots310) D:\PythonEnv>
        
    * Install Genshi (optional, required for template-html output)
    
        .. code:: console
    
            (bots310) D:\PythonEnv> pip install Genshi
            Downloading/unpacking Genshi
              You are installing a potentially insecure and unverifiable file. Future versions of pip will default to disallowing insecure files.
              Downloading Genshi-0.7.tar.gz (491kB): 491kB downloaded
              Running setup.py egg_info for package Genshi

                warning: no files found matching 'COPYING' under directory 'doc'
                warning: no previously-included files matching '*' found under directory 'doc\logo.lineform'
                warning: no previously-included files found matching 'doc\2000ft.graffle'
                warning: no previously-included files matching '\*.pyc' found anywhere in distribution
            Installing collected packages: Genshi
              Running setup.py install for Genshi
                building 'genshi._speedups' extension
                C:\MinGW\bin\gcc.exe -mdll -O -Wall -ID:\Python27\include -ID:\PythonEnv\bots310\PC -c genshi/_speedups.c -o build\temp.win32-2.7\Release\genshi\_speedups.o
                C:\MinGW\bin\gcc.exe -shared -s build\temp.win32-2.7\Release\genshi\_speedups.o build\temp.win32-2.7\Release\genshi\_speedups.def -LD:\Python27\Libs -LD:\PythonEnv\bots310\libs -LD:\PythonEnv\bots310\PCbuild -lpython27 -lmsvcr90 -obuild\lib.win32-2.7\genshi\_speedups.pyd

                warning: no files found matching 'COPYING' under directory 'doc'
                warning: no previously-included files matching '\*' found under directory 'doc\logo.lineform'
                warning: no previously-included files found matching 'doc\2000ft.graffle'
                warning: no previously-included files matching '\*.pyc' found anywhere in distribution
            Successfully installed Genshi
            Cleaning up...

            (bots310) D:\PythonEnv>
        
    * Install cdecimal (optional, improves :doc:`performance <../advanced-deployment/performance>`)
    
        This will not install/compile correctly on Windows using pip, and the installer is an msi (not exe) so easy_install won't work either. You can install it manually though; the two files needed are ``cdedimal.pyd`` and ``cdecimal-2.3-py2.7.egg-info`` and they go in your virtual environment's ``site-packages`` directory. There are two ways to get these files.

            * Install cdecimal in the default python folder (eg. ``C:\python27\lib\site-packages``) using the windows msi installer, then copy the two files to your virtual environment.
            * Extract the files from the windows msi installer using a tool such as `universal extractor <http://www.lupopensuite.com/db/universalextractor.htm>`_.
        
    * Install pycrypto and paramiko (optional, required for sftp channels)
    
        These will not install/compile correctly on Windows using pip. Instead, I used easy_install with a downloaded Windows installer exe.
    
        .. code:: console
    
            (bots310) C:\PythonEnv>easy_install pycrypto-2.1.0.win32-py2.7.exe

            Processing pycrypto-2.1.0.win32-py2.7.exe
            creating 'c:\docume~1\adadmi~3\locals~1\temp\1\easy_install-wy9qt4\pycrypto-2.1.
            0-py2.7-win32.egg' and adding 'c:\docume~1\adadmi~3\locals~1\temp\1\easy_install
            -wy9qt4\pycrypto-2.1.0-py2.7-win32.egg.tmp' to it
            Moving pycrypto-2.1.0-py2.7-win32.egg to c:\pythonenv\bots310\lib\site-packages
            Adding pycrypto 2.1.0 to easy-install.pth file

            Installed c:\pythonenv\bots310\lib\site-packages\pycrypto-2.1.0-py2.7-win32.egg
            Processing dependencies for pycrypto==2.1.0
            Finished processing dependencies for pycrypto==2.1.0

            (bots310) C:\PythonEnv>easy_install paramiko-1.7.6.win32.exe

            Processing paramiko-1.7.6.win32.exe
            creating 'c:\docume~1\adadmi~3\locals~1\temp\1\easy_install-mwtlnu\paramiko-1.7.
            6-py2.7-win32.egg' and adding 'c:\docume~1\adadmi~3\locals~1\temp\1\easy_install
            -mwtlnu\paramiko-1.7.6-py2.7-win32.egg.tmp' to it
            Moving paramiko-1.7.6-py2.7-win32.egg to c:\pythonenv\bots310\lib\site-packages
            Adding paramiko 1.7.6 to easy-install.pth file

            Installed c:\pythonenv\bots310\lib\site-packages\paramiko-1.7.6-py2.7-win32.egg
            Processing dependencies for paramiko==1.7.6
            Finished processing dependencies for paramiko==1.7.6

    **Start Bots Webserver in the virtual environment**

    You can simply start the webserver manually from commandline. The variable ``%VIRTUAL_ENV%`` contains the path to the activated environment. Using the start command causes a new console window to be opened.

    ``(bots310) D:\PythonEnv> start python %VIRTUAL_ENV%\scripts\bots-webserver.py``

    Alternatively you can modify the environment's activate command (it is a small batch file of about 25 lines). Edit ``%VIRTUAL_ENV%\scripts\activate.bat`` and add the above command to the end. Then every time you activate the environment, the webserver is started too. Same for jobqueueserver (if required). I also add a window title. eg.

    ``start "webserver (bots310)" python %VIRTUAL_ENV%\scripts\bots-webserver.py``

    **Running multiple Bots environments concurrently**

    **Yes**, this is possible. Although only a single environment can be "activated", 
    once they are created you can run multiple bots webservers and engines simultaneously from different environments, if configured with different ports.

    *bots.ini* - use different ports for each environment. eg.

    .. code:: python

        [settings]
        #port used to assure only one instance of bots-engine is running. default: 28081
        port = 28091

        [webserver]
        #port at which at bots-gui is server. default is 8080
        port = 8090

        [jobqueue]
        # Port to use for the job queue xmlrpc server (on localhost). Default: 28082
        port = 28092

    *settings.py* - add new setting for the session cookie name, and use a different name for each environment. This allows simultaneous login to each environment from the same browser. eg. use the environment name (default is ``sessionid``)

    .. code:: python

        #*********sessions, cookies, log out time*************************
        SESSION_COOKIE_NAME = 'bots310'
