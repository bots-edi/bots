# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import os
import sys
import unittest
import shutil
import filecmp
try:
    import json as simplejson
except ImportError:
    import simplejson

import tests.utilsunit
import bots.botslib as botslib
import bots.botsinit as botsinit
import bots.botsglobal as botsglobal
import bots.inmessage as inmessage
import bots.outmessage as outmessage
if sys.version_info[0] > 2:
    basestring = unicode = str

'''
pluging unitinisout.zip
    in bots.ini: max_number_errors = 1
    activate UNITTEST_CORRECTION code
    runs OK in python2.7 (xml behave slightly differnt in 2.6)
    not an acceptance test
'''


class TestInmessage_xml(unittest.TestCase):
    ''' Read messages; some should be OK (True), some should give errors (False).
        Tests per editype.
    '''

    def testxml(self):
        #~ #empty file
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xmlnocheck',
                          messagetype='xmlnocheck', filename='botssys/infile/unitinmessagexml/xml/110401.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxml', filename='botssys/infile/unitinmessagexml/xml/110401.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110401.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxmlflatten', filename='botssys/infile/unitinmessagexml/xml/110401.xml')
        #only root record in 110402.xml
        self.failUnless(inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                                 filename='botssys/infile/unitinmessagexml/xml/110402.xml'), 'only a root tag; should be OK')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxml', filename='botssys/infile/unitinmessagexml/xml/110402.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110402.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxmlflatten', filename='botssys/infile/unitinmessagexml/xml/110402.xml')

        #root tag different from grammar
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxml', filename='botssys/infile/unitinmessagexml/xml/110406.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110406.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxmlflatten', filename='botssys/infile/unitinmessagexml/xml/110406.xml')
        #root tag is double
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xmlnocheck',
                          messagetype='xmlnocheck', filename='botssys/infile/unitinmessagexml/xml/110407.xml')
        #invalid: no closing tag
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xmlnocheck',
                          messagetype='xmlnocheck', filename='botssys/infile/unitinmessagexml/xml/110408.xml')
        #invalid: extra closing tag
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xmlnocheck',
                          messagetype='xmlnocheck', filename='botssys/infile/unitinmessagexml/xml/110409.xml')
        #invalid: mandatory xml-element missing
        self.failUnless(inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                                 filename='botssys/infile/unitinmessagexml/xml/110410.xml'), '')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxml', filename='botssys/infile/unitinmessagexml/xml/110410.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110410.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxmlflatten', filename='botssys/infile/unitinmessagexml/xml/110410.xml')

        #invalid: to many occurences
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxml', filename='botssys/infile/unitinmessagexml/xml/110411.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110411.xml')

        #invalid: missing mandatory xml attribute
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxml', filename='botssys/infile/unitinmessagexml/xml/110412.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110412.xml')

        #unknown xml element
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110413.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110414.xml')

        #2x the same xml attribute
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml',
                          messagetype='testxml', filename='botssys/infile/unitinmessagexml/xml/110415.xml')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='xml', messagetype='testxml',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagexml/xml/110415.xml')

        #messages with all max occurences, use attributes, etc
        in1 = inmessage.parse_edi_file(editype='xml', messagetype='testxml',
                                       filename='botssys/infile/unitinmessagexml/xml/110416.xml')  # all elements, attributes

        #other order of xml elements; should esult in the same node tree
        # as 18., other order of elements
        in1 = inmessage.parse_edi_file(editype='xml', messagetype='testxml',
                                       filename='botssys/infile/unitinmessagexml/xml/110417.xml')
        in2 = inmessage.parse_edi_file(editype='xml', messagetype='testxml',
                                       filename='botssys/infile/unitinmessagexml/xml/110418.xml')
        self.failUnless(utilsunit.comparenode(in2.root, in1.root), 'compare')

        #??what is tested here
        inn7 = inmessage.parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True,
                                        filename='botssys/infile/unitinmessagexml/xml/110405.xml')  # with <?xml version="1.0" encoding="utf-8"?>
        inn8 = inmessage.parse_edi_file(editype='xml', messagetype='testxmlflatten', checkunknownentities=True,
                                        filename='botssys/infile/unitinmessagexml/xml/110405.xml')  # with <?xml version="1.0" encoding="utf-8"?>
        self.failUnless(utilsunit.comparenode(inn7.root, inn8.root), 'compare')

        #~ #test different file which should give equal results
        in1 = inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                       filename='botssys/infile/unitinmessagexml/xml/110403.xml')  # no grammar used
        in5 = inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                       filename='botssys/infile/unitinmessagexml/xml/110404.xml')  # no grammar used
        in6 = inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                       filename='botssys/infile/unitinmessagexml/xml/110405.xml')  # no grammar used
        # with <?xml version="1.0" encoding="utf-8"?>
        in2 = inmessage.parse_edi_file(editype='xml', messagetype='testxml',
                                       filename='botssys/infile/unitinmessagexml/xml/110403.xml')
        # without <?xml version="1.0" encoding="utf-8"?>
        in3 = inmessage.parse_edi_file(editype='xml', messagetype='testxml',
                                       filename='botssys/infile/unitinmessagexml/xml/110404.xml')
        # use cr/lf and whitespace for 'nice' xml
        in4 = inmessage.parse_edi_file(editype='xml', messagetype='testxml',
                                       filename='botssys/infile/unitinmessagexml/xml/110405.xml')
        self.failUnless(utilsunit.comparenode(in2.root, in1.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in3.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in4.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in5.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in6.root), 'compare')

        #~ #test different file which should give equal results; flattenxml=True,
        in1 = inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                       filename='botssys/infile/unitinmessagexml/xml/110403.xml')  # no grammar used
        in5 = inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                       filename='botssys/infile/unitinmessagexml/xml/110404.xml')  # no grammar used
        in6 = inmessage.parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck',
                                       filename='botssys/infile/unitinmessagexml/xml/110405.xml')  # no grammar used
        # use cr/lf and whitespace for 'nice' xml
        in4 = inmessage.parse_edi_file(editype='xml', messagetype='testxmlflatten',
                                       filename='botssys/infile/unitinmessagexml/xml/110405.xml')
        # with <?xml version="1.0" encoding="utf-8"?>
        in2 = inmessage.parse_edi_file(editype='xml', messagetype='testxmlflatten',
                                       filename='botssys/infile/unitinmessagexml/xml/110403.xml')
        # without <?xml version="1.0" encoding="utf-8"?>
        in3 = inmessage.parse_edi_file(editype='xml', messagetype='testxmlflatten',
                                       filename='botssys/infile/unitinmessagexml/xml/110404.xml')
        self.failUnless(utilsunit.comparenode(in2.root, in1.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in3.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in4.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in5.root), 'compare')
        self.failUnless(utilsunit.comparenode(in2.root, in6.root), 'compare')


