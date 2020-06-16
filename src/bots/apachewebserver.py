#!/usr/bin/env python
# -*- coding: utf-8 -*-


#bots-modules
from . import botsglobal
from . import botsinit
''' This source file starts up bots monitor when using apache2 as webserver.

WSGI SCRIPT EXAMPLE (outside bots directory, imports and starts this script apachewebserver.py):
import sys
import django.core.handlers.wsgi
import mod_wsgi

#Set PYTHONPATH. This is not needed if bots is already on PYTHONPATH
#sys.path.append('/usr/local/lib/python2.7/dist-packages')
from bots import apachewebserver

config = mod_wsgi.process_group
apachewebserver.start(config)
application = django.core.handlers.wsgi.WSGIHandler()
'''
'''
APACHE CONFIG FILE EXAMPLE:
WSGIScriptAlias /    <wsgi script>
Alias /media    <media directory>

Listen 8080
NameVirtualHost *:8080
<VirtualHost *:8080>
WSGIDaemonProcess config user=xxxxx
WSGIProcessGroup config
</VirtualHost>
'''


def start(configdir):
    botsinit.generalinit(configdir)  # find locating of bots, configfiles, init paths etc.
    process_name = 'apache_webserver_' + configdir
    # initialise file-logging for web-server. This logging only contains the logging from bots-webserver.
    botsglobal.logger = botsinit.initserverlogging(process_name)
