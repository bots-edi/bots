# -*- coding: utf-8 -*-


import pkg_resources

#Globals used by Bots
version = pkg_resources.get_distribution('bots').version  # bots version
db = None  # db-object
ini = None  # ini-file-object that is read (bots.ini)
logger = None  # logger or bots-engine
logmap = None  # logger for mapping in bots-engine
settings = None  # django's settings.py
usersysimportpath = None
currentrun = None  # needed for minta4query
routeid = ''  # current route. This is used to set routeid for Processes.
confirmrules = []  # confirmrules are read into memory at start of run
not_import = set()  # register modules that are not importable
