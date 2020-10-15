#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import filecmp
import os
import sys
import logging
import subprocess
import glob
#import bots-modules
import tests.utilsunit
import bots.botslib as botslib
import bots.botsinit as botsinit
import bots.botsglobal as botsglobal
import bots.transform as transform
from bots.botsconfig import *
if sys.version_info[0] > 2:
    basestring = unicode = str

'''
plugin 'unit_multi_1'
enable routes
not an acceptance test.
'''


def test_plugin():
    for row in botslib.query(u'''SELECT COUNT(*) as count
                                FROM    partner
                                WHERE   isgroup = %(isgroup)s ''',
                             {'isgroup': False}):
        if row[str('count')] != 5:
            raise Exception('error partner count')
        break
    else:
        raise Exception('no partner count?')
    for row in botslib.query(u'''SELECT COUNT(*) as count
                                FROM    partner
                                WHERE   isgroup = %(isgroup)s ''',
                             {'isgroup': True}):
        if row[str('count')] != 3:
            raise Exception('error partner count')
        break
    else:
        raise Exception('no partner count?')
    for row in botslib.query(u'''SELECT COUNT(*) as count
                                    FROM partnergroup
                                    WHERE from_partner_id=%(from_partner_id)s  ''',
                             {'from_partner_id': 'plugintest1'}):
        if row[str('count')] != 3:
            raise Exception('error partner count')
        break
    else:
        raise Exception('no partner count?')
    for row in botslib.query(u'''SELECT to_partner_id
                                    FROM partnergroup
                                    WHERE from_partner_id=%(from_partner_id)s  ''',
                             {'from_partner_id': 'plugintest2'}):
        if row[str('to_partner_id')] != 'plugingroup2':
            raise Exception('error partner count')
    for row in botslib.query(u'''SELECT COUNT(*) as count
                                    FROM partnergroup
                                    WHERE to_partner_id=%(to_partner_id)s  ''',
                             {'to_partner_id': 'plugingroup2'}):
        if row[str('count')] != 2:
            raise Exception('error partner count')
        break
    else:
        raise Exception('no partner count?')


def test_ccode_with_unicode():
    domein = 'test'
    tests = [(u'key1', u'leftcode'),
             (u'key2', u'~!@#$%^&*()_+}{:";][=-/.,<>?`'),
             (u'key3', u'?�r����?�s??lzcn?'),
             (u'key4', u'?�?����䴨???�?��'),
             (u'key5', u'��???UI��?�`~'),
             (u'key6', u"a\xac\u1234\u20ac\U00008000"),
             (u'key7', u"abc_\u03a0\u03a3\u03a9.txt"),
             (u'key8', u"?�R����?�S??LZCN??"),
             (u'key9', u"�?�YܨI����???�?���`�`Z?"),
             ]
    try:  # clean before test
        botslib.changeq(u'''DELETE FROM ccode ''')
        botslib.changeq(u'''DELETE FROM ccodetrigger''')
    except:
        print('Error while deleting: ', botslib.txtexc())
        raise
    try:
        botslib.changeq(u'''INSERT INTO ccodetrigger (ccodeid)
                                VALUES (%(ccodeid)s)''',
                        {'ccodeid': domein})
        for key, value in tests:
            botslib.changeq(u'''INSERT INTO ccode (ccodeid_id,leftcode,rightcode,attr1,attr2,attr3,attr4,attr5,attr6,attr7,attr8)
                                    VALUES (%(ccodeid)s,%(leftcode)s,%(rightcode)s,'1','1','1','1','1','1','1','1')''',
                            {'ccodeid': domein, 'leftcode': key, 'rightcode': value})
    except:
        print('Error while updating: ', botslib.txtexc())
        raise
    try:
        for key, value in tests:
            print('key', key)
            for row in botslib.query(u'''SELECT rightcode
                                        FROM    ccode
                                        WHERE   ccodeid_id = %(ccodeid)s
                                        AND     leftcode = %(leftcode)s''',
                                     {'ccodeid': domein, 'leftcode': key}):
                print('    ', key, type(row[str('rightcode')]), type(value))
                if row[str('rightcode')] != value:
                    print('failure in test "%s": result "%s" is not equal to "%s"' % (key, row['rightcode'], value))
                else:
                    print('    OK')
                break
            else:
                print('??can not find testentry %s %s in db' % (key, value))
    except:
        print('Error while quering db: ', botslib.txtexc())
        raise


