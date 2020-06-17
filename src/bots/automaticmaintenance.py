# -*- coding: utf-8 -*-



import sys
from django.utils.translation import ugettext as _
#bots-modules
from . import botslib
from . import botsglobal
from .botsconfig import *

#ta-fields used in evaluation
TAVARS = 'idta,statust,divtext,child,ts,filename,status,idroute,fromchannel,tochannel,frompartner,topartner,frommail,tomail,contenttype,nrmessages,editype,messagetype,errortext,script,rsrv1,filesize,numberofresends'


def evaluate(command, rootidtaofrun):
    ''' Trace for each received file.
        Write a filereport for each file,
        Write a report for the run.
    '''
    resultsofrun = {OPEN: 0, ERROR: 0, OK: 0, DONE: 0}  # to collect the results of the filereports for runreport
    totalfilesize = 0
    #evaluate every incoming file of this run;
    for row in botslib.query('''SELECT ''' + TAVARS + '''
                                FROM ta
                                WHERE idta > %(rootidtaofrun)s
                                AND status=%(status)s ''',
                             {'status': EXTERNIN, 'rootidtaofrun': rootidtaofrun}):
        traceofinfile = Trace(row, rootidtaofrun)
        resultsofrun[traceofinfile.statust] += 1
        totalfilesize += traceofinfile.filesize
        traceofinfile.make_file_report()
    make_run_report(rootidtaofrun, resultsofrun, command, totalfilesize)
    return email_error_report(rootidtaofrun)  # return report status: 0 (no error) or 1 (error)


def make_run_report(rootidtaofrun, resultsofrun, command, totalfilesize):
    #count nr files send
    for row in botslib.query('''SELECT COUNT(*) as count
                                FROM ta
                                WHERE idta > %(rootidtaofrun)s
                                AND status=%(status)s
                                AND statust=%(statust)s ''',
                             {'status': EXTERNOUT, 'rootidtaofrun': rootidtaofrun, 'statust': DONE}):
        send = row[str('count')]
    #count process errors
    for row in botslib.query('''SELECT COUNT(*) as count
                                FROM ta
                                WHERE idta >= %(rootidtaofrun)s
                                AND status=%(status)s
                                AND statust=%(statust)s''',
                             {'status': PROCESS, 'rootidtaofrun': rootidtaofrun, 'statust': ERROR}):
        processerrors = row[str('count')]
    #generate report (in database)
    rootta = botslib.OldTransaction(rootidtaofrun)
    rootta.syn('ts')  # get the timestamp of this run
    lastreceived = resultsofrun[DONE] + resultsofrun[OK] + resultsofrun[OPEN] + resultsofrun[ERROR]
    status = bool(resultsofrun[OK] + resultsofrun[OPEN] + resultsofrun[ERROR] + processerrors)
    #give information about the used command line parameters for each run. Problem is that there is only 35pos for this (in MySQL, PostgreSQL).
    #~ commandline =
    if botsglobal.settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        commandline = ' '.join(sys.argv)
    else:
        commandline = ' '.join(arg for arg in sys.argv[1:] if arg != '-cconfig' and not arg.startswith('--'))[:35]
    botslib.changeq('''INSERT INTO report (idta,lastopen,lasterror,lastok,lastdone,send,processerrors,
                                            ts,lastreceived,status,type,filesize,acceptance,rsrv1)
                            VALUES  (%(rootidtaofrun)s,%(lastopen)s,%(lasterror)s,%(lastok)s,%(lastdone)s,%(send)s,%(processerrors)s,
                                    %(ts)s,%(lastreceived)s,%(status)s,%(type)s,%(totalfilesize)s,%(acceptance)s,%(rsrv1)s) ''',
                    {'rootidtaofrun': rootidtaofrun, 'lastopen': resultsofrun[OPEN], 'lasterror': resultsofrun[ERROR], 'lastok': resultsofrun[OK],
                     'lastdone': resultsofrun[DONE], 'send': send, 'processerrors': processerrors, 'ts': rootta.ts, 'lastreceived': lastreceived,
                     'status': status, 'type': command, 'totalfilesize': totalfilesize, 'acceptance': int(botsglobal.ini.getboolean('acceptance', 'runacceptancetest', False)),
                     'rsrv1': commandline})
    #20120830: if new run with nothing received and no process errors: delete ta's.
    if command == 'new' and not lastreceived and not processerrors:
        botslib.changeq('''DELETE FROM ta WHERE idta>=%(rootidtaofrun)s''', {'rootidtaofrun': rootidtaofrun})


