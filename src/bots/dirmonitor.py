# -*- coding: utf-8 -*-

"""
monitors directories for new files.
if a new file, lauch a job to the jobqueue server (so: jobqueue-server is needed).
directories to wachs are in config/bots.ini
runs as a daemon/service.
this module contains separate implementations for linux and windows
"""

from __future__ import print_function
from __future__ import unicode_literals

import click
import fnmatch
import os
import sys
import threading
import time

from . import botsinit
from . import botsglobal
from . import job2queue


if os.name == "nt":
    try:
        import win32file
        import win32con
    except Exception as msg:
        raise ImportError(
            'Dependency failure: bots directory monitoring requires python library "Python Win32 Extensions" on windows.'
        )

    def windows_event_handler(logger, dir_watch, cond, tasks):
        ACTIONS = {
            1: "Created  ",  # tekst for printing results
            2: "Deleted  ",
            3: "Updated  ",
            4: "Rename from",
            5: "Rename to",
        }
        FILE_LIST_DIRECTORY = 0x0001
        hDir = win32file.CreateFile(
            dir_watch["path"],  # path to directory
            FILE_LIST_DIRECTORY,  # access (read/write) mode
            # share mode: FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
            win32con.FILE_SHARE_READ
            | win32con.FILE_SHARE_WRITE
            | win32con.FILE_SHARE_DELETE,
            None,  # security descriptor
            win32con.OPEN_EXISTING,  # how to create
            win32con.FILE_FLAG_BACKUP_SEMANTICS,  # file attributes: FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED
            None,
        )
        # detecting right events is not easy in windows :-(
        # want to detect: new file,  move, drop, rename, write/append to file
        # only FILE_NOTIFY_CHANGE_LAST_WRITE: copy yes, no move
        # for rec=True: event that subdirectory itself is updated (for file deletes in dir)
        while True:
            results = win32file.ReadDirectoryChangesW(
                hDir,
                8192,  # buffer size was 1024, do not want to miss anything
                dir_watch["rec"],  # recursive
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                # ~ win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                # ~ win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                # ~ win32con.FILE_NOTIFY_CHANGE_SIZE |
                # ~ win32con.FILE_NOTIFY_CHANGE_SECURITY |
                # ~ win32con.FILE_NOTIFY_CHANGE_CREATION |       #unknown, does not work!
                # ~ win32con.FILE_NOTIFsY_CHANGE_LAST_ACCESS |   #unknown, does not work!
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                None,
                None,
            )
            if results:
                # for each incoming event: place route to run in a set. Main thread takes action.
                for action, filename in results:
                    logger.debug(
                        "Event: %(action)s %(filename)s",
                        {
                            "action": ACTIONS.get(action, "Unknown"),
                            "filename": filename,
                        },
                    )
                for action, filename in results:
                    if action in [1, 3, 5] and fnmatch.fnmatch(
                        filename, dir_watch["filemask"]
                    ):
                        # ~ if dir_watch['rec'] and os.sep in filename:
                        # ~ continue
                        # ~ full_filename = os.path.join (path_to_watch, file)
                        cond.acquire()
                        tasks.add(dir_watch["route"])
                        cond.notify()
                        cond.release()
                        break  # the route is triggered, do not need to trigger more often

    # end of windows-specific
else:
    # linux specific
    try:
        import pyinotify
    except Exception as msg:
        raise ImportError(
            'Dependency failure: bots directory monitoring requires python library "pyinotify" on linux.'
        )

    class LinuxEventHandler(pyinotify.ProcessEvent):
        """
        incoming event contains:
            dir=<bool>    check? - looks like the mask does nover contains dirs.
            mask=0x80
            maskname=eg IN_MOVED_TO
            name=<filename>
            path=<path>
            pathname=<path>/<filename>
            wd=<int>     #the watch
        """

        def my_init(self, logger, dir_watch_data, cond, tasks):
            self.dir_watch_data = dir_watch_data
            self.cond = cond
            self.tasks = tasks
            self.logger = logger

        def process_IN_CREATE(self, event):
            """ these events are not needed, but otherwise auto_add does not work...."""
            pass

        def process_default(self, event):
            """ for each incoming event: place route to run in a set. Main thread sends actual job.
            """
            # ~ if event.mask == pyinotify.IN_CLOSE_WRITE and event.dir and self.watch_data[event.wd][2]:
            # ~ logger.info('new directory!!"%s %s".',event.)
            for dir_watch in self.dir_watch_data:
                if event.pathname.startswith(dir_watch["path"]):
                    if fnmatch.fnmatch(event.name, dir_watch["filemask"]):
                        self.cond.acquire()
                        self.tasks.add(dir_watch["route"])
                        self.cond.notify()
                        self.cond.release()

    def linux_event_handler(logger, dir_watch_data, cond, tasks):
        watch_manager = pyinotify.WatchManager()
        mask = (
            pyinotify.IN_CLOSE_WRITE
            | pyinotify.IN_MOVED_TO
            | pyinotify.IN_MODIFY
            | pyinotify.IN_CREATE
        )
        for dir_watch in dir_watch_data:
            watch_manager.add_watch(
                path=dir_watch["path"],
                mask=mask,
                rec=dir_watch["rec"],
                auto_add=True,
                do_glob=True,
            )
        handler = LinuxEventHandler(
            logger=logger, dir_watch_data=dir_watch_data, cond=cond, tasks=tasks
        )
        notifier = pyinotify.Notifier(watch_manager, handler)
        notifier.loop()

    # end of linux-specific ##################################################################################


