#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bots.botslib as botslib
import bots.botsglobal as botsglobal
import bots.botsinit as botsinit

'''
no plugin needed.
run in commandline.
should give no errors.
utf-16 etc are reported.
'''


def testraise(expect, msg2, *args, **kwargs):
    try:
        raise botslib.BotsError(msg2, *args, **kwargs)
    except Exception, msg:
        if not isinstance(msg, unicode):
            msg = unicode(msg)
            #~ print 'not unicode',type(msg),expect
            #~ print 'Error xxx\n',msg
        if expect:
            if unicode(expect) != msg.strip():
                print expect, '(expected)'
                print msg, '(received)'
        txt = botslib.txtexc()
        if not isinstance(txt, unicode):
            print 'Error txt\n', txt


# .decode(): bytes->unicode
# .encode(): unicode -> bytes


def testrun():
    print '\n'
    #normal, valid handling
    testraise('', '', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise('0test', '0test', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise('0test test1 test2', '0test %(test1)s %(test2)s %(test4)s',
              {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise('1test test1 test2 test3', '1test %(test1)s %(test2)s %(test3)s',
              {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise(u'2test test1 test2 test3', u'2test %(test1)s %(test2)s %(test3)s',
              {u'test1': u'test1', u'test2': u'test2', u'test3': u'test3'})
    #different inputs in BotsError
    testraise(u'3test', '3test')
    testraise(u'4test test1 test2', u'4test %(test1)s %(test2)s %(test3)s', {u'test1': u'test1', u'test2': u'test2'})
    testraise(u'5test test1 test2', u'5test %(test1)s %(test2)s %(test3)s', test1=u'test1', test2=u'test2')
    testraise(u'6test', u'6test %(test1)s %(test2)s %(test3)s', u'test1')
    testraise(u"7test [u'test1', u'test2']", u'7test %(test1)s %(test2)s %(test3)s', test1=[u'test1', u'test2'])
    testraise(u"8test {u'test1': u'test1', u'test2': u'test2'}",
              u'8test %(test1)s %(test2)s %(test3)s', test1={u'test1': u'test1', u'test2': u'test2'})
    testraise(u"9test [<module 'bots.botslib' from '/home/hje/Bots/botsdev/bots/botslib.pyc'>, <module 'bots.botslib' from '/home/hje/Bots/botsdev/bots/botslib.pyc'>]",
              u'9test %(test1)s %(test2)s %(test3)s', test1=[botslib, botslib])

    #different charsets in BotsError
    testraise(u'12test test1 test2 test3', u'12test %(test1)s %(test2)s %(test3)s',
              {u'test1': u'test1', u'test2': u'test2', u'test3': u'test3'})
    testraise(u'13test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test2\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test3\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
              u'13test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s %(test2)s %(test3)s',
              {u'test1': u'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202', u'test2': u'test2\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202', u'test3': u'test3\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'})
    testraise(u'14test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
              u'14test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s'.encode('utf_8'),
              {u'test1': u'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_8')})
    testraise(u'15test test1',
              u'15test %(test1)s',
              {u'test1': u'test1'.encode('utf_16')})
    testraise(u'16test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
              u'16test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s',
              {u'test1': u'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_16')})
    testraise(u'17test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
              u'17test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s',
              {u'test1': u'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_32')})
    testraise(u'18test\u00E9\u00EB\u00FA\u00FB\u00FC test1\u00E9\u00EB\u00FA\u00FB\u00FC',
              u'18test\u00E9\u00EB\u00FA\u00FB\u00FC %(test1)s',
              {u'test1': u'test1\u00E9\u00EB\u00FA\u00FB\u00FC'.encode('latin_1')})
    testraise(u'19test test1',
              u'19test %(test1)s',
              {u'test1': u'test1'.encode('cp500')})
    testraise(u'20test test1',
              u'20test %(test1)s',
              {u'test1': u'test1'.encode('euc_jp')})
    #make utf-8 unicode string,many chars
    l = []
    for i in xrange(0, pow(256, 2)):
        l.append(unichr(i))
    s = u''.join(l)
    print type(s)
    testraise(u'', s)
    #~ print type(s)
    s2 = s.encode('utf-8')
    print type(s2)
    testraise(u'', s2)

    #make iso-8859-1 string,many chars
    l = []
    for i in range(0, 256):
        l.append(chr(i))
    s = ''.join(l)
    print type(s)
    #~ print s
    testraise(u'', s)
    s2 = s.decode('latin_1')
    print type(s2)
    testraise(u'', s2)


if __name__ == '__main__':
    botsinit.generalinit('config')
    botsinit.initbotscharsets()
    botsglobal.logger = botsinit.initenginelogging('engine')
    botsglobal.ini.set('settings', 'debug', 'False')
    testrun()
    botsglobal.ini.set('settings', 'debug', 'True')
    testrun()
