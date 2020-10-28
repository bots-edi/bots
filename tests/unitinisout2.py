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

from tests import utilsunit
import bots.botslib as botslib
import bots.botsinit as botsinit
import bots.botsglobal as botsglobal
import bots.inmessage as inmessage
import bots.outmessage as outmessage
import pprint
from avro.datafile import DataFileReader
from avro.io import DatumReader
import copy


if sys.version_info[0] > 2:
    basestring = unicode = str

class OutmessageAvro(unittest.TestCase):
    #***********************************************************************
    #***********compare avro to json *******
    #***********************************************************************

    def testcompareavrowithjson(self):
        filein = 'botssys/infile/json/example.json'
        fileout = 'botssys/outfile/avro/example.avro'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='example')
        out = outmessage.outmessage_init(editype='avro', messagetype='example', filename=fileout, divtext='', topartner='')  # make outmessage object
        out.root = copy.deepcopy(inn1.root)
        out.writeall()
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='example')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    # Avro primitive types: null, boolean, int, long, float, double, bytes, and string
    def testcompareavrowithjsonprimitive(self):
        filein = 'botssys/infile/json/example2.json'
        fileout = 'botssys/outfile/avro/example2.avro'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='example2')
        out = outmessage.outmessage_init(editype='avro', messagetype='example2', filename=fileout, divtext='', topartner='')  # make outmessage object
        out.root = copy.deepcopy(inn1.root)
        out.writeall()
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='example2')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    # Avro logical types: uuid
    def testcompareavrowithjsonlogical(self):
        filein = 'botssys/infile/json/example3.json'
        fileout = 'botssys/outfile/avro/example3.avro'
        inn1 = inmessage.parse_edi_file(filename=filein, editype='json', messagetype='example3')
        out = outmessage.outmessage_init(editype='avro', messagetype='example3', filename=fileout, divtext='', topartner='')  # make outmessage object
        out.root = copy.deepcopy(inn1.root)
        out.writeall()
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='example3')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    #***********************************************************************
    #***********compare avro to avro *******
    #***********************************************************************

    def testsymmetricalreadwrite(self):
        filein = 'botssys/infile/avro/example.avro'
        fileout = 'botssys/outfile/avro/example.avro'
        utilsunit.readwrite(editype='avro', messagetype='example', filenamein=filein, filenameout=fileout)
        inn1 = inmessage.parse_edi_file(filename=filein, editype='avro', messagetype='example')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='example')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    def testcompareavrowithavrounion(self):
        filein = 'botssys/infile/avro/union.avro'
        fileout = 'botssys/outfile/avro/union.avro'
        utilsunit.readwrite(editype='avro', messagetype='union', filenamein=filein, filenameout=fileout)
        inn1 = inmessage.parse_edi_file(filename=filein, editype='avro', messagetype='union')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='union')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    def testcompareavrowithavroarray(self):
        filein = 'botssys/infile/avro/array.avro'
        fileout = 'botssys/outfile/avro/array.avro'
        utilsunit.readwrite(editype='avro', messagetype='array', filenamein=filein, filenameout=fileout)
        inn1 = inmessage.parse_edi_file(filename=filein, editype='avro', messagetype='array')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='array')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    def testcompareavrowithavromap(self):
        filein = 'botssys/infile/avro/map.avro'
        fileout = 'botssys/outfile/avro/map.avro'
        utilsunit.readwrite(editype='avro', messagetype='map', filenamein=filein, filenameout=fileout)
        inn1 = inmessage.parse_edi_file(filename=filein, editype='avro', messagetype='map')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='map')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    def testcompareavrowithavroenum(self):
        filein = 'botssys/infile/avro/enum.avro'
        fileout = 'botssys/outfile/avro/enum.avro'
        utilsunit.readwrite(editype='avro', messagetype='enum', filenamein=filein, filenameout=fileout)
        inn1 = inmessage.parse_edi_file(filename=filein, editype='avro', messagetype='enum')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='enum')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))

    def testcompareavrowithavronoheader(self):
        filein = 'botssys/infile/avro/noheader.avro'
        fileout = 'botssys/outfile/avro/noheader.avro'
        utilsunit.readwrite(editype='avro', messagetype='noheader', filenamein=filein, filenameout=fileout)
        inn1 = inmessage.parse_edi_file(filename=filein, editype='avro', messagetype='noheader')
        inn2 = inmessage.parse_edi_file(filename=fileout, editype='avro', messagetype='noheader')
        self.assertTrue(utilsunit.comparenode(inn1.root, inn2.root))


def setup_module(module):
    botsinit.generalinit('config')
    botsglobal.logger = botsinit.initenginelogging('engine')
    shutil.rmtree('bots/botssys/outfile/', ignore_errors=True)  # remove whole output directory
    os.mkdir('bots/botssys/outfile')
