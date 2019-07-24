# -*- coding: utf-8 -*-

from __future__ import print_function

# ~ from __future__ import unicode_literals  #python2: gives problems; this module contains unicode strings; in function ccode ascii strings are needed (for field).
import sys
import unittest
import utilsunit
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


class TestTranslate(unittest.TestCase):
    def setUp(self):
        pass

    def testcodeconversion(self):
        # codeconversion via tabel ccode OLD functionnames:
        self.assertEqual(
            "TESTOUT", transform.codetconversion("artikel", "TESTIN"), "basis"
        )
        self.assertEqual(
            "TESTOUT", transform.safecodetconversion("artikel", "TESTIN"), "basis"
        )
        self.assertEqual(
            "TESTINNOT", transform.safecodetconversion("artikel", "TESTINNOT"), "basis"
        )
        self.assertRaises(
            botslib.CodeConversionError,
            transform.codetconversion,
            "artikel",
            "TESTINNOT",
        )
        self.assertEqual(
            "TESTIN", transform.rcodetconversion("artikel", "TESTOUT"), "basis"
        )
        self.assertEqual(
            "TESTIN", transform.safercodetconversion("artikel", "TESTOUT"), "basis"
        )
        self.assertEqual(
            "TESTINNOT", transform.safercodetconversion("artikel", "TESTINNOT"), "basis"
        )
        self.assertRaises(
            botslib.CodeConversionError,
            transform.rcodetconversion,
            "artikel",
            "TESTINNOT",
        )
        # attributes
        self.assertEqual(
            "TESTATTR1",
            transform.codetconversion("artikel", "TESTIN", "attr1"),
            "basis",
        )
        self.assertEqual(
            "TESTATTR1",
            transform.safecodetconversion("artikel", "TESTIN", "attr1"),
            "basis",
        )

        # codeconversion via tabel ccode:
        self.assertEqual("TESTOUT", transform.ccode("artikel", "TESTIN"), "basis")
        self.assertEqual("TESTOUT", transform.safe_ccode("artikel", "TESTIN"), "basis")
        self.assertEqual(
            "TESTINNOT", transform.safe_ccode("artikel", "TESTINNOT"), "basis"
        )
        self.assertRaises(
            botslib.CodeConversionError, transform.ccode, "artikel", "TESTINNOT"
        )
        self.assertEqual(
            "TESTIN", transform.reverse_ccode("artikel", "TESTOUT"), "basis"
        )
        self.assertEqual(
            "TESTIN", transform.safe_reverse_ccode("artikel", "TESTOUT"), "basis"
        )
        self.assertEqual(
            "TESTINNOT", transform.safe_reverse_ccode("artikel", "TESTINNOT"), "basis"
        )
        self.assertRaises(
            botslib.CodeConversionError, transform.reverse_ccode, "artikel", "TESTINNOT"
        )
        # attributes
        self.assertEqual(
            "TESTATTR1", transform.ccode("artikel", "TESTIN", "attr1"), "basis"
        )
        self.assertEqual(
            "TESTATTR1", transform.safe_ccode("artikel", "TESTIN", "attr1"), "basis"
        )


if __name__ == "__main__":
    botsinit.generalinit("config")
    botsglobal.logger = botsinit.initenginelogging("engine")
    botsinit.connect()
    unittest.main()
    botsglobal.db.close()
