#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import click
import os

from . import botsinit
from . import botsglobal


@click.command()
@click.option("--configdir", "-c", default="config", help="path to config-directory.")
def start(configdir):
    """A utility to generate the index file of a plugin;
    this can be seen as a database dump of the configuration.
    This is eg useful for version control.
    """
    botsinit.generalinit(configdir)
    import pluglib  # import here, import at start of file gives error; first initialize.

    usersys = botsglobal.ini.get("directories", "usersysabs")
    index_filename = os.path.join(usersys, "index.py")

    dummy_for_cleaned_data = {
        "databaseconfiguration": True,
        "umlists": botsglobal.ini.getboolean("settings", "codelists_in_plugin", True),
        "databasetransactions": False,
    }

    pluglib.make_index(dummy_for_cleaned_data, index_filename)


if __name__ == "__main__":
    start()