class Testinisoutxml(unittest.TestCase):

    def testxml01a(self):
        ''' check  xml; new behaviour'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout02.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout01a.xml'
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml02a(self):
        ''' check xmlnoccheck; new behaviour'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout02.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout02tmpa.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout02a.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck',
                            filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml03(self):
        ''' check  xml (different grammar)'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/110419.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout03.xml'
        utilsunit.readwrite(editype='xml', messagetype='testxmlflatten', charset='utf-8',
                            filenamein=filenamein, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenamein, 'bots/' + filenameout))

    def testxml04(self):
        ''' check xmlnoccheck'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/110419.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout04tmp.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout04.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck',
                            charset='utf-8', filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='testxmlflatten', charset='utf-8',
                            filenamein=filenametmp, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenamein, 'bots/' + filenameout))

    def testxml05(self):
        ''' test xml;  iso-8859-1'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout03.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisoutcompare05.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout05.xml'
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenamein,
                            filenameout=filenameout, charset='ISO-8859-1')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml06(self):
        ''' test xmlnocheck; iso-8859-1'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout03.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout05tmp.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisoutcompare05.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout05a.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck',
                            filenamein=filenamein, filenameout=filenametmp, charset='ISO-8859-1')
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenametmp,
                            filenameout=filenameout, charset='ISO-8859-1')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml09(self):
        ''' BOM;; BOM is not written....'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout05.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisout04.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout09.xml'
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenamein,
                            filenameout=filenameout, charset='utf-8')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml10(self):
        ''' BOM;; BOM is not written....'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout05.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout10tmp.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout10.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisout04.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck',
                            filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenametmp,
                            filenameout=filenameout, charset='utf-8')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml11(self):
        ''' check  xml; new behaviour; use standalone parameter'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout06.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout11.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisout02.xml'
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein,
                            filenameout=filenameout, standalone=None)
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml11a(self):
        ''' check  xml; new behaviour; use standalone parameter'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout06.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout11a.xml'
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein,
                            filenameout=filenameout, standalone='no')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml12(self):
        ''' check xmlnoccheck; new behaviour use standalone parameter'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout06.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout12tmp.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout12.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck',
                            filenamein=filenamein, filenameout=filenametmp, standalone='no')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp,
                            filenameout=filenameout, standalone='no')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml13(self):
        ''' check  xml; read doctype&write doctype'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout13.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout13.xml'
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein,
                            filenameout=filenameout, DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml14(self):
        ''' check xmlnoccheck;  read doctype&write doctype'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout13.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout14tmp.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout14.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein,
                            filenameout=filenametmp, DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp,
                            filenameout=filenameout, DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"')
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml15(self):
        ''' check  xml; read processing_instructions&write processing_instructions'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout15.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout15.xml'
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout, processing_instructions=[
                            ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'), ('type-of-ppi', 'attr1="value1" attr2="value2"')])
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml16(self):
        ''' check xmlnoccheck;  read processing_instructions&write processing_instructions'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout15.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout16tmp.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout16.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp, processing_instructions=[
                            ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'), ('type-of-ppi', 'attr1="value1" attr2="value2"')])
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout, processing_instructions=[
                            ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'), ('type-of-ppi', 'attr1="value1" attr2="value2"')])
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testxml17(self):
        ''' check  xml; read processing_instructions&doctype&comments. Do not write these.'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout17.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout17.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisout02.xml'
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml18(self):
        ''' check  xml; read processing_instructions&doctype&comments. Do not write these.'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout17.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout18tmp.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout18.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisout02.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck',
                            filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml19(self):
        ''' check  xml; indented; use lot of options.'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout02.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout19.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisout19.xml'
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout, indented=True, standalone='yes', DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"',
                            processing_instructions=[('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'), ('type-of-ppi', 'attr1="value1" attr2="value2"')])
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))

    def testxml20(self):
        ''' check  xml; indented; use lot of options.'''
        filenamein = 'botssys/infile/unitinmessagexml/xml/inisout02.xml'
        filenametmp = 'botssys/infile/unitinmessagexml/output/inisout20tmp.xml'
        filenameout = 'botssys/infile/unitinmessagexml/output/inisout20.xml'
        filenamecmp = 'botssys/infile/unitinmessagexml/xml/inisout19.xml'
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp, indented=True, standalone='yes',
                            DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"', processing_instructions=[('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'), ('type-of-ppi', 'attr1="value1" attr2="value2"')])
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout, indented=True, standalone='yes', DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"',
                            processing_instructions=[('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'), ('type-of-ppi', 'attr1="value1" attr2="value2"')])
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamecmp))