def email_error_report(rootidtaofrun):
    for results in botslib.query('''SELECT idta,lastopen,lasterror,lastok,lastdone,
                                            send,processerrors,ts,lastreceived,type,status
                                    FROM report
                                    WHERE idta=%(rootidtaofrun)s''',
                                 {'rootidtaofrun': rootidtaofrun}):
        break
    else:
        raise botslib.PanicError(_('In generate report: could not find report?'))
    subject = _('[Bots Error Report] %(time)s') % {'time': str(results[str('ts')])[:16]}
    reporttext = _('Bots Report; type: %(type)s, time: %(time)s\n') % {
        'type': results[str('type')], 'time': str(results[str('ts')])[:19]}
    reporttext += _('    %d files received/processed in run.\n') % (results[str('lastreceived')])
    if results[str('lastdone')]:
        reporttext += _('    %d files without errors,\n') % (results[str('lastdone')])
    if results[str('lasterror')]:
        subject += _('; %d file errors') % (results[str('lasterror')])
        reporttext += _('    %d files with errors,\n') % (results[str('lasterror')])
    if results[str('lastok')]:
        subject += _('; %d files stuck') % (results[str('lastok')])
        reporttext += _('    %d files got stuck,\n') % (results[str('lastok')])
    if results[str('lastopen')]:
        subject += _('; %d system errors') % (results[str('lastopen')])
        reporttext += _('    %d system errors,\n') % (results[str('lastopen')])
    if results[str('processerrors')]:
        subject += _('; %d process errors') % (results[str('processerrors')])
        reporttext += _('    %d errors in processes.\n') % (results[str('processerrors')])
    reporttext += _('    %d files send in run.\n') % (results[str('send')])

    botsglobal.logger.info(reporttext)  # log the report texts
    # only send email report if there are errors.
    # sendreportifprocesserror (in bots.ini): no email reports if only process errors
    if results[str('lasterror')] or results[str('lastopen')] or results[str('lastok')] or (results[str('processerrors')] and botsglobal.ini.getboolean('settings', 'sendreportifprocesserror', True)):

        # Include details about process errors in the email report; if debug is True: includes trace
        if results[str('processerrors')]:
            for row in botslib.query('''SELECT idroute,fromchannel,tochannel,errortext
                                        FROM ta
                                        WHERE idta>=%(rootidtaofrun)s
                                        AND status=%(status)s
                                        AND statust=%(statust)s ''',
                                     {'rootidtaofrun': rootidtaofrun, 'status': PROCESS, 'statust': ERROR}):
                reporttext += '\nProcess error:\n'
                for key in list(row.keys()):
                    reporttext += '%s: %s\n' % (key, row[key])
        # Include details about file errors in the email report; if debug is True: includes trace
        if results[str('lasterror')] or results[str('lastopen')] or results[str('lastok')]:
            for row in botslib.query('''SELECT idroute,frompartner,fromchannel,topartner,tochannel,errortext,infilename
                                        FROM filereport
                                        WHERE idta>%(rootidtaofrun)s
                                        AND statust!=%(statust)s ''',
                                     {'rootidtaofrun': rootidtaofrun, 'statust': DONE}):
                reporttext += '\nFile error:\n'
                for key in list(row.keys()):
                    reporttext += '%s: %s\n' % (key, row[key])

        botslib.sendbotserrorreport(subject, reporttext)

    return int(results[str('status')])  # return report status: 0 (no error) or 1 (error)