def test_unique_in_run_counter():
    if 1 != int(transform.unique_runcounter('test')):
        raise Exception('test_unique_in_run_counter')
    if 1 != int(transform.unique_runcounter('test2')):
        raise Exception('test_unique_in_run_counter')
    if 2 != int(transform.unique_runcounter('test')):
        raise Exception('test_unique_in_run_counter')
    if 3 != int(transform.unique_runcounter('test')):
        raise Exception('test_unique_in_run_counter')
    if 2 != int(transform.unique_runcounter('test2')):
        raise Exception('test_unique_in_run_counter')


def test_partner_lookup():
    for s in [str('attr1'), str('attr2'), str('attr3'), str('attr4'), str('attr5')]:
        if transform.partnerlookup('test', s) != s:
            raise Exception('test_partner_lookup')
    #test lookup for not existing partner
    idpartner = 'partner_not_there'
    if transform.partnerlookup(idpartner, 'attr1', safe=True) != idpartner:
        raise Exception('test_partner_lookup')
    try:
        transform.partnerlookup(idpartner, 'attr1')
    except botslib.CodeConversionError as msg:
        pass
    else:
        raise Exception('expect exception in test_partner_lookup')

    #test lookup where no value is in the database
    idpartner = 'test2'
    if transform.partnerlookup(idpartner, str('attr1')) != 'attr1':
        raise Exception('test_partner_lookup')
    try:
        transform.partnerlookup(idpartner, str('attr2'))
    except botslib.CodeConversionError as msg:
        pass
    else:
        raise Exception('expect exception in test_partner_lookup')


def grammartest(l, expect_error=True):
    if expect_error:
        if not subprocess.call(l):
            raise Exception('grammartest: expected error, but no error')
    else:
        if subprocess.call(l):
            raise Exception('grammartest: expected no error, but received an error')


