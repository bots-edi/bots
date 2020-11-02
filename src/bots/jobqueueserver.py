#!/usr/bin/env python
import sys
import os
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
import time
import datetime
import subprocess
import threading
import botsinit
import botslib
import botsglobal


#-------------------------------------------------------------------------------
PRIORITY = 0
JOBNUMBER = 1
TASK = 2
class Jobqueue(object):
    ''' handles the jobqueue.
        methodes can be called over xmlrpc (except the methods starting with '_')
    '''
    def __init__(self,logger):
        self.jobqueue = []       # list of jobs. in jobqueue are jobs are: (priority,jobnumber,task)
        self.jobcounter = 0      # to assign unique sequential job-number
        self.logger = logger
                
    def addjob(self,task,priority):
        #canonize task (to better find duplicates)??. Is dangerous, as non-bots-tasks might be started....
        #first check if job already in queue
        for job in self.jobqueue:
            if job[TASK] == task:
                if job[PRIORITY] != priority:   #change priority. is this useful?
                    job[PRIORITY] = priority
                    self.logger.info(u'Duplicate job, changed priority to %(priority)s: %(task)s',{'priority':priority,'task':task})
                    self._sort()
                    return 0        #zero or other code??
                else:
                    self.logger.info(u'Duplicate job not added: %(task)s',{'task':task})
                    return 4
        #add the job
        self.jobcounter += 1
        self.jobqueue.append([priority, self.jobcounter,task])
        self.logger.info(u'Added job %(job)s, priority %(priority)s: %(task)s',{'job':self.jobcounter,'priority':priority,'task':task})
        self._sort()
        return 0

    def clearjobq(self):
        self.jobqueue = []
        self.logger.info(u'Job queue cleared.')
        return 0

    def getjob(self):
        if len(self.jobqueue):
            return self.jobqueue.pop()
        return 0

    def _sort(self):
        self.jobqueue.sort(reverse=True)
        self.logger.debug(u'Job queue changed. New queue: %(queue)s',{'queue':''.join(['\n    ' + repr(job) for job in self.jobqueue])})
        #~ print self.jobqueue

#-------------------------------------------------------------------------------
def maxruntimeerror(logger,maxruntime,jobnumber,task_to_run):
    logger.error(u'Job %(job)s exceeded maxruntime of %(maxruntime)s minutes',{'job':jobnumber,'maxruntime':maxruntime})
    botslib.sendbotserrorreport(u'[Bots Job Queue] - Job exceeded maximum runtime',
                                u'Job %(job)s exceeded maxruntime of %(maxruntime)s minutes:\n %(task)s' % {'job':jobnumber,'maxruntime':maxruntime,'task':task_to_run})

#-------------------------------------------------------------------------------
def launcher(logger,port,lauchfrequency,maxruntime):
    xmlrpcclient = xmlrpclib.ServerProxy(u'http://localhost:' + unicode(port))
    maxseconds = maxruntime*60
    time.sleep(3)   #to allow jobqserver to start
    while True:
        time.sleep(lauchfrequency)
        job = xmlrpcclient.getjob()

        if job:       #0 means nothing to launch
            jobnumber = job[1]
            task_to_run = job[2]
            # Start a timer thread for maxruntime error
            timer_thread = threading.Timer(maxseconds,maxruntimeerror,args=(logger,maxruntime,jobnumber,task_to_run))
            timer_thread.start()
            try:
                starttime = datetime.datetime.now()
                logger.info(u'Starting job %(job)s',{'job':jobnumber})
                result = subprocess.call(task_to_run,stdin=open(os.devnull,'r'),stdout=open(os.devnull,'w'),stderr=open(os.devnull,'w'))
                time_taken = datetime.timedelta(seconds=(datetime.datetime.now() - starttime).seconds)
                logger.info(u'Finished job %(job)s, elapsed time %(time_taken)s, result %(result)s',{'job':jobnumber,'time_taken':time_taken,'result':result})
            except Exception as msg:
                logger.error(u'Error starting job %(job)s: %(msg)s',{'job':jobnumber,'msg':msg})
                botslib.sendbotserrorreport(u'[Bots Job Queue] - Error starting job',
                                            u'Error starting job %(job)s:\n %(task)s\n\n %(msg)s' % {'job':jobnumber,'task':task_to_run,'msg':msg})
            timer_thread.cancel()


def start():
    #NOTE: bots directory should always be on PYTHONPATH - otherwise it will not start.
    #***command line arguments**************************
    usage = '''
    This is "%(name)s" version %(version)s, part of Bots open source edi translator (http://bots.sourceforge.net).
    Server program that ensures only a single bots-engine runs at any time, and no engine run requests are 
    lost/discarded. Each request goes to a queue and is run in sequence when the previous run completes. 
    Use of the job queue is optional and must be configured in bots.ini (jobqueue section, enabled = True).
    Usage:
        %(name)s  -c<directory>
    Options:
        -c<directory>   directory for configuration files (default: config).
        
    '''%{'name':os.path.basename(sys.argv[0]),'version':botsglobal.version}
    configdir = 'config'
    for arg in sys.argv[1:]:
        if arg.startswith('-c'):
            configdir = arg[2:]
            if not configdir:
                print 'Error: configuration directory indicated, but no directory name.'
                sys.exit(1)
        else:
            print usage
            sys.exit(0)
    #***end handling command line arguments**************************
    botsinit.generalinit(configdir)     #find locating of bots, configfiles, init paths etc.
    if not botsglobal.ini.getboolean('jobqueue','enabled',False):
        print 'Error: bots jobqueue cannot start; not enabled in %s/bots.ini' % configdir
        sys.exit(1)
    process_name = 'jobqueue'
    logger = botsinit.initserverlogging(process_name)
    logger.log(25,u'Bots %(process_name)s started.',{'process_name':process_name})
    logger.log(25,u'Bots %(process_name)s configdir: "%(configdir)s".',{'process_name':process_name,'configdir':botsglobal.ini.get('directories','config')})
    port = botsglobal.ini.getint('jobqueue','port',28082)
    logger.log(25,u'Bots %(process_name)s listens for xmlrpc at port: "%(port)s".',{'process_name':process_name,'port':port})

    #start launcher thread
    lauchfrequency = botsglobal.ini.getint('jobqueue','lauchfrequency',5)
    maxruntime = botsglobal.ini.getint('settings','maxruntime',60)
    launcher_thread = threading.Thread(name='launcher', target=launcher, args=(logger,port,lauchfrequency,maxruntime))
    launcher_thread.daemon = True
    launcher_thread.start()
    logger.info(u'Jobqueue launcher started.')

    #the main thread is the xmlrpc server: all adding, getting etc for jobqueue is done via xmlrpc.
    logger.info(u'Jobqueue server started.')
    server = SimpleXMLRPCServer(('localhost', port),logRequests=False)        
    server.register_instance(Jobqueue(logger))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    
    sys.exit(0)


if __name__ == '__main__':
    start()