class InmessageJson(unittest.TestCase):
    #***********************************************************************
    #***********test json eg list of article (as eg used in database comm *******
    #***********************************************************************

    def testjson01(self):
        filein = 'botssys/infile/unitinmessagejson/org/01.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='articles')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjson01nocheck(self):
        filein = 'botssys/infile/unitinmessagejson/org/01.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='articles')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjson11(self):
        filein = 'botssys/infile/unitinmessagejson/org/11.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='articles')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjson11nocheck(self):
        filein = 'botssys/infile/unitinmessagejson/org/11.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='articles')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))
    #***********************************************************************
    #*********json incoming tests complex structure*************************
    #***********************************************************************

    def testjsoninvoic01(self):
        filein = 'botssys/infile/unitinmessagejson/org/invoic01.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjsoninvoic01nocheck(self):
        filein = 'botssys/infile/unitinmessagejson/org/invoic01.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjsoninvoic02(self):
        ''' check  01.xml the same after rad&write/check '''
        filein = 'botssys/infile/unitinmessagejson/org/invoic02.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjsoninvoic02nocheck(self):
        ''' check  01.xml the same after rad&write/check '''
        filein = 'botssys/infile/unitinmessagejson/org/invoic02.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic01.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    #***********************************************************************
    #*********json incoming tests int,float*********************************
    #***********************************************************************
    def testjsoninvoic03(self):
        ''' test int, float in json '''
        filein = 'botssys/infile/unitinmessagejson/org/invoic03.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic02.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjsoninvoic03xmlnocheck(self):
        ''' test int, float in json '''
        filein = 'botssys/infile/unitinmessagejson/org/invoic03.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic02.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xmlnocheck', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjsoninvoic03nocheck(self):
        ''' test int, float in json '''
        filein = 'botssys/infile/unitinmessagejson/org/invoic03.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic02.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjsoninvoic03nocheckxmlnocheck(self):
        ''' test int, float in json '''
        filein = 'botssys/infile/unitinmessagejson/org/invoic03.jsn'
        filecomp = 'botssys/infile/unitinmessagejson/comp/invoic02.xml'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = inmessage.parse_edi_file(filename=filecomp, editype='xmlnocheck', messagetype='invoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testjsondiv(self):
        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                                 checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130101.json'), 'standaard test')
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130101.json'), 'standaard test')

        #~ #empty object
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130102.json')

        #unknown field
        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                                 checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130103.json'), 'unknown field')
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130103.json'), 'unknown field')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130103.json')  # unknown field

        #compare standard test with standard est with extra unknown fields and objects: must give same tree:
        in1 = inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                       checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130101.json')
        in2 = inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                       checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130115.json')
        self.failUnless(utilsunit.comparenode(in1.root, in2.root), 'compare')

        #numeriek field
        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                                 checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130104.json'), 'numeriek field')
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130104.json'), 'numeriek field')
        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                                 checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130104.json'), 'numeriek field')

        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                                 checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130105.json'), 'fucked up')
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130105.json'), 'fucked up')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130105.json')  # fucked up

        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                                 checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130106.json'), 'fucked up')
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130106.json'), 'fucked up')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130106.json')  # fucked up

        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                                 checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130107.json'), 'fucked up')
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130107.json'), 'fucked up')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130107.json')  # fucked up

        #root is list with 3 messagetrees
        inn = inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                       checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130108.json')
        self.assertEqual(len(inn.root.children), 3, 'should deliver 3 messagetrees')
        inn = inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                       filename='botssys/infile/unitinmessagejson/org/130108.json')
        self.assertEqual(len(inn.root.children), 3, 'should deliver 3 messagetrees')

        #root is list, but list has a non-object member
        self.failUnless(inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False,
                                                 filename='botssys/infile/unitinmessagejson/org/130109.json'), 'root is list, but list has a non-object member')
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130109.json'), 'root is list, but list has a non-object member')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01', checkunknownentities=True,
                          filename='botssys/infile/unitinmessagejson/org/130109.json')  # root is list, but list has a non-object member

        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130110.json')  # too many occurences

        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130111.json')  # ent TEST1 should have a TEST2
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130111.json'), 'ent TEST1 should have a TEST2')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130111.json')  # ent TEST1 should have a TEST2

        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130112.json')  # ent TEST1 has a TEST2
        self.failUnless(inmessage.parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck',
                                                 filename='botssys/infile/unitinmessagejson/org/130112.json'), 'ent TEST1 has a TEST2')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=True, filename='botssys/infile/unitinmessagejson/org/130112.json')  # ent TEST1 has a TEST2

        #unknown entries
        inn = inmessage.parse_edi_file(editype='json', messagetype='testjsonorder01',
                                       checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130113.json')

        #empty file
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130114.json')  # empty file
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='jsonnocheck',
                          messagetype='jsonnocheck', filename='botssys/infile/unitinmessagejson/org/130114.json')  # empty file

        #numeric key
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130116.json')

        #key is list
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='json', messagetype='testjsonorder01',
                          checkunknownentities=False, filename='botssys/infile/unitinmessagejson/org/130117.json')

    def testinisoutjson01(self):
        filein = 'botssys/infile/unitinmessagejson/org/inisout01.json'
        fileout1 = 'botssys/infile/unitinmessagejson/output/inisout01.json'
        fileout3 = 'botssys/infile/unitinmessagejson/output/inisout03.json'
        utilsunit.readwrite(editype='json', messagetype='jsonorder', filenamein=filein, filenameout=fileout1)
        utilsunit.readwrite(editype='jsonnocheck', messagetype='jsonnocheck', filenamein=filein, filenameout=fileout3)
        inn1 = inmessage.parse_edi_file(filename=fileout1, editype='jsonnocheck', messagetype='jsonnocheck')
        inn2 = inmessage.parse_edi_file(filename=fileout3, editype='jsonnocheck', messagetype='jsonnocheck')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testinisoutjson02(self):
        #fails. this is because list of messages is read; and these are written in one time....nice for next release...
        filein = 'botssys/infile/unitinmessagejson/org/inisout05.json'
        fileout = 'botssys/infile/unitinmessagejson/output/inisout05.json'
        inn = inmessage.parse_edi_file(editype='json', messagetype='jsoninvoic', filename=filein)
        out = outmessage.outmessage_init(editype='json', messagetype='jsoninvoic',
                                         filename=fileout, divtext='', topartner='')  # make outmessage object
        # inn.root.display()
        out.root = inn.root
        out.writeall()
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck',
                                        messagetype='jsonnocheck', defaultBOTSIDroot='HEA')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='jsonnocheck', messagetype='jsonnocheck')
        # inn1.root.display()
        # inn2.root.display()
        # self.failUnless(utilsunit.comparenode(inn1.root,inn2.root))
        # rawfile1 = utilsunit.readfile(filein)
        # rawfile2 = utilsunit.readfile(fileout)
        # jsonobject1 = simplejson.loads(rawfile1)
        # jsonobject2 = simplejson.loads(rawfile2)
        # self.assertEqual(jsonobject1,jsonobject2,'CmpJson')

    def testinisoutjson03(self):
        ''' non-ascii-char'''
        filein = 'botssys/infile/unitinmessagejson/org/inisout04.json'
        fileout = 'botssys/infile/unitinmessagejson/output/inisout04.json'
        utilsunit.readwrite(editype='json', messagetype='jsonorder', filenamein=filein, filenameout=fileout)
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='jsonnocheck')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='jsonnocheck', messagetype='jsonnocheck')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))

    def testinisoutjson04(self):
        filein = 'botssys/infile/unitinmessagejson/org/inisout05.json'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='jsonnocheck',
                                        messagetype='jsonnocheck', defaultBOTSIDroot='HEA')
        inn2 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='jsoninvoic')
        self.failUnless(utilsunit.comparenode(inn1.root, inn2.root))


