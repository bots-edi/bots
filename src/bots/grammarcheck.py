# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import sys

if sys.version_info[0] > 2:
    basestring = unicode = str
import os
import atexit
import glob
import logging

# Bots-modules
from . import botsinit
from . import botslib
from . import grammar
from . import botsglobal
from .botsconfig import *


def startmulti(grammardir, editype):
    """ specialized tool for bulk checking of grammars while developing botsgrammars
        grammardir: directory with gramars (eg bots/usersys/grammars/edifact)
        editype: eg edifact
    """
    configdir = "config"
    botsinit.generalinit(
        configdir
    )  # find locating of bots, configfiles, init paths etc.
    process_name = "grammarcheck"
    botsglobal.logger = botsinit.initenginelogging(process_name)
    atexit.register(logging.shutdown)

    for filename in glob.iglob(grammardir):
        filename_basename = os.path.basename(filename)
        if filename_basename in ["__init__.py", "envelope.py"]:
            continue
        if (
            filename_basename.startswith("edifact")
            or filename_basename.startswith("records")
            or filename_basename.endswith("records.py")
        ):
            continue
        if filename_basename.endswith("pyc"):
            continue
        filename_noextension = os.path.splitext(filename_basename)[0]
        try:
            grammar.grammarread(
                editype, filename_noextension, typeofgrammarfile="grammars"
            )
        except:
            print(botslib.txtexc(), end="\n\n")
        else:
            print("OK - no error found in grammar", filename, end="\n\n")


def start():
    # NOTE: bots directory should always be on PYTHONPATH - otherwise it will not start.
    # ********command line arguments**************************
    usage = """
    This is "%(name)s" version %(version)s, part of Bots open source edi translator (http://bots.sourceforge.net).
    Checks a Bots grammar. Same checks are used as in translations with bots-engine. Searches for grammar in
    regular place: bots/usersys/grammars/<editype>/<messagetype>.py  (even if a path is passed).

    Usage:  %(name)s  -c<directory> <editype> <messagetype>
       or   %(name)s  -c<directory> <path to grammar>
    Options:
        -c<directory>   directory for configuration files (default: config).
    Examples:
        %(name)s -cconfig  edifact  ORDERSD96AUNEAN008
        %(name)s -cconfig  C:/python27/lib/site-packages/bots/usersys/grammars/edifact/ORDERSD96AUNEAN008.py

    """ % {
        "name": os.path.basename(sys.argv[0]),
        "version": botsglobal.version,
    }
    configdir = "config"
    editype = ""
    messagetype = ""
    for arg in sys.argv[1:]:
        if arg.startswith("-c"):
            configdir = arg[2:]
            if not configdir:
                print(
                    "Error: configuration directory indicated, but no directory name."
                )
                sys.exit(1)
        elif arg in ["?", "/?", "-h", "--help"] or arg.startswith("-"):
            print(usage)
            sys.exit(0)
        else:
            if os.path.isfile(arg):
                p1, p2 = os.path.split(arg)
                editype = os.path.basename(p1)
                messagetype, ext = os.path.splitext(p2)
                messagetype = unicode(messagetype)
                print("grammarcheck", editype, messagetype)
            elif not editype:
                editype = arg
            else:
                messagetype = arg
    if not (editype and messagetype):
        print("Error: both editype and messagetype, or a file path, are required.")
        sys.exit(1)
    # ***end handling command line arguments**************************
    botsinit.generalinit(
        configdir
    )  # find locating of bots, configfiles, init paths etc.
    process_name = "grammarcheck"
    botsglobal.logger = botsinit.initenginelogging(process_name)
    atexit.register(logging.shutdown)

    try:
        grammar.grammarread(editype, messagetype, typeofgrammarfile="grammars")
    except:
        print("Found error in grammar: ", botslib.txtexc())
        sys.exit(1)
    else:
        print("OK - no error found in grammar")
        sys.exit(0)


if __name__ == "__main__":
    start()
