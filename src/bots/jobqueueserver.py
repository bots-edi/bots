#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from future import standard_library

standard_library.install_aliases()

import click
import os
import time
import datetime
import subprocess
import queue
import sys
import threading

from builtins import *  # noqa

# from builtins import (
#     bytes, dict, int, list, object, range, str, ascii, chr, hex,
#     input, next, oct, open, pow, round, super, filter, map, zip)

from bots import botsinit
from bots import botslib
from bots import botsglobal

try:
    from xmlrpc.server import (
        SimpleXMLRPCServer,
    )  # fails to import on python2  even future is available
except ImportError:
    from SimpleXMLRPCServer import SimpleXMLRPCServer

# if sys.version_info[0] > 2:
#     basestring = unicode = str

PRIORITY = 0
JOBNUMBER = 1
TASK = 2


class Jobqueue(object):
    """handles the jobqueue.

    methodes can be called over xmlrpc (except the methods starting with '_')
    """

    def __init__(self, logger):
        """"""
        self.jobqueue = (
            []
        )  # list of jobs. in jobqueue are jobs are: (priority,jobnumber,task)
        self.jobcounter = 0  # to assign unique sequential job-number
        self.logger = logger

    def addjob(self, task, priority):
        """"""
        # canonize task (to better find duplicates)??. Is dangerous, as non-bots-tasks might be started....
        # first check if job already in queue
        for job in self.jobqueue:
            if job[TASK] == task:
                if job[PRIORITY] != priority:  # change priority. is this useful?
                    job[PRIORITY] = priority
                    self.logger.info(
                        "Duplicate job, changed priority to %(priority)s: %(task)s",
                        {"priority": priority, "task": task},
                    )
                    self._sort()
                    return 0  # zero or other code??
                else:
                    self.logger.info(
                        "Duplicate job not added: %(task)s", {"task": task}
                    )
                    return 4
        # add the job
        self.jobcounter += 1
        self.jobqueue.append([priority, self.jobcounter, task])
        self.logger.info(
            "Added job %(job)s, priority %(priority)s: %(task)s",
            {"job": self.jobcounter, "priority": priority, "task": task},
        )
        self._sort()
        return 0

    def clearjobq(self):
        """"""
        self.jobqueue = []
        self.logger.info("Job queue cleared.")
        return 0

    def getjob(self):
        """"""
        if len(self.jobqueue):
            return self.jobqueue.pop()
        return 0

    def _sort(self):
        """"""
        self.jobqueue.sort(reverse=True)
        self.logger.debug(
            "Job queue changed. New queue: %(queue)s",
            {"queue": "".join(["\n    " + repr(job) for job in self.jobqueue])},
        )


def maxruntimeerror(logger, maxruntime, jobnumber, task_to_run):
    """"""
    logger.error(
        "Job {} exceeded maxruntime of {} minutes".format(jobnumber, maxruntime)
    )

    botslib.sendbotserrorreport(
        "[Bots Job Queue] - Job exceeded maximum runtime",
        "Job {} exceeded maxruntime of {} minutes:\n {}".format(
            jobnumber, maxruntime, task_to_run
        ),
    )


def launcher(logger, queue, lauchfrequency, maxruntime):
    """"""
    maxseconds = maxruntime * 60
    time.sleep(3)  # allow jobqserver to start
    while True:
        time.sleep(lauchfrequency)
        job = queue.get(block=True, timeout=None)
        if job:
            jobnumber = job[1]
            task_to_run = job[2]
            # Start a timer thread for maxruntime error
            timer_thread = threading.Timer(
                maxseconds,
                maxruntimeerror,
                args=(logger, maxruntime, jobnumber, task_to_run),
            )
            timer_thread.start()
            try:
                t0 = datetime.datetime.now()
                logger.info("Starting job %(job)s", {"job": jobnumber})
                result = subprocess.call(
                    task_to_run,
                    stdin=open(os.devnull, "r"),
                    stdout=open(os.devnull, "w"),
                    stderr=open(os.devnull, "w"),
                )
                t1 = datetime.datetime.now()
                time_taken = (t1 - t0).seconds

                logger.info(
                    "Finished job %(job)s, elapsed time %(time_taken)s, result %(result)s",
                    {"job": jobnumber, "time_taken": time_taken, "result": result},
                )
            except Exception as e:
                logger.error("Error starting job {}: {}".format(jobnumber, e))

                botslib.sendbotserrorreport(
                    "[Bots Job Queue] - Error starting job",
                    "Error starting job {}:\n {}\n\n {}".format(
                        jobnumber, task_to_run, e
                    ),
                )

            timer_thread.cancel()
            queue.task_done()


@click.command()
@click.option("--configdir", "-c", default="config", help="path to config-directory.")
def start(configdir):
    """Server program that ensures only a single bots-engine runs at any time,
    and no engine run requests are lost/discarded.

    Each request goes to a queue and is run in sequence when the previous run completes.
    Use of the job queue is optional and must be configured in bots.ini (jobqueue section, enabled = True).
    """

    botsinit.generalinit(configdir)
    if not botsglobal.ini.getboolean("jobqueue", "enabled", False):
        print(
            "Error: bots jobqueue cannot start; not enabled in {}/bots.ini".format(
                configdir
            )
        )
        sys.exit(1)
    nr_threads = 2  # botsglobal.ini.getint('jobqueue','nr_threads')
    process_name = "jobqueue"

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
    port = botsglobal.ini.getint("jobqueue", "port", 28082)
    logger.log(
        25,
        'Bots %(process_name)s listens for xmlrpc at port: "%(port)s".',
        {"process_name": process_name, "port": port},
    )

    # start launcher thread
    q = queue.Queue()

    lauchfrequency = botsglobal.ini.getint("jobqueue", "lauchfrequency", 5)
    maxruntime = botsglobal.ini.getint("settings", "maxruntime", 60)
    for thread in range(nr_threads):
        launcher_thread = threading.Thread(
            name="launcher",
            target=launcher,
            args=(logger, q, lauchfrequency, maxruntime),
        )
        launcher_thread.start()

    # the main thread is the xmlrpc server:
    # all adding, getting etc for jobqueue is done via xmlrpc.
    logger.info("Jobqueue server started.")
    server = SimpleXMLRPCServer(("localhost", port), logRequests=False)
    server.register_instance(Jobqueue(logger))

    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit) as e:  # noqa
        pass

    sys.exit(0)


if __name__ == "__main__":
    start()
