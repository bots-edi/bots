#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

try:
    from cheroot.server import get_ssl_adapter_class
    from cheroot.wsgi import WSGIServer as wsgiserver
    from cheroot.wsgi import PathInfoDispatcher as infodispatcher
except ImportError:
    from cherrypy.wsgiserver import get_ssl_adapter_class
    from cherrypy.wsgiserver import CherryPyWSGIServer as wsgiserver
    from cherrypy.wsgiserver import WSGIPathInfoDispatcher as infodispatcher

import cherrypy
import click
import sys

from django.core.handlers.wsgi import WSGIHandler
from django.utils.translation import ugettext as _

from . import botsglobal
from . import botsinit

if sys.version_info[0] > 2:
    basestring = unicode = str


@click.command()
@click.option("--configdir", "-c", default="config", help="path to config-directory.")
def start(configdir):
    """Start the webserver.
    The interface (bots-monitor) can be accessed via browser at e.g 'http://localhost:8080'.
    """

    botsinit.generalinit(
        configdir
    )  # find locating of bots, configfiles, init paths etc.
    process_name = "webserver"
    # initialise file-logging for web-server. This logging only contains the
    # logging from bots-webserver, not from cherrypy.
    botsglobal.logger = botsinit.initserverlogging(process_name)

    # ***init cherrypy as webserver*********************************************
    # global configuration for cherrypy
    cherrypy.config.update(
        {
            "global": {
                "log.screen": False,
                "server.environment": botsglobal.ini.get(
                    "webserver", "environment", "production"
                ),
            }
        }
    )

    # cherrypy handling of static files
    conf = {
        "/": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "media",
            "tools.staticdir.root": botsglobal.ini.get("directories", "botspath"),
        }
    }
    # None: no cherrypy application (as this only serves static files)
    servestaticfiles = cherrypy.tree.mount(None, "/media", conf)
    # cherrypy handling of django
    # was: servedjango = AdminMediaHandler(WSGIHandler())  - django does not need the AdminMediaHandler.
    servedjango = WSGIHandler()
    # cherrypy uses a dispatcher in order to handle the serving of static files and django.
    dispatcher = infodispatcher(
        {"/": servedjango, str("/media"): servestaticfiles}
    )  # UNICODEPROBLEM: needs to be binary

    botswebserver = wsgiserver(
        bind_addr=("0.0.0.0", botsglobal.ini.getint("webserver", "port", 8080)),
        wsgi_app=dispatcher,
        server_name=botsglobal.ini.get("webserver", "name", "bots-webserver"),
    )

    botsglobal.logger.log(
        25, _("Bots %(process_name)s started."), {"process_name": process_name}
    )
    botsglobal.logger.log(
        25,
        _('Bots %(process_name)s configdir: "%(configdir)s".'),
        {
            "process_name": process_name,
            "configdir": botsglobal.ini.get("directories", "config"),
        },
    )
    botsglobal.logger.log(
        25,
        _('Bots %(process_name)s serving at port: "%(port)s".'),
        {
            "process_name": process_name,
            "port": botsglobal.ini.getint("webserver", "port", 8080),
        },
    )

    # handle ssl: cherrypy < 3.2 always uses pyOpenssl. cherrypy >= 3.2 uses
    # python buildin ssl (python >= 2.6 has buildin support for ssl).
    ssl_certificate = botsglobal.ini.get("webserver", "ssl_certificate", None)
    ssl_private_key = botsglobal.ini.get("webserver", "ssl_private_key", None)
    if ssl_certificate and ssl_private_key:
        if cherrypy.__version__ >= "3.2.0":
            adapter_class = get_ssl_adapter_class("builtin")
            botswebserver.ssl_adapter = adapter_class(ssl_certificate, ssl_private_key)
        else:
            # but: pyOpenssl should be there!
            botswebserver.ssl_certificate = ssl_certificate
            botswebserver.ssl_private_key = ssl_private_key
        botsglobal.logger.log(
            25,
            _("Bots %(process_name)s uses ssl (https)."),
            {"process_name": process_name},
        )
    else:
        botsglobal.logger.log(
            25,
            _("Bots %(process_name)s uses plain http (no ssl)."),
            {"process_name": process_name},
        )

    # start the cherrypy webserver.
    try:
        botswebserver.start()
    except (KeyboardInterrupt, SystemExit) as e:  # noqa
        botswebserver.stop()


if __name__ == "__main__":
    start()