class TestInmessage(unittest.TestCase):

    def testEdifact0401(self):
        ''' 0401	Errors in records'''
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0401/040101.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0401/040102.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0401/040103.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0401/040104.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0401/040105.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0401/040106.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0401/040107.edi')

    def testedifact0403(self):
        #~ #test charsets
        #~ self.assertRaises(botslib.MessageError,inmessage.parse_edi_file,editype='edifact',messagetype='edifact',filename='botssys/infile/unitinmessageedifact/0403/040301.edi')   #UNOA-regular OK for UNOA as UNOC
        #~ self.assertRaises(botslib.MessageError,inmessage.parse_edi_file,editype='edifact',messagetype='edifact',filename='botssys/infile/unitinmessageedifact/0403/040302F-generated.edi')    #UNOA-regular  OK for UNOA as UNOC
        in0 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/040303.edi')  # UNOA-regular  also UNOA-strict
        in1 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/040306.edi')  # UNOA regular
        in2 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/T0000000005.edi')  # UNOA regular
        in3 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/T0000000006.edi')  # UNOA regular
        for in1node, in2node, in3node in zip(in1.nextmessage(), in2.nextmessage(), in3.nextmessage()):
            self.failUnless(utilsunit.comparenode(in1node.root, in2node.root), 'compare')
            self.failUnless(utilsunit.comparenode(in1node.root, in3node.root), 'compare')

        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact', messagetype='edifact',
                          filename='botssys/infile/unitinmessageedifact/0403/040305.edi')  # needs UNOA regular
        #~ in1= inmessage.parse_edi_file(editype='edifact',messagetype='edifact',filename='botssys/infile/unitinmessageedifact/0403/040305.edi') #needs UNOA extended; add (and delete later)

        in7 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/040304.edi')  # UNOB-regular
        in5 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/T0000000008.edi')  # UNOB regular
        in4 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/T0000000007-generated.edi')  # UNOB regular

        in6 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0403/T0000000009.edi')  # UNOC

    def testedifact0404(self):
        #envelope tests
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040401.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040402.edi')
        self.failUnless(inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                                 filename='botssys/infile/unitinmessageedifact/0404/040403.edi'), 'standaard test')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040404.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040405.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040406.edi')
        # self.assertRaises(botslib.InMessageError,inmessage.parse_edi_file,editype='edifact',messagetype='edifact',filename='botssys/infile/unitinmessageedifact/0404/040407.edi')
        # #syntax version '0'; is not checked anymore
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040408.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040409.edi')
        self.failUnless(inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                                 filename='botssys/infile/unitinmessageedifact/0404/040410.edi'), 'standaard test')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040411.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040412.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040413.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040414.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040415.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040416.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040417.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0404/040418.edi')

    def testedifact0407(self):
        #lex test with characters in strange places
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0407/040701.edi')
        self.failUnless(inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                                 filename='botssys/infile/unitinmessageedifact/0407/040702.edi'), 'standaard test')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0407/040703.edi')
        self.assertRaises(botslib.MessageError, inmessage.parse_edi_file, editype='edifact',
                          messagetype='edifact', filename='botssys/infile/unitinmessageedifact/0407/040704.edi')
        self.failUnless(inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                                 filename='botssys/infile/unitinmessageedifact/0407/040705.edi'), 'standaard test')
        self.failUnless(inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                                 filename='botssys/infile/unitinmessageedifact/0407/040706.edi'), 'UNOA Crtl-Z at end')
        self.failUnless(inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                                 filename='botssys/infile/unitinmessageedifact/0407/040707.edi'), 'UNOB Crtl-Z at end')
        self.failUnless(inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                                 filename='botssys/infile/unitinmessageedifact/0407/040708.edi'), 'UNOC Crtl-Z at end')

    def testedifact0408(self):
        #differentenvelopingsamecontent: 1rst UNH per UNB, 2nd has 2 UNB for all UNH's, 3rd has UNG-UNE
        in1 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0408/040801.edi')
        in2 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0408/040802.edi')
        in3 = inmessage.parse_edi_file(editype='edifact', messagetype='edifact',
                                       filename='botssys/infile/unitinmessageedifact/0408/040803.edi')
        for in1node, in2node, in3node in zip(in1.nextmessage(), in2.nextmessage(), in3.nextmessage()):
            self.failUnless(utilsunit.comparenode(in1node.root, in2node.root), 'compare')
            self.failUnless(utilsunit.comparenode(in1node.root, in3node.root), 'compare')


