# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import unittest
import shutil
import os
import sys
import subprocess
import logging
import tests.utilsunit
import bots.botslib as botslib
import bots.botsinit as botsinit
import bots.botsglobal as botsglobal
from bots.botsconfig import *
if sys.version_info[0] > 2:
    basestring = unicode = str


'''
plugin unitconfirm.zip
active all routes
before each run: clear transactions!

tested is:
- seperate unit tests
- total expectation of whole run
- seperate unit-tests to check confirm-rules
'''

botssys = 'bots/botssys'


class TestMain(unittest.TestCase):

    def testroutetestmdn(self):
        lijst = utilsunit.getdir(os.path.join(botssys, 'outfile/confirm/mdn/*'))
        self.failUnless(len(lijst) == 0)
        nr_rows = 0
        for row in botslib.query(u'''SELECT idta,confirmed,confirmidta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                AND     idroute=%(idroute)s
                                AND     confirmtype=%(confirmtype)s
                                AND     confirmasked=%(confirmasked)s
                                AND     frommail != ''
                                ORDER BY idta DESC
                                ''',
                                 {'status': 220, 'statust': DONE, 'idroute': 'testmdn', 'confirmtype': 'send-email-MDN', 'confirmasked': True}):
            nr_rows += 1
            print(row[str('idta')], row[str('confirmed')], row[str('confirmidta')])
            self.failUnless(row[str('confirmed')])
            self.failUnless(row[str('confirmidta')] != 0)
        else:
            self.failUnless(nr_rows == 1)

        nr_rows = 0
        for row in botslib.query(u'''SELECT idta,confirmed,confirmidta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                AND     idroute=%(idroute)s
                                AND     confirmtype=%(confirmtype)s
                                AND     confirmasked=%(confirmasked)s
                                AND     frommail != ''
                                ORDER BY idta DESC
                                ''',
                                 {'status': 500, 'statust': DONE, 'idroute': 'testmdn', 'confirmtype': 'ask-email-MDN', 'confirmasked': True}):
            nr_rows += 1
            self.failUnless(row[str('confirmed')])
            self.failUnless(row[str('confirmidta')] != 0)
        else:
            self.failUnless(nr_rows == 1)

    def testroutetestmdn2(self):
        lijst = utilsunit.getdir(os.path.join(botssys, 'outfile/confirm/mdn2/*'))
        self.failUnless(len(lijst) == 0)
        nr_rows = 0
        for row in botslib.query(u'''SELECT idta,confirmed,confirmidta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                AND     idroute=%(idroute)s
                                AND     confirmtype=%(confirmtype)s
                                AND     confirmasked=%(confirmasked)s
                                AND     frommail != ''
                                ORDER BY idta DESC
                                ''',
                                 {'status': 500, 'statust': DONE, 'idroute': 'testmdn2', 'confirmtype': 'ask-email-MDN', 'confirmasked': True}):
            nr_rows += 1
            self.failUnless(not row[str('confirmed')])
            self.failUnless(row[str('confirmidta')] == 0)
        else:
            self.failUnless(nr_rows == 1)

    def testrouteotherx12(self):
        lijst = utilsunit.getdir(os.path.join(botssys, 'outfile/confirm/otherx12/*'))
        self.failUnless(len(lijst) == 15)

    def testroutetest997(self):
        '''
        test997 1:  pickup 850*1    ask confirm 850*2   gen & send 850*2
                                    send confirm 850*1  gen & send 997*1
        test997 2:  receive 997*1   confirm 850*1       gen xml*1
                    receive 850*2   ask confirm 850*3   gen 850*3
                                    send confirm 850*2  gen & send 997*2
        test997 3:  receive 997*2   confirm 850*2       gen & send xml (to trash)
                                                        send 850*3 (to trash)
                                                        send xml (to trash)
        '''
        lijst = utilsunit.getdir(os.path.join(botssys, 'outfile/confirm/x12/*'))
        self.failUnless(len(lijst) == 0)
        lijst = utilsunit.getdir(os.path.join(botssys, 'outfile/confirm/trash/*'))
        self.failUnless(len(lijst) == 6)
        counter = 0
        for row in botslib.query(u'''SELECT idta,confirmed,confirmidta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                AND     idroute=%(idroute)s
                                AND     confirmtype=%(confirmtype)s
                                AND     confirmasked=%(confirmasked)s
                                ORDER BY idta DESC
                                ''',
                                 {'status': 400, 'statust': DONE, 'idroute': 'test997', 'confirmtype': 'ask-x12-997', 'confirmasked': True}):
            counter += 1
            if counter == 1:
                self.failUnless(not row[str('confirmed')])
                self.failUnless(row[str('confirmidta')] == 0)
            elif counter == 2:
                self.failUnless(row[str('confirmed')])
                self.failUnless(row[str('confirmidta')] != 0)
            else:
                break
        else:
            self.failUnless(counter != 0)
        for row in botslib.query(u'''SELECT idta,confirmed,confirmidta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                AND     idroute=%(idroute)s
                                AND     confirmtype=%(confirmtype)s
                                AND     confirmasked=%(confirmasked)s
                                ORDER BY idta DESC
                                ''',
                                 {'status': 310, 'statust': DONE, 'idroute': 'test997', 'confirmtype': 'send-x12-997', 'confirmasked': True}):
            counter += 1
            if counter <= 2:
                self.failUnless(row[str('confirmed')])
                self.failUnless(row[str('confirmidta')] != 0)
            else:
                break
        else:
            self.failUnless(counter != 0)

    def testroutetestcontrl(self):
        '''
        test997 1:  pickup ORDERS*1   ask confirm ORDERS*2   gen & send ORDERS*2
                                      send confirm ORDERS*1  gen & send CONTRL*1
        test997 2:  receive CONTRL*1  confirm ORDERS*1       gen xml*1
                    receive ORDERS*2  ask confirm ORDERS*3   gen ORDERS*3
                                      send confirm ORDERS*2  gen & send CONTRL*2
        test997 3:  receive CONTRL*2  confirm ORDERS*2       gen & send xml (to trash)
                                                             send ORDERS*3 (to trash)
                                                             send xml (to trash)
        '''
        lijst = utilsunit.getdir(os.path.join(botssys, 'outfile/confirm/edifact/*'))
        self.failUnless(len(lijst) == 0)
        lijst = utilsunit.getdir(os.path.join(botssys, 'outfile/confirm/trash/*'))
        self.failUnless(len(lijst) == 6)
        counter = 0
        for row in botslib.query(u'''SELECT idta,confirmed,confirmidta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                AND     idroute=%(idroute)s
                                AND     confirmtype=%(confirmtype)s
                                AND     confirmasked=%(confirmasked)s
                                ORDER BY idta DESC
                                ''',
                                 {'status': 400, 'statust': DONE, 'idroute': 'testcontrl', 'confirmtype': 'ask-edifact-CONTRL', 'confirmasked': True}):
            counter += 1
            if counter == 1:
                self.failUnless(not row[str('confirmed')])
                self.failUnless(row[str('confirmidta')] == 0)
            elif counter == 2:
                self.failUnless(row[str('confirmed')])
                self.failUnless(row[str('confirmidta')] != 0)
            else:
                break
        else:
            self.failUnless(counter != 0)
        for row in botslib.query(u'''SELECT idta,confirmed,confirmidta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                AND     idroute=%(idroute)s
                                AND     confirmtype=%(confirmtype)s
                                AND     confirmasked=%(confirmasked)s
                                ORDER BY idta DESC
                                ''',
                                 {'status': 310, 'statust': DONE, 'idroute': 'testcontrl', 'confirmtype': 'send-edifact-CONTRL', 'confirmasked': True}):
            counter += 1
            if counter <= 2:
                self.failUnless(row[str('confirmed')])
                self.failUnless(row[str('confirmidta')] != 0)
            else:
                break
        else:
            self.failUnless(counter != 0)

    def testconfirmrulesdirect(self):
        self.failUnless(True == botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel',
                                                          topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype'))
        self.failUnless(True == botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel',
                                                          topartner='topartner', frompartner='frompartner', editype='x12', messagetype='justfortes'))
        self.failUnless(True == botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel',
                                                          topartner='topartner', frompartner='frompartner', editype='x12', messagetype='justfortest2'))
        self.failUnless(False == botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel',
                                                           topartner='topartner', frompartner='frompartner', editype='x12', messagetype='justfortest'))

        self.failUnless(True == botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='tochannel',
                                                          topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype'))
        self.failUnless(False == botslib.checkconfirmrules('send-email-MDN', idroute='otherx12', idchannel='tochannel',
                                                           topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype'))
        self.failUnless(False == botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='mdn2_in',
                                                           topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype'))
        self.failUnless(False == botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='tochannel',
                                                           topartner='partnerunittest', frompartner='frompartner', editype='x12', messagetype='messagetype'))
        self.failUnless(False == botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='tochannel',
                                                           topartner='topartner', frompartner='partnerunittest', editype='x12', messagetype='messagetype'))
        self.failUnless(False == botslib.checkconfirmrules('send-email-MDN', idroute='otherx12', idchannel='mdn2_in',
                                                           topartner='partnerunittest', frompartner='partnerunittest', editype='x12', messagetype='messagetype'))
        self.failUnless(True == botslib.checkconfirmrules('send-email-MDN', idroute='otherx1', idchannel='mdn2_i',
                                                          topartner='partnerunittes', frompartner='partnerunittes', editype='x12', messagetype='messagetype'))


if __name__ == '__main__':
    pythoninterpreter = 'python2.7'
    newcommand = [pythoninterpreter, 'bots-engine.py', ]
    shutil.rmtree(os.path.join(botssys, 'outfile'), ignore_errors=True)  # remove whole output directory
    subprocess.call(newcommand)
    print('''expect:
    21 files received/processed in run.
    17 files without errors,
    4 files with errors,
    30 files send in run.
    ''')
    #connect to database etc
    #check nrs confirmed etc.
    botsinit.generalinit('config')
    botsinit.initenginelogging('engine')
    botsinit.connect()
    botslib.prepare_confirmrules()
    unittest.main()
    logging.shutdown()
    botsglobal.db.close()
