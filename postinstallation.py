# -*- coding: utf-8 -*-

import sys
import os
import tarfile
import glob
import shutil
import subprocess
import traceback
import time
import bots.botsglobal as botsglobal


def join(path,*paths):
    return os.path.normpath(os.path.join(path,*paths))



#******************************************************************************
#***    start                     *********************************************
#******************************************************************************
def start():
    print('Installation of bots open source edi translator.')
    #python version dependencies
    version = str(sys.version_info[0]) + str(sys.version_info[1])
    if version == '26':
        pass
    elif version == '27':
        pass
    else:
        raise Exception('Wrong python version, use python 2.6.* or 2.7.*')

    botsdir = os.path.dirname(botsglobal.__file__)
    print('    Installed bots in "%s".'%(botsdir))

#******************************************************************************
#***    install configuration files      **************************************
#******************************************************************************
    if os.path.exists(join(botsdir,'config','settings.py')):    #use this to see if this is an existing installation
        print('    Found existing configuration files')
        print('        Configuration files bots.ini and settings.py not overwritten.')
        print('        Manual action is needed for these configuration files.')
        print('        See bots wiki for more info: http://code.google.com/p/bots/wiki/Migrate.')
    else:
        shutil.copy(join(botsdir,'install','bots.ini'),join(botsdir,'config','bots.ini'))
        shutil.copy(join(botsdir,'install','settings.py'),join(botsdir,'config','settings.py'))
        print('    Installed configuration files')

#******************************************************************************
#***    install database; upgrade existing db *********************************
#******************************************************************************
    sqlitedir = join(botsdir,'botssys','sqlitedb')
    if os.path.exists(join(sqlitedir,'botsdb')):    #use this to see if this is an existing installation
        print('    Found existing database file botssys/sqlitedb/botsdb')
        print('        Manual action is needed to convert the database to new bots 3.0 format.')
        print('        There is a script to update the database.')
        print('        See bots wiki for more info: http://code.google.com/p/bots/wiki/Migrate.')
    else:
        if not os.path.exists(sqlitedir):    #use this to see if this is an existing installation
            os.makedirs(sqlitedir)
        shutil.copy(join(botsdir,'install','botsdb'),join(sqlitedir,'botsdb'))
        print('    Installed SQLite database')

#******************************************************************************
#***    install libraries, dependencies  ***************************************
#******************************************************************************
    list_of_setuppers = []
    list_of_dirs_to_remove = []
    for library in glob.glob(join(botsdir,'installwin','*.gz')):
        tar = tarfile.open(library)
        tar.extractall(path=os.path.dirname(library))
        tar.close()
        untar_dir = library[:-len('.tar.gz')]
        list_of_setuppers.append(subprocess.Popen([join(sys.prefix,'pythonw.exe'), 'setup.py','--quiet','install'],cwd=untar_dir,bufsize=-1))
        list_of_dirs_to_remove.append(untar_dir)
    ready = False
    while not ready:
        time.sleep(1)
        for setupper in list_of_setuppers:
            if setupper.poll() is None:
                break
        else:
            ready = True
    for untar_dir in list_of_dirs_to_remove:
        shutil.rmtree(untar_dir, ignore_errors=True)

    print('    Installed needed libraries.')

#******************************************************************************
#***    shortcuts       *******************************************************
#******************************************************************************
    scriptpath = join(sys.prefix,'Scripts')
    shortcutdir = join(get_special_folder_path('CSIDL_COMMON_PROGRAMS'),'Bots3.2rc2')
    try:
        os.mkdir(shortcutdir)
    except:
        pass
    else:
        directory_created(shortcutdir)

    try:
        #~ create_shortcut(join(scriptpath,'botswebserver'),'Bots open source EDI translator',join(shortcutdir,'Bots-webserver.lnk'))
        create_shortcut(join(sys.prefix,'python.exe'),'bots open source edi translator',join(shortcutdir,'bots-webserver.lnk'),join(scriptpath,'bots-webserver.py'))
        file_created(join(shortcutdir,'bots-webserver.lnk'))
    except:
        print('    Failed to install shortcut/link for bots in your menu.')
    else:
        print('    Installed shortcut in "Program Files".')

#******************************************************************************
#******************************************************************************

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='-install':
        try:
            start()
        except:
            print(traceback.format_exc(0))
            print()
            print('Bots installation failed.')
        else:
            print()
            print('Bots installation succeeded.')
    #avoid strange errors when UAC is off.
    try:
        sys.stdout.flush()
    except IOError:
        pass
    try:
        sys.stderr.flush()
    except IOError:
        pass