class Testinisoutedifact(unittest.TestCase):

    def testedifact02(self):
        infile = 'botssys/infile/unitinisout/org/inisout02.edi'
        outfile = 'botssys/infile/unitinisout/output/inisout02.edi'
        inn = inmessage.parse_edi_file(editype='edifact', messagetype='orderswithenvelope', filename=infile)
        out = outmessage.outmessage_init(editype='edifact', messagetype='orderswithenvelope',
                                         filename=outfile, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        self.failUnless(filecmp.cmp('bots/' + outfile, 'bots/' + infile))

    def testedifact03(self):
        #~ #takes quite long
        infile = 'botssys/infile/unitinisout/org/inisout03.edi'
        outfile = 'botssys/infile/unitinisout/output/inisout03.edi'
        inn = inmessage.parse_edi_file(editype='edifact', messagetype='invoicwithenvelope', filename=infile)
        out = outmessage.outmessage_init(editype='edifact', messagetype='invoicwithenvelope',
                                         filename=outfile, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        self.failUnless(filecmp.cmp('bots/' + outfile, 'bots/' + infile))

    def testedifact04(self):
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040601.edi',
                            filenameout='botssys/infile/unitinisout/output/040601.edi')
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040602.edi',
                            filenameout='botssys/infile/unitinisout/output/040602.edi')
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040603.edi',
                            filenameout='botssys/infile/unitinisout/output/040603.edi')
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040604.edi',
                            filenameout='botssys/infile/unitinisout/output/040604.edi')
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040605.edi',
                            filenameout='botssys/infile/unitinisout/output/040605.edi')
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040606.edi',
                            filenameout='botssys/infile/unitinisout/output/040606.edi')
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040607.edi',
                            filenameout='botssys/infile/unitinisout/output/040607.edi')
        utilsunit.readwrite(editype='edifact',
                            messagetype='orderswithenvelope',
                            filenamein='botssys/infile/unitinisout/0406edifact/040608.edi',
                            filenameout='botssys/infile/unitinisout/output/040608.edi')
        self.failUnless(filecmp.cmp('bots/botssys/infile/unitinisout/output/040601.edi',
                                    'bots/botssys/infile/unitinisout/output/040602.edi'))
        self.failUnless(filecmp.cmp('bots/botssys/infile/unitinisout/output/040601.edi',
                                    'bots/botssys/infile/unitinisout/output/040603.edi'))
        self.failUnless(filecmp.cmp('bots/botssys/infile/unitinisout/output/040601.edi',
                                    'bots/botssys/infile/unitinisout/output/040604.edi'))
        self.failUnless(filecmp.cmp('bots/botssys/infile/unitinisout/output/040601.edi',
                                    'bots/botssys/infile/unitinisout/output/040605.edi'))
        self.failUnless(filecmp.cmp('bots/botssys/infile/unitinisout/output/040601.edi',
                                    'bots/botssys/infile/unitinisout/output/040606.edi'))
        self.failUnless(filecmp.cmp('bots/botssys/infile/unitinisout/output/040601.edi',
                                    'bots/botssys/infile/unitinisout/output/040607.edi'))
        self.failUnless(filecmp.cmp('bots/botssys/infile/unitinisout/output/040601.edi',
                                    'bots/botssys/infile/unitinisout/output/040608.edi'))