if __name__ == '__main__':
    pythoninterpreter = 'python2.7'
    botsinit.generalinit('config')
    utilsunit.dummylogger()
    utilsunit.cleanoutputdir()
    botssys = botsglobal.ini.get('directories', 'botssys')
    botsinit.connect()
    #*************************************************************************
    #test references *********************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'testreference'],
                                    {'status': 0, 'lastreceived': 1, 'lasterror': 0, 'lastdone': 1, 'lastok': 0, 'lastopen': 0, 'send': 1, 'processerrors': 0, 'filesize': 262})
    ta_externout = utilsunit.getlastta(EXTERNOUT)
    if ta_externout[str('botskey')] != 'BOTSKEY01':
        raise Exception('testreference: botskey not OK')
    ta_externout = utilsunit.getlastta(PARSED)
    if ta_externout[str('reference')] != 'UNBREF01':
        raise Exception('testreference: unb ref not OK')
    ta_externout = utilsunit.getlastta(SPLITUP)
    if ta_externout[str('reference')] != 'BOTSKEY01':
        raise Exception('testreference: botskey not OK')
    if ta_externout[str('botskey')] != 'BOTSKEY01':
        raise Exception('testreference: botskey not OK')
    ta_externout = utilsunit.getlastta(TRANSLATED)
    if ta_externout[str('reference')] != 'BOTSKEY01':
        raise Exception('testreference: botskey not OK')
    if ta_externout[str('botskey')] != 'BOTSKEY01':
        raise Exception('testreference: botskey not OK')
    #test KECA charset *******************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'testkeca'],
                                    {'status': 0, 'lastreceived': 1, 'lasterror': 0, 'lastdone': 1, 'lastok': 0, 'lastopen': 0, 'send': 1, 'processerrors': 0, 'filesize': 333})
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'testkeca2'],
                                    {'status': 0, 'lastreceived': 1, 'lasterror': 0, 'lastdone': 1, 'lastok': 0, 'lastopen': 0, 'send': 1, 'processerrors': 0, 'filesize': 333})
    #mailbag *****************************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'mailbagtest'],
                                    {'status': 0, 'lastreceived': 18, 'lasterror': 0, 'lastdone': 18, 'lastok': 0, 'lastopen': 0, 'send': 44, 'processerrors': 0, 'filesize': 39344})
    #passthroughtest *********************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'passthroughtest'],
                                    {'status': 0, 'lastreceived': 4, 'lasterror': 0, 'lastdone': 4, 'lastok': 0, 'lastopen': 0, 'send': 4, 'processerrors': 0, 'filesize': 7346})
    #botsidnr ****************************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'test_botsidnr', 'test_changedelete'],
                                    {'status': 0, 'lastreceived': 2, 'lasterror': 0, 'lastdone': 2, 'lastok': 0, 'lastopen': 0, 'send': 4, 'processerrors': 0, 'filesize': 5813})
    infile = 'infile/test_botsidnr/compare/unitnodebotsidnr1.edi'
    outfile = 'outfile/test_botsidnr/unitnodebotsidnr1.edi'
    infile2 = 'infile/test_botsidnr/compare/unitnodebotsidnr2.edi'
    outfile2 = 'outfile/test_botsidnr/unitnodebotsidnr2.edi'
    if not filecmp.cmp(os.path.join(botssys, infile), os.path.join(botssys, outfile)):
        raise Exception('error in file compare')
    if not filecmp.cmp(os.path.join(botssys, infile2), os.path.join(botssys, outfile2)):
        raise Exception('error in file2 compare')
    #*************************************************************************
    test_ccode_with_unicode()
    #*************************************************************************
    test_unique_in_run_counter()
    #*************************************************************************
    test_partner_lookup()
    #*************************************************************************
    # testgrammar: tricky grammars and messages (collision tests). these test
    # should run OK (no grammar-errors, reading & writing OK, extra checks in
    # mappings scripts have to be OK
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'testgrammar'],
                                    {'status': 0, 'lastreceived': 8, 'lasterror': 0, 'lastdone': 8, 'lastok': 0, 'lastopen': 0, 'send': 9, 'processerrors': 0, 'filesize': 2329})
    #grammar/Collision testing************************************************
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNERR001'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNERR002'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNERR003'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNERR004'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNERR005'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNERR006'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNbackcollision2'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNbackcollision3'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CUSCARD96AUNnestedcollision1'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CUSCARD96AUNnestedcollision2'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CUSCARD96AUNnestedcollision3'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'DELFORD96AUNbackcollision'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'DELJITD96AUNbackcollision'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'INVRPTD96AUNnestingcollision'])
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNno'], expect_error=False)
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONDRAD96AUNno2'], expect_error=False)
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONESTD96AUNno'], expect_error=False)
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CONESTD96AUNno2'], expect_error=False)
    grammartest([pythoninterpreter, 'bots-grammarcheck.py', 'edifact', 'CUSCARD96AUNno'], expect_error=False)
    #plugin testing: check if right entries have been read (partners/patnergro
    test_plugin()
    #csv_orders_inputtest (csv with records too big.small.not correct ending e
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'csv_orders_inputtest'],
                                    {'status': 1, 'lastreceived': 5, 'lasterror': 2, 'lastdone': 3, 'lastok': 0, 'lastopen': 0, 'send': 3, 'processerrors': 0, 'filesize': 131})
    #testextendedalt function*************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'testextendedalt'],
                                    {'status': 0, 'lastreceived': 1, 'lasterror': 0, 'lastdone': 1, 'lastok': 0, 'lastopen': 0, 'send': 3, 'processerrors': 0, 'filesize': 261})
    #testincomingmime ********************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'testincomingmime'],
                                    {'status': 1, 'lastreceived': 5, 'lasterror': 5, 'lastdone': 0, 'lastok': 0, 'lastopen': 0, 'send': 0, 'processerrors': 0, 'filesize': 22592})
    #*************************************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'testxml_outspecials'],
                                    {'status': 0, 'lastreceived': 2, 'lasterror': 0, 'lastdone': 2, 'lastok': 0, 'lastopen': 0, 'send': 2, 'processerrors': 0, 'filesize': 1337})
    cmpfile = 'infile/testxml_outspecials/compare/01xml02OK.xml'
    outfilepath = 'outfile/testxml_outspecials/*'
    for filename in glob.glob(os.path.join(botssys, outfilepath)):
        if not filecmp.cmp(os.path.join(botssys, cmpfile), filename):
            raise Exception('error in file compare')
    #*************************************************************************
    #mailbag *****************************************************************
    utilsunit.RunTestCompareResults([pythoninterpreter, 'bots-engine.py', 'maxsizeinfile'],
                                    {'status': 1, 'lastreceived': 1, 'lasterror': 1, 'lastdone': 0, 'lastok': 0, 'lastopen': 0, 'send': 0, 'processerrors': 0, 'filesize': 6702825})
    #*************************************************************************
    #*************************************************************************
    logging.shutdown()
    botsglobal.db.close
    print('Tests OK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
