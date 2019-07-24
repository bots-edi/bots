# -*- coding: utf-8 -*-

from __future__ import print_function

# python2: gives problems; this module contains unicode strings; in function ccode ascii strings are needed (for field).
from __future__ import unicode_literals
import sys
import unittest
import utilsunit
import time
import bots.botsglobal as botsglobal
import bots.botslib as botslib
import bots.botsinit as botsinit
import bots.inmessage as inmessage
import bots.transform as transform
import bots.validate_email as validate_email

if sys.version_info[0] > 2:
    basestring = unicode = str

"""plugin unittranslateutils.zip
in bots.ini:  runacceptancetest = False
"""


class MyObject(object):
    c = "c_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ"

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


def persist_lookup_ts(domein, botskey):
    """ lookup persistent values in db.
    """
    for row in botslib.query(
        """SELECT ts
                                FROM persist
                                WHERE domein=%(domein)s
                                AND botskey=%(botskey)s""",
        {"domein": domein, "botskey": botskey},
    ):
        return row[str("ts")]
    return None


class TestTranslate(unittest.TestCase):
    def setUp(self):
        pass

    def testpersist_strings(self):
        # inn = inmessage.parse_edi_file(editype='edifact',messagetype='orderswithenvelope',filename='botssys/infile/tests/inisout02.edi')
        domein = "test"
        botskey = "test"
        value = "abcdedfgh"
        value2 = "IEFJUKAHE*FMhrt4hr f.wch shjeriw"
        value3 = "1" * 3024
        transform.persist_delete(domein, botskey)
        # self.assertRaises(botslib.PersistError,transform.persist_add,domein,botskey,value3)   #content is too long
        transform.persist_add(domein, botskey, value)
        self.assertRaises(
            botslib.PersistError, transform.persist_add, domein, botskey, value
        )  # is already present
        self.assertEqual(value, transform.persist_lookup(domein, botskey), "basis")
        transform.persist_update(domein, botskey, value2)
        self.assertEqual(value2, transform.persist_lookup(domein, botskey), "basis")
        # self.assertRaises(botslib.PersistError,transform.persist_update,domein,botskey,value3)   #content is too long
        transform.persist_delete(domein, botskey)
        self.assertEqual(None, transform.persist_lookup(domein, botskey), "basis")
        transform.persist_update(
            domein, botskey, value
        )  # test-tet is not there. gives no error...

    def testpersist_unicode(self):
        domein = "test"
        botskey = "ëö1235:\ufb52\ufb66\ufedb"
        botskey3 = "ëö135:\ufb52\ufb66\ufedb"
        value = "xxxxxxxxxxxxxxxxx"
        value2 = "IEFJUKAHE*FMhr\u0302\u0267t4hr f.wch shjeriw"
        value3 = "1/2/d" * 3024
        transform.persist_delete(domein, botskey)
        transform.persist_delete(domein, botskey3)
        transform.persist_add(domein, botskey3, value3)
        self.assertEqual(value3, transform.persist_lookup(domein, botskey3), "basis")
        transform.persist_add(domein, botskey, value)
        self.assertRaises(
            botslib.PersistError, transform.persist_add, domein, botskey, value
        )  # is already present
        self.assertEqual(value, transform.persist_lookup(domein, botskey), "basis")
        transform.persist_update(domein, botskey, value2)
        self.assertEqual(value2, transform.persist_lookup(domein, botskey), "basis")
        # self.assertRaises(botslib.PersistError,transform.persist_update,domein,botskey,value3)   #content is too long
        transform.persist_delete(domein, botskey)
        self.assertEqual(None, transform.persist_lookup(domein, botskey), "basis")
        transform.persist_update(
            domein, botskey, value
        )  # is not there. gives no error...

    def testpersist_moreunicode(self):
        domein = "test"
        botskey = "éëèêíïìîóöòõôúüùûáäàãâ\ufb52\ufb66\ufedb"
        botskey3 = "ëéèõöóòñýÿÖÓÒÕ"
        value = "éëèêíïìîóöòõôúüùûáäàãâ\ufb52\ufb66\ufedbñýÿÖÓÒÕ"
        value2 = "ëéèõöóò"
        value3 = "1/2/dñýÿÖÓÒÕ" * 3024
        transform.persist_delete(domein, botskey)
        transform.persist_delete(domein, botskey3)
        transform.persist_add(domein, botskey3, value3)
        self.assertEqual(value3, transform.persist_lookup(domein, botskey3), "basis")
        transform.persist_add(domein, botskey, value)
        self.assertRaises(
            botslib.PersistError, transform.persist_add, domein, botskey, value
        )  # is already present
        self.assertEqual(value, transform.persist_lookup(domein, botskey), "basis")
        transform.persist_update(domein, botskey, value2)
        self.assertEqual(value2, transform.persist_lookup(domein, botskey), "basis")
        # ~ #self.assertRaises(botslib.PersistError,transform.persist_update,domein,botskey,value3)   #content is too long
        transform.persist_delete(domein, botskey)
        self.assertEqual(None, transform.persist_lookup(domein, botskey), "basis")
        transform.persist_update(
            domein, botskey, value
        )  # is not there. gives no error...

    def testpersist_object(self):
        """ use objects for pickling
        """
        domein = "test"
        botskey = "éëèêíïìîóöòõôúüùûáäàãâ\ufb52\ufb66\ufedb"
        myobject = MyObject(
            "a_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ", "b_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ"
        )
        myobject.d = "1_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ"
        myobject.e = 12345
        transform.persist_delete(domein, botskey)
        transform.persist_add(domein, botskey, myobject)
        self.assertEqual(myobject, transform.persist_lookup(domein, botskey), "basis")

    def testpersist_timestamp(self):
        # inn = inmessage.parse_edi_file(editype='edifact',messagetype='orderswithenvelope',filename='botssys/infile/tests/inisout02.edi')
        domein = "test"
        botskey = "timestamp"
        value = "abcdedfgh"
        value2 = "IEFJUKAHE*FMhrt4hr f.wch shjeriw"
        value3 = "1" * 3024
        transform.persist_delete(domein, botskey)
        # self.assertRaises(botslib.PersistError,transform.persist_add,domein,botskey,value3)   #content is too long
        transform.persist_add(domein, botskey, value)
        ts1 = persist_lookup_ts(domein, botskey)
        time.sleep(1)
        self.assertRaises(
            botslib.PersistError, transform.persist_add, domein, botskey, value
        )  # is already present
        self.assertEqual(value, transform.persist_lookup(domein, botskey), "basis")
        transform.persist_update(domein, botskey, value2)
        self.assertEqual(value2, transform.persist_lookup(domein, botskey), "basis")
        ts2 = persist_lookup_ts(domein, botskey)
        print(ts1, ts2)

    def testgetcodeset(self):
        self.assertEqual(
            ["TESTOUT"], transform.getcodeset("artikel", "TESTIN"), "test getcodeset"
        )
        # print(transform.getcodeset('list','list'))
        self.assertEqual(
            ["1", "2", "4", "5"],
            transform.getcodeset("list", "list"),
            "test getcodeset",
        )

    def testdatemask(self):
        self.assertEqual(
            "20121231",
            transform.datemask("12/31/2012", "MM/DD/YYYY", "YYYYMMDD"),
            "test datemask",
        )
        self.assertEqual(
            "201231",
            transform.datemask("12/31/2012", "MM/DD/YYYY", "YYMMDD"),
            "test datemask",
        )

    def testuseoneof(self):
        self.assertEqual("test", transform.useoneof(None, "test"), "test useoneof")
        self.assertEqual(
            "test", transform.useoneof("test", "test1", "test2"), "test useoneof"
        )
        self.assertEqual(None, transform.useoneof(), "test useoneof")
        self.assertEqual(None, transform.useoneof(()), "test useoneof")
        self.assertEqual(None, transform.useoneof(""), "test useoneof")
        self.assertEqual(
            None, transform.useoneof(None, None, None, None), "test useoneof"
        )

    def testuseoneofalt(self):
        self.assertEqual("test", None or "test", "test useoneof")
        self.assertEqual("test", "test" or "test1" or "test2", "test useoneof")
        self.assertEqual(None, None, "test useoneof")
        self.assertEqual(None, None or None or None or None, "test useoneof")
        self.assertEqual("t", None or "" or None or "t", "test useoneof")

    def testdateformat(self):
        self.assertEqual(None, transform.dateformat(""), "test dateformat")
        self.assertEqual(None, transform.dateformat(None), "test dateformat")
        self.assertEqual("102", transform.dateformat("12345678"), "test dateformat")
        # ~ #self.assertEqual(None,transform.dateformat('123456789'),'test dateformat')
        self.assertRaises(botslib.BotsError, transform.dateformat, "123456789")
        # ~ #self.assertEqual(None,transform.dateformat('1234567'),'test dateformat')
        self.assertRaises(botslib.BotsError, transform.dateformat, "1234567")
        self.assertEqual("203", transform.dateformat("123456789012"), "test dateformat")
        self.assertEqual(
            "718", transform.dateformat("1234567890123456"), "test dateformat"
        )

    def testtruncate(self):
        self.assertEqual(None, transform.truncate(5, None), "test truncate")
        self.assertEqual("artik", transform.truncate(5, "artikel"), "test truncate")
        self.assertEqual("artikel", transform.truncate(10, "artikel"), "test truncate")
        self.assertEqual("a", transform.truncate(1, "artikel"), "test truncate")
        self.assertEqual("", transform.truncate(0, "artikel"), "test truncate")

    def testconcat(self):
        self.assertEqual(None, transform.concat(None, None), "test concatenate")
        self.assertEqual(
            "artikel", transform.concat("artikel", None), "test concatenate"
        )
        self.assertEqual(
            "artikel", transform.concat(None, "artikel"), "test concatenate"
        )
        self.assertEqual("artikel", transform.concat("", "artikel"), "test concatenate")
        self.assertEqual(
            "artikel1artikel2",
            transform.concat("artikel1", "artikel2"),
            "test concatenate",
        )
        self.assertEqual(
            "artikel1 artikel2",
            transform.concat("artikel1", "artikel2", sep=" "),
            "test concatenate",
        )
        self.assertEqual(
            "artikel1\nartikel2",
            transform.concat("artikel1", "artikel2", sep="\n"),
            "test concatenate",
        )
        self.assertEqual(
            "artikel1<br>artikel2<br>artikel3",
            transform.concat("artikel1", "artikel2", "artikel3", sep="<br>"),
            "test concatenate",
        )

    def testunique(self):
        newdomain = "test" + transform.unique("test")
        self.assertEqual("1", transform.unique(newdomain), "init new domain")
        self.assertEqual("2", transform.unique(newdomain), "next one")
        self.assertEqual("3", transform.unique(newdomain), "next one")
        self.assertEqual("4", transform.unique(newdomain), "next one")

        newdomain = "test" + transform.unique("test")
        self.assertEqual(True, transform.checkunique(newdomain, 1), "init new domain")
        self.assertEqual(False, transform.checkunique(newdomain, 1), "seq should be 2")
        self.assertEqual(False, transform.checkunique(newdomain, 3), "seq should be 2")
        self.assertEqual(True, transform.checkunique(newdomain, 2), "next one")
        self.assertEqual(True, transform.checkunique(newdomain, 3), "next one")
        self.assertEqual(True, transform.checkunique(newdomain, 4), "next one")
        self.assertEqual(False, transform.checkunique(newdomain, 4), "next one")
        self.assertEqual(False, transform.checkunique(newdomain, 6), "next one")
        self.assertEqual(True, transform.checkunique(newdomain, 5), "next one")

        newdomain = "test" + transform.unique("test")
        self.assertEqual("1", transform.unique(newdomain), "init new domain")
        self.assertEqual(
            "1", transform.unique(newdomain, updatewith=999), "init new domain"
        )
        self.assertEqual(
            "999", transform.unique(newdomain, updatewith=9999), "init new domain"
        )
        self.assertEqual(
            "9999", transform.unique(newdomain, updatewith=9999), "init new domain"
        )
        self.assertEqual(
            "9999", transform.unique(newdomain, updatewith=20140404), "init new domain"
        )
        self.assertEqual(
            "20140404",
            transform.unique(newdomain, updatewith=20140405),
            "init new domain",
        )
        self.assertEqual(
            "20140405",
            transform.unique(newdomain, updatewith=20140406),
            "init new domain",
        )
        self.assertEqual(
            "20140406",
            transform.unique(newdomain, updatewith=20140407),
            "init new domain",
        )
        self.assertEqual(
            "20140407",
            transform.unique(newdomain, updatewith=20140408),
            "init new domain",
        )

    def testean(self):
        self.assertEqual(
            "123456789012", transform.addeancheckdigit("12345678901"), "UPC"
        )
        self.assertEqual("2", transform.calceancheckdigit("12345678901"), "UPC")
        self.assertEqual(True, transform.checkean("123456789012"), "UPC")
        self.assertEqual(False, transform.checkean("123456789011"), "UPC")
        self.assertEqual(False, transform.checkean("123456789013"), "UPC")

        self.assertEqual(
            "123456789012", transform.addeancheckdigit("12345678901"), "UPC"
        )
        self.assertEqual("2", transform.calceancheckdigit("12345678901"), "UPC")
        self.assertEqual(True, transform.checkean("123456789012"), "UPC")
        self.assertEqual(False, transform.checkean("123456789011"), "UPC")
        self.assertEqual(False, transform.checkean("123456789013"), "UPC")

        self.assertEqual("12345670", transform.addeancheckdigit("1234567"), "EAN8")
        self.assertEqual("0", transform.calceancheckdigit("1234567"), "EAN8")
        self.assertEqual(True, transform.checkean("12345670"), "EAN8")
        self.assertEqual(False, transform.checkean("12345679"), "EAN8")
        self.assertEqual(False, transform.checkean("12345671"), "EAN8")

        self.assertEqual(
            "1234567890128", transform.addeancheckdigit("123456789012"), "EAN13"
        )
        self.assertEqual("8", transform.calceancheckdigit("123456789012"), "EAN13")
        self.assertEqual(True, transform.checkean("1234567890128"), "EAN13")
        self.assertEqual(False, transform.checkean("1234567890125"), "EAN13")
        self.assertEqual(False, transform.checkean("1234567890120"), "EAN13")

        self.assertEqual(
            "12345678901231", transform.addeancheckdigit("1234567890123"), "EAN14"
        )
        self.assertEqual("1", transform.calceancheckdigit("1234567890123"), "EAN14")
        self.assertEqual(True, transform.checkean("12345678901231"), "EAN14")
        self.assertEqual(False, transform.checkean("12345678901230"), "EAN14")
        self.assertEqual(False, transform.checkean("12345678901236"), "EAN14")

        self.assertEqual(
            "123456789012345675", transform.addeancheckdigit("12345678901234567"), "UPC"
        )
        self.assertEqual("5", transform.calceancheckdigit("12345678901234567"), "UPC")
        self.assertEqual(True, transform.checkean("123456789012345675"), "UPC")
        self.assertEqual(False, transform.checkean("123456789012345670"), "UPC")
        self.assertEqual(False, transform.checkean("123456789012345677"), "UPC")

    def testvalidate_email(self):
        self.assertEqual(
            True, validate_email.validate_email_address("test@gmail.com"), ""
        )
        self.assertEqual(
            True, validate_email.validate_email_address("niceandsimple@example.com"), ""
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address(
                "a.little.lengthy.but.fine@dept.example.com"
            ),
            "",
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address(
                "disposable.style.email.with+symbol@example.com"
            ),
            "",
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address("other.email-with-dash@example.com"),
            "",
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address('"much.more unusual"@example.com'),
            "",
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address(
                '"very.unusual.@.unusual.com"@example.com'
            ),
            "",
        )
        # ~ #self.assertEqual(True,validate_email.validate_email_address('''"very.(),:;<>[]\".VERY.\"very@\\ \"very\".unusual"@strange.example.com'''),'')
        self.assertEqual(
            True, validate_email.validate_email_address("admin@mailserver1"), ""
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address(
                """#!$%&'*+-/=?^_`{}|~@example.org"""
            ),
            "",
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address(
                """"()<>[]:,;@\\\"!#$%&'*+-/=?^_`{}| ~.a"@example.org"""
            ),
            "",
        )
        self.assertEqual(
            True, validate_email.validate_email_address('" "@example.org'), ""
        )
        # ~ #self.assertEqual(True,validate_email.validate_email_address('üñîçøðé@example.com'),'')  #does work in 3.4, not in 2.7
        # ~ #self.assertEqual(True,validate_email.validate_email_address('test@üñîçøðé.com'),'')  #does work in 3.4, not in 2.7
        self.assertEqual(
            True, validate_email.validate_email_address('"test@test"@gmail.com'), ""
        )

        self.assertEqual(
            False, validate_email.validate_email_address("test.gmail.com"), ""
        )
        self.assertEqual(
            False, validate_email.validate_email_address("test@test@gmail.com"), ""
        )
        self.assertEqual(
            False,
            validate_email.validate_email_address(
                'a"b(c)d,e:f;g<h>i[j\k]l@example.com'
            ),
            "",
        )
        self.assertEqual(
            False,
            validate_email.validate_email_address('just"not"right@example.com'),
            "",
        )
        self.assertEqual(
            False,
            validate_email.validate_email_address('this is"not\allowed@example.com'),
            "",
        )
        self.assertEqual(
            False,
            validate_email.validate_email_address('this is"not\allowed@example.com'),
            "",
        )
        self.assertEqual(
            False, validate_email.validate_email_address("test..test@gmail.com"), ""
        )
        self.assertEqual(
            False, validate_email.validate_email_address("test.test@gmail..com"), ""
        )
        self.assertEqual(
            False, validate_email.validate_email_address("test test@gmail.com"), ""
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address(
                '"/C=NL/A=400NET/P=XXXXXX/O=XXXXXXXXXXXXXXXXXXXX XXXXXXXX/S=XXXXXXXXXXX XXXXXXXX/"@xgateprod.400net.nl'
            ),
            "",
        )
        self.assertEqual(
            False,
            validate_email.validate_email_address(
                "/C=NL/A=400NET/P=XXXXX/O=XXXXXXXXXX XXXXXXXXXXXXXXXXXX/S=XXXXXXXXXXX XXXXXXXX/@xgateprod.400net.nl"
            ),
            "",
        )
        self.assertEqual(
            True,
            validate_email.validate_email_address(
                "/C=NL/A=400NET/P=XXXXX/O=XXXXXXXXXXXXXXXXXXXXXXXXXXXX/S=XXXXXXXXXXXXXXXXXXX/@xgateprod.400net.nl"
            ),
            "",
        )

    def testchunk(self):
        self.assertEqual(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]],
            list(transform.chunk([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)),
        )
        self.assertEqual(
            ["a nic", "e exa", "mple ", "strin", "g"],
            list(transform.chunk("a nice example string", 5)),
        )
        self.assertEqual(
            [["a nic", "e exa"], ["mple ", "strin"], ["g"]],
            list(transform.chunk(list(transform.chunk("a nice example string", 5)), 2)),
        )
        self.assertEqual([], list(transform.chunk(list(transform.chunk("", 5)), 2)))
        self.assertEqual([], list(transform.chunk(list(transform.chunk(None, 5)), 2)))

    def testdiacritics(self):
        title = "äáãàâāăąåǻȁªấặắḁÄÁÃÀÂĀĂĄÅǞǠǺȀḀ,çćĉċčÇĆĈĊČ,éëêèêēĕėęěȅềe̊ËÉẼÈÊĒĔĖĘĚȄE̊,ïíìîĩįȉÏÍĨÌÎȈ,öóõòôơỏȍÖÓÕÒÔƠȌ,üúũùûưǖǘǚǜųȕÜÚŨÙÛƯǕǗǛȔ,ḃḋďḟĝġğĞĠĜḥḤķľḷḶṁńñǹňņÑṗ̥r̥̄řŕȑȐR̥R̥̄šŞȘťṫțẘWýÿÝžźż,ðæÆÐØßø,ƎƏƐƆƇƈđłȺⱥʉ,Ĳĳ¼½⁇ǳ™Ⅱ⑴⑩⒜㎝㏒"
        self.assertEqual(
            "aaaaaaaaaaaaaaaaAAAAAAAAAAAAAA,cccccCCCCC,eeeeeeeeeeeeeEEEEEEEEEEEE,iiiiiiiIIIIII,ooooooooOOOOOOO,uuuuuuuuuuuuUUUUUUUUUU,bddfgggGGGhHkllLmnnnnnNprrrrRRRsSStttwWyyYzzz,,,Ii11?dTI(1(cl",
            transform.dropdiacritics(title),
        )
        self.assertEqual(
            "äáãàâaaaåaaªaaaaÄÁÃÀÂAAAÅAAAAA,çccccÇCCCC,éëêèêeeeeeeeeËÉEÈÊEEEEEEE,ïíìîiiiÏÍIÌÎI,öóõòôoooÖÓÕÒÔOO,üúuùûuuuuuuuÜÚUÙÛUUUUU,bddfgggGGGhHkllLmnñnnnÑprrrrRRRsSStttwWýÿÝzzz,ðæÆÐØßø,,Ii¼½?dTI(1(cl",
            transform.dropdiacritics(title, charset="latin1"),
        )


if __name__ == "__main__":
    botsinit.generalinit("config")
    botsglobal.logger = botsinit.initenginelogging("engine")
    botsinit.connect()
    unittest.main()
    botsglobal.db.close()
