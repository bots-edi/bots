# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import unittest
import subprocess
import logging
import datetime
import sys
import tests.utilsunit
import bots.botslib as botslib
import bots.botsinit as botsinit
import bots.botsglobal as botsglobal
import bots.communication as communication
from bots.botsconfig import *
if sys.version_info[0] > 2:
    basestring = unicode = str

'''
plugin unitfilenameout.zip
active all routes
no acceptance-test!
'''

botssys = 'bots/botssys'


class TestMain(unittest.TestCase):

    def testroutetestmdn(self):
        comclass = communication._comsession(channeldict={
                                             'idchannel': 'dutchic_desadv_out'}, idroute='dutchic_desadv', userscript=None, scriptname=None, command='new', rootidta=0)
        count = 0
        for row in botslib.query(u'''SELECT idta
                                FROM    ta
                                WHERE   status=%(status)s
                                AND     statust=%(statust)s
                                ORDER BY idta DESC
                                ''',
                                 {'status': 520, 'statust': DONE, 'idroute': 'testmdn', 'confirmtype': 'send-email-MDN', 'confirmasked': True}):
            count += 1
            sub_unique = botslib.unique('dutchic_desadv_out')
            ta = botslib.OldTransaction(row[str('idta')])

            self.assertEqual(comclass.filename_formatter('*.edi', ta), str(sub_unique + 1) + '.edi', '')
            self.assertEqual(comclass.filename_formatter('*.edi', ta), str(sub_unique + 2) + '.edi', '')
            self.assertEqual(comclass.filename_formatter('*.edi', ta), str(sub_unique + 3) + '.edi', '')
            self.assertEqual(comclass.filename_formatter('{messagetype}/{editype}/{topartner}/{frompartner}/{botskey}_*', ta),
                             'DESADVD96AUNEAN005/edifact/8712345678920/8712345678910/VERZENDVB8_' + str(sub_unique + 4), '')
            self.assertEqual(comclass.filename_formatter(
                '*_{datetime:%Y-%m-%d}.edi', ta), str(sub_unique + 5) + '_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.edi', '')
            self.assertEqual(comclass.filename_formatter('*_*.edi', ta),
                             str(sub_unique + 6) + '_' + str(sub_unique + 6) + '.edi', '')
            self.assertEqual(comclass.filename_formatter('123.edi', ta), '123.edi', '')
            self.assertEqual(comclass.filename_formatter('{infile}', ta), 'desadv1.edi', '')
            self.assertEqual(comclass.filename_formatter('{infile:name}.txt', ta), 'desadv1.txt', '')
            self.assertEqual(comclass.filename_formatter('{infile:name}.{infile:ext}', ta), 'desadv1.edi', '')
            print('expect: <idta>.edi                          ', comclass.filename_formatter('{idta}.edi', ta))
            self.assertRaises(botslib.CommunicationOutError, comclass.filename_formatter, '{tada}', ta)
            self.assertRaises(botslib.CommunicationOutError, comclass.filename_formatter, '{infile:test}', ta)
            if count == 1:  # test only 1 incoming files
                break


if __name__ == '__main__':
    pythoninterpreter = 'python3.4'
    newcommand = [pythoninterpreter, 'bots-engine.py', ]
    subprocess.call(newcommand)

    botsinit.generalinit('config')
    botsinit.initenginelogging('engine')
    botsinit.connect()
    unittest.main()
    logging.shutdown()
    botsglobal.db.close()