class Testinisoutinh(unittest.TestCase):

    def testinh01(self):
        filenamein = 'botssys/infile/unitinisout/org/inisout01.inh'
        filenameout = 'botssys/infile/unitinisout/output/inisout01.inh'
        inn = inmessage.parse_edi_file(editype='fixed', messagetype='invoicfixed', filename=filenamein)
        out = outmessage.outmessage_init(editype='fixed', messagetype='invoicfixed',
                                         filename=filenameout, divtext='', topartner='KCS0004')  # make outmessage object
        out.root = inn.root
        out.writeall()
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testidoc01(self):
        filenamein = 'botssys/infile/unitinisout/org/inisout01.idoc'
        filenameout = 'botssys/infile/unitinisout/output/inisout01.idoc'
        inn = inmessage.parse_edi_file(editype='idoc', messagetype='WP_PLU02', filename=filenamein)
        out = outmessage.outmessage_init(editype='idoc', messagetype='WP_PLU02',
                                         filename=filenameout, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))


class Testinisoutx12(unittest.TestCase):

    def testx12_01(self):
        filenamein = 'botssys/infile/unitinisout/org/inisout01.x12'
        filenameout = 'botssys/infile/unitinisout/output/inisout01.x12'
        inn = inmessage.parse_edi_file(editype='x12', messagetype='850withenvelope', filename=filenamein)
        self.assertEqual(inn.ta_info['frompartner'], '11111111111', 'ISA partner without spaces')
        self.assertEqual(inn.ta_info['topartner'], '22222222222', 'ISA partner without spaces')
        out = outmessage.outmessage_init(editype='x12', messagetype='850withenvelope',
                                         filename=filenameout, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        linesfile1 = utilsunit.readfilelines('bots/' + filenamein)
        linesfile2 = utilsunit.readfilelines('bots/' + filenameout)
        self.assertEqual(linesfile1[0][:103], linesfile2[0][:103], 'first part of ISA')
        for line1, line2 in zip(linesfile1[1:], linesfile2[1:]):
            self.assertEqual(line1, line2, 'Cmplines')

    def testx12_02(self):
        filenamein = 'botssys/infile/unitinisout/org/inisout02.x12'
        filenameout = 'botssys/infile/unitinisout/output/inisout02.x12'
        inn = inmessage.parse_edi_file(editype='x12', messagetype='850withenvelope', filename=filenamein)
        out = outmessage.outmessage_init(add_crlfafterrecord_sep='', editype='x12', messagetype='850withenvelope',
                                         filename=filenameout, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        linesfile1 = utilsunit.readfile('bots/' + filenamein)
        linesfile2 = utilsunit.readfile('bots/' + filenameout)
        self.assertEqual(linesfile1[:103], linesfile2[:103], 'first part of ISA')
        self.assertEqual(linesfile1[105:], linesfile2[103:], 'rest of message')


class Testinisoutcsv(unittest.TestCase):

    def testcsv001(self):
        filenamein = 'botssys/infile/unitinisout/org/inisout01.csv'
        filenameout = 'botssys/infile/unitinisout/output/inisout01.csv'
        utilsunit.readwrite(editype='csv', messagetype='invoic', filenamein=filenamein, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))

    def testcsv003(self):
        #utf-charset
        filenamein = 'botssys/infile/unitinisout/org/inisout03.csv'
        filenameout = 'botssys/infile/unitinisout/output/inisout03.csv'
        utilsunit.readwrite(editype='csv', messagetype='invoic', filenamein=filenamein, filenameout=filenameout)
        self.failUnless(filecmp.cmp('bots/' + filenameout, 'bots/' + filenamein))
        #~ #utf-charset with BOM **error. BOM is not removed by python.
        #~ #utilsunit.readwrite(editype='csv',
        #~ #            messagetype='invoic',
        #~ #            filenamein='botssys/infile/unitinisout/inisout04.csv',
        #~ #            filenameout='botssys/infile/unitinisout/output/inisout04.csv')
        #~ #self.failUnless(filecmp.cmp('botssys/infile/unitinisout/output/inisout04.csv','botssys/infile/unitinisout/inisout04.csv'))


if __name__ == '__main__':
    botsinit.generalinit('config')
    botsglobal.logger = botsinit.initenginelogging('engine')
    shutil.rmtree('bots/botssys/infile/unitinisout/output', ignore_errors=True)  # remove whole output directory
    os.mkdir('bots/botssys/infile/unitinisout/output')
    shutil.rmtree('bots/botssys/infile/unitinmessagejson/output/', ignore_errors=True)  # remove whole output directory
    os.mkdir('bots/botssys/infile/unitinmessagejson/output')
    shutil.rmtree('bots/botssys/infile/unitinmessagexml/output', ignore_errors=True)  # remove whole output directory
    os.mkdir('bots/botssys/infile/unitinmessagexml/output')
    unittest.main()