@click.command()
@click.option("--configdir", "-c", default="config", help="path to config-directory.")
def start(configdir):
    """Directory-monitor.
    """
    botsinit.generalinit(
        configdir
    )  # find locating of bots, configfiles, init paths etc.
    if not botsglobal.ini.getboolean("jobqueue", "enabled", False):
        print(
            "Error: bots jobqueue cannot start; not enabled in %s/bots.ini"
            % (configdir)
        )
        sys.exit(1)
    process_name = "dirmonitor"
    logger = botsinit.initserverlogging(process_name)
    logger.log(25, "Bots %(process_name)s started.", {"process_name": process_name})
    logger.log(
        25,
        'Bots %(process_name)s configdir: "%(configdir)s".',
        {
            "process_name": process_name,
            "configdir": botsglobal.ini.get("directories", "config"),
        },
    )

    botsenginepath = os.path.join(
        os.path.dirname(os.path.abspath(sys.argv[0])), "bots-engine.py"
    )  # get path to bots-engine
    cond = threading.Condition()
    tasks = set()
    dir_watch_data = []
    for section in botsglobal.ini.sections():
        if section.startswith("dirmonitor") and section[len("dirmonitor") :]:
            dir_watch_data.append({})
            dir_watch_data[-1]["path"] = botsglobal.ini.get(section, "path")
            dir_watch_data[-1]["rec"] = botsglobal.ini.getboolean(
                section, "recursive", False
            )
            dir_watch_data[-1]["filemask"] = botsglobal.ini.get(
                section, "filemask", "*"
            )
            dir_watch_data[-1]["route"] = botsglobal.ini.get(section, "route", "")
    if not dir_watch_data:
        logger.error("Nothing to watch!")
        sys.exit(0)

    if os.name == "nt":
        # for windows: start a thread per directory watcher
        for dir_watch in dir_watch_data:
            dir_watch_thread = threading.Thread(
                target=windows_event_handler, args=(logger, dir_watch, cond, tasks)
            )
            dir_watch_thread.daemon = True  # do not wait for thread when exiting
            dir_watch_thread.start()
    else:
        # for linux: one watch-thread, but multiple watches.
        dir_watch_thread = threading.Thread(
            target=linux_event_handler, args=(logger, dir_watch_data, cond, tasks)
        )
        dir_watch_thread.daemon = True  # do not wait for thread when exiting
        dir_watch_thread.start()

    # this main thread get the results from the watch-thread(s).
    logger.info("Bots %(process_name)s started.", {"process_name": process_name})
    active_receiving = False
    timeout = 2.0
    cond.acquire()
    while True:
        # this functions as a buffer: all events go into set tasks.
        # the tasks are fired to jobqueue after TIMOUT sec.
        # this is to avoid firing to many tasks to jobqueue; events typically come in bursts.
        # is value of timeout is larger, reaction times are slower...but less tasks are fired to jobqueue.
        # in itself this is not a problem, as jobqueue will alos discard duplicate jobs.
        # 2 sec seems to e a good value: reasonable quick, not to nervous.
        cond.wait(timeout=timeout)  # get back when results, or after timeout sec
        if tasks:
            if (
                not active_receiving
            ):  # first request (after tasks have been  fired, or startup of dirmonitor)
                active_receiving = True
                last_time = time.time()
            else:  # active receiving events
                current_time = time.time()
                if (
                    current_time - last_time >= timeout
                ):  # cond.wait returned probably because of a timeout
                    try:
                        for task in tasks:
                            logger.info(
                                'Send to queue "%(path)s %(config)s %(task)s".',
                                {
                                    "path": botsenginepath,
                                    "config": "-c" + configdir,
                                    "task": task,
                                },
                            )
                            job2queue.send_job_to_jobqueue(
                                [sys.executable, botsenginepath, "-c" + configdir, task]
                            )
                    except Exception as msg:
                        logger.info('Error in running task: "%(msg)s".', {"msg": msg})
                    tasks.clear()
                    active_receiving = False
                else:  # cond.wait returned probably because of a timeout
                    logger.debug("time difference to small.")
                    last_time = current_time
    cond.release()
    sys.exit(0)


if __name__ == "__main__":
    start()
