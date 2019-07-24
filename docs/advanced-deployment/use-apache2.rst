Use Apache2 as Webserver
========================

* Bots uses cherrypy webserver Out of the Box and in order to scale it, you need to run it on an Apache2 Web Server
* One Advantage is that with this is that apache2 will take care of staring the Bots Monitor so there is no need to create a daemon for the bots webserver.

**Procedure**

#. Ensure that apache2 is installed and running on the system. (try ``httpd -M``)
#. The ``mod_wsgi`` package is needed for this set up, so install it and add the line ``LoadModule wsgi_module modules/mod_wsgi.so`` to apache ``httpd.conf`` file.
#. Restart the apache server, run the command ``httpd -M`` and you should see the ``wsgi_module`` at the end.
#. Now we need to shuffle a few directories, create a base directory called **bots_app** in your home folder (do not run under root)
#. Move the folders **botssys**, **usersys**, **media** and **config** from the bots installation directory to **bots_app** folder. 
#. Do not forget to create sym links for these folders in the installation dir to this new location.
#. Now add the following files to the **bots_app** folder:

    .. code-block:: python

        ##bots.wsgi

        import sys
        import django.core.handlers.wsgi
        import mod_wsgi

        #set PYTHONPATH...not needed if bots is already on PYTHONPATH
        #sys.path.append('/usr/local/lib/python2.7/dist-packages')
        from bots import apachewebserver

        config = mod_wsgi.process_group
        apachewebserver.start(config)
        application = django.core.handlers.wsgi.WSGIHandler()

    .. code-block:: apache 

        ##apache2.conf

        Listen {PORT}
        NameVirtualHost \*:{PORT}
        ## Use this if you run into socket errors on linux
        WSGISocketPrefix /var/run/wsgi

        <VirtualHost \*:{PORT}>
           WSGIScriptAlias /{PATH TO UR HOME}/bots_app/bots.wsgi
           WSGIDaemonProcess config user={System User} group={System User Group}
           WSGIProcessGroup config
   
        ## Use this section only when enabling https for bots app
           SSLEngine on
           SSLCertificateFile /path/to/www.example.com.cert
           SSLCertificateKeyFile /path/to/www.example.com.key

           Alias /media {PATH TO UR HOME}/bots_app/media

           <Directory {PATH TO UR HOME}/bots_app/>
                Order deny,allow
                Allow from all
           </Directory>

           <Directory {PATH TO UR HOME}/bots_app/media>
                Order deny,allow
                Allow from all
           </Directory>

        </VirtualHost>

#. Add execute permission to the ``bots.wsgi`` file and add the line ``Include {PATH TO UR HOME}/bots_app/apache2.conf`` at the end of the apache2 ``httpd.conf`` file.
#. Restart apache server and open ``http://{ip}:{port}/``, you should see the bots welcome screen. If you get permission errors or images are not loading then correct permissions need to be given to **bots_app** and its parent directory.
#. Once the server is running the logs will be generated in the folder ``botssys/logging`` as ``apache_webserver_config.log``
#. The script ``bots-webserver.py`` should **not** be used now as apache2 will automatically start up the application.
#. Add ``botsengine_path = /usr/local/bin/bots-engine.py`` in the Bots ini file.