class Trace(object):
    ''' trace for one incoming file.
        each step in the processing is represented by a ta-object.
        the ta-objects form a tree; the incoming edi-file (status EXTERNIN) is root.
        (this also works for merging, strange but inherent).
        this tree is evaluated to get one statust, by walking the tree and evaluating the statust of nodes.
    '''

    def __init__(self, row, rootidtaofrun):
        self.rootofinfile = dict(row)
        self.rootidtaofrun = rootidtaofrun
        self._buildtreeoftransactions(self.rootofinfile)
        try:
            self.statust = self._getstatusfortreeoftransactions(self.rootofinfile)
        except Exception as msg:
            botsglobal.logger.exception(_('Error in automatic maintenance: "%(msg)s".'), {'msg': msg})
            self.statust = OPEN
        self._collectdataforfilereport()

    def display(self, currentta, level=0):
        ''' method for debugging.'''
        print(level * '    ', currentta['idta'], currentta['statust'], currentta['talijst'])
        for ta_child in currentta['talijst']:
            self.display(ta_child, level + 1)

    def _buildtreeoftransactions(self, tacurrent):
        ''' build a tree of all ta's for the incoming file. recursive.
        '''
        if tacurrent['child']:  # find successor by using child relation ship (when merging)
            for row in botslib.query('''SELECT ''' + TAVARS + '''
                                         FROM ta
                                         WHERE idta=%(child)s
                                         ORDER BY idta ''',
                                     {'child': tacurrent['child']}):
                tacurrent[str('talijst')] = [dict(row)]  # add next one (a child has only one parent)
        else:  # find successor by using parent-relationship; for one-one-one relation an splitting
            talijst = []
            for row in botslib.query('''SELECT ''' + TAVARS + '''
                                        FROM ta
                                        WHERE idta > %(currentidta)s
                                        AND parent=%(currentidta)s
                                        ORDER BY idta ''',  # adding the idta > %(currentidta)s to selection speeds up a lot.
                                     {'currentidta': tacurrent['idta']}):
                talijst.append(dict(row))
            # there ws logic here to assure that earlier try's where not used. this is
            # only needed for communication-retries now
            tacurrent['talijst'] = talijst
        #recursive build:
        for child in tacurrent['talijst']:
            self._buildtreeoftransactions(child)

    def _getstatusfortreeoftransactions(self, tacurrent):
        ''' recursive, walks tree of ediobject-ta, depth-first
            algoritm is backwards (start with last node)
            each 'branche' always evaluates to one statust: OPEN, ERROR, OK, DONE
            for each db-ta:
            -   get statust of all child-db-ta (recursive); count these statust's
            -   evaluate status of db-ta itself
        '''
        statustcount = [0, 0, 0, 0]  # count of statust of child-branches: number of OPEN, ERROR, OK, DONE
        #evaluate all child-branches; collect results in statustcount
        for child in tacurrent['talijst']:
            statustcount[self._getstatusfortreeoftransactions(child)] += 1
        #evaluate curent ta; return statust of whole branche;
        if tacurrent['statust'] == DONE:
            if statustcount[ERROR]:  # if error in a child: report error
                return ERROR
            elif statustcount[OK]:
                return OK  # if child is stuck: report stuck
            else:  # al is OK, or has no children (end of trace)
                return DONE
        elif tacurrent['statust'] == OK:  # file is stucked. There should be no children
            if tacurrent['talijst']:
                raise botslib.TraceError(_('Statust OK (stuck) but has child(ren) (idta: %(idta)s).'), tacurrent)
            else:
                return OK
        elif tacurrent['statust'] == ERROR:  # should be no children.
            if tacurrent['talijst']:
                raise botslib.TraceError(_('Statust ERROR but has child(ren) (idta: %(idta)s).'), tacurrent)
            else:
                return ERROR
        else:  # tacurrent.statust==OPEN: something is very wrong. Raise exception.
            raise botslib.TraceError(_('Severe error: found statust OPEN for idta: %(idta)s.'), tacurrent)

    def _collectdataforfilereport(self):
        ''' Walk the ta-tree again in order to retrieve information/data belonging to incoming file (but not statust).
            If information is different in different ta's: place '(several values)' (but there is a setting in bots.ini to show only the first one)
        '''
        def core(ta_object):
            if ta_object['status'] == FILEIN:  # get data for incoming email, not attachments
                if not self.filesize2:
                    self.filesize2 = ta_object['filesize']
                if not self.incontenttype:
                    self.frommail = ta_object['frommail']
                    self.tomail = ta_object['tomail']
                    self.incontenttype = ta_object['contenttype']
                    self.rsrv1 = ta_object['rsrv1']  # email subject
            elif ta_object['status'] == PARSED:
                self.filesize += ta_object['filesize']
                if self.ineditype:
                    if self.ineditype != ta_object['editype'] and asterisk:
                        self.ineditype = '(several values)'
                else:
                    self.ineditype = ta_object['editype']
            elif ta_object['status'] == SPLITUP:
                self.nrmessages += 1
                if self.inmessagetype:
                    if self.inmessagetype != ta_object['messagetype'] and asterisk:
                        self.inmessagetype = '(several values)'
                else:
                    self.inmessagetype = ta_object['messagetype']
            elif ta_object['status'] == TRANSLATED:
                if self.divtext:
                    if self.divtext != ta_object['divtext'] and asterisk:
                        self.divtext = '(several values)'
                else:
                    self.divtext = ta_object['divtext']
            elif ta_object['status'] == EXTERNOUT:
                #for resends: nrmessages is not picked up, do this here.
                if not self.nrmessages:
                    self.nrmessages = ta_object['nrmessages']
                if ta_object['numberofresends']:
                    if self.outidta:
                        if self.outidta != ta_object['idta'] and asterisk:
                            self.outidta = 0
                    else:
                        self.outidta = ta_object['idta']
                if self.outeditype:
                    if self.outeditype != ta_object['editype'] and asterisk:
                        self.outeditype = '(several values)'
                else:
                    self.outeditype = ta_object['editype']
                if self.outmessagetype:
                    if self.outmessagetype != ta_object['messagetype'] and asterisk:
                        self.outmessagetype = '(several values)'
                else:
                    self.outmessagetype = ta_object['messagetype']
                if ta_object['frommail']:
                    if self.frommail:
                        if self.frommail != ta_object['frommail'] and asterisk:
                            self.frommail = '(several values)'
                    else:
                        self.frommail = ta_object['frommail']
                if ta_object['tomail']:
                    if self.tomail:
                        if self.tomail != ta_object['tomail'] and asterisk:
                            self.tomail = '(several values)'
                    else:
                        self.tomail = ta_object['tomail']
                if ta_object['contenttype']:
                    if self.outcontenttype:
                        if self.outcontenttype != ta_object['contenttype'] and asterisk:
                            self.outcontenttype = '(several values)'
                    else:
                        self.outcontenttype = ta_object['contenttype']
                if self.outfilename:
                    if self.outfilename != ta_object['filename'] and asterisk:
                        self.outfilename = '(several values)'
                else:
                    self.outfilename = ta_object['filename']
                if self.tochannel:
                    if self.tochannel != ta_object['tochannel'] and asterisk:
                        self.tochannel = '(several values)'
                else:
                    self.tochannel = ta_object['tochannel']
            #for every status
            if ta_object['frompartner']:
                if self.frompartner:
                    if self.frompartner != ta_object['frompartner'] and asterisk:
                        self.frompartner = '(several values)'
                else:
                    self.frompartner = ta_object['frompartner']
            if ta_object['topartner']:
                if self.topartner:
                    if self.topartner != ta_object['topartner'] and asterisk:
                        self.topartner = '(several values)'
                else:
                    self.topartner = ta_object['topartner']
            if ta_object['errortext']:
                self.errortext += ta_object['errortext'] + '\n'
            #go recursive!
            for child in ta_object['talijst']:
                core(child)
            #end of core function

        asterisk = botsglobal.ini.getboolean('settings', 'multiplevaluesasterisk', True)
        self.idta = self.rootofinfile['idta']
        self.reportidta = self.rootidtaofrun
        self.retransmit = 0
        self.idroute = self.rootofinfile['idroute']
        self.fromchannel = self.rootofinfile['fromchannel']
        self.ts = self.rootofinfile['ts']
        self.infilename = self.rootofinfile['filename']
        self.tochannel = ''
        self.frompartner = ''
        self.topartner = ''
        self.frommail = ''
        self.tomail = ''
        self.ineditype = ''
        self.inmessagetype = ''
        self.outeditype = ''
        self.outmessagetype = ''
        self.incontenttype = ''
        self.outcontenttype = ''
        self.nrmessages = 0
        self.outfilename = ''
        self.outidta = 0
        self.errortext = ''
        self.divtext = ''
        self.rsrv1 = ''  # email subject
        self.filesize = 0  # counts all PARSED files
        self.filesize2 = 0  # pick up FILEIN; use if filesize is 0
        core(self.rootofinfile)
        if not self.filesize:
            self.filesize = self.filesize2

    def make_file_report(self):
        # 20140116: patch for MySQLdb version 1.2.5. This version seems to check
        # all parameters - not just the ones actually used.
        tmp_dict = self.__dict__.copy()
        tmp_dict.pop('rootofinfile', 'nep')
        botslib.changeq('''INSERT INTO filereport (idta,statust,reportidta,retransmit,idroute,fromchannel,ts,
                                                    infilename,tochannel,frompartner,topartner,frommail,
                                                    tomail,ineditype,inmessagetype,outeditype,outmessagetype,
                                                    incontenttype,outcontenttype,nrmessages,outfilename,errortext,
                                                    divtext,outidta,rsrv1,filesize)
                                VALUES  (%(idta)s,%(statust)s,%(reportidta)s,%(retransmit)s,%(idroute)s,%(fromchannel)s,%(ts)s,
                                        %(infilename)s,%(tochannel)s,%(frompartner)s,%(topartner)s,%(frommail)s,
                                        %(tomail)s,%(ineditype)s,%(inmessagetype)s,%(outeditype)s,%(outmessagetype)s,
                                        %(incontenttype)s,%(outcontenttype)s,%(nrmessages)s,%(outfilename)s,%(errortext)s,
                                        %(divtext)s,%(outidta)s,%(rsrv1)s,%(filesize)s )
                                ''',
                        tmp_dict)
