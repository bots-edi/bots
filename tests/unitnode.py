# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import os
import sys
import unittest
import shutil
import bots.inmessage as inmessage
import bots.outmessage as outmessage
import bots.botslib as botslib
import bots.node as node
import bots.botsinit as botsinit
import bots.botsglobal as botsglobal

if sys.version_info[0] > 2:
    basestring = unicode = str

"""plugin unitnode.zip
not an acceptance tst
does not work with get_checklevel=2
"""

# fetchqueries is dynamically added to node, to retrieve and check
collectqueries = {}


def fetchqueries(self, level=0):
    """for debugging
        usage: in mapping script:     inn.root.displayqueries()
    """
    if self.record:
        tmp = self.queries
        if tmp:
            collectqueries[self.record["BOTSID"]] = tmp
    for childnode in self.children:
        childnode.fetchqueries(level + 1)


class Testnode(unittest.TestCase):
    """ test node.py and message.py.
    """

    def testedifact01(self):
        inn = inmessage.parse_edi_file(
            editype="edifact",
            messagetype="invoicwithenvelope",
            filename="botssys/infile/unitnode/nodetest01.edi",
        )
        out = outmessage.outmessage_init(
            editype="edifact",
            messagetype="invoicwithenvelope",
            filename="botssys/infile/unitnode/output/inisout03.edi",
            divtext="",
            topartner="",
        )  # make outmessage object
        out.root = inn.root

        # * getloop **************************************
        count = 0
        for t in inn.getloop({"BOTSID": "XXX"}):
            count += 1
        self.assertEqual(count, 0, "Cmplines")

        count = 0
        for t in inn.getloop({"BOTSID": "UNB"}):
            count += 1
        self.assertEqual(count, 2, "Cmplines")

        count = 0
        for t in out.getloop({"BOTSID": "UNB"}, {"BOTSID": "XXX"}):
            count += 1
        self.assertEqual(count, 0, "Cmplines")

        count = 0
        for t in out.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}):
            count += 1
        self.assertEqual(count, 3, "Cmplines")

        count = 0
        for t in inn.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}, {"BOTSID": "XXX"}):
            count += 1
        self.assertEqual(count, 0, "Cmplines")

        count = 0
        for t in inn.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}, {"BOTSID": "LIN"}):
            count += 1
        self.assertEqual(count, 6, "Cmplines")

        count = 0
        for t in inn.getloop(
            {"BOTSID": "UNB"}, {"BOTSID": "XXX"}, {"BOTSID": "LIN"}, {"BOTSID": "QTY"}
        ):
            count += 1
        self.assertEqual(count, 0, "Cmplines")

        count = 0
        for t in inn.getloop(
            {"BOTSID": "UNB"}, {"BOTSID": "UNH"}, {"BOTSID": "LIN"}, {"BOTSID": "XXX"}
        ):
            count += 1
        self.assertEqual(count, 0, "Cmplines")

        count = 0
        for t in inn.getloop(
            {"BOTSID": "UNB"}, {"BOTSID": "UNH"}, {"BOTSID": "LIN"}, {"BOTSID": "QTY"}
        ):
            count += 1
        self.assertEqual(count, 6, "Cmplines")

        # * getcount, getcountmpath **************************************
        count = 0
        countlist = [5, 0, 1]
        nrsegmentslist = [132, 10, 12]
        for t in out.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}):
            count2 = 0
            for u in t.getloop({"BOTSID": "UNH"}, {"BOTSID": "LIN"}):
                count2 += 1
            count3 = t.getcountoccurrences({"BOTSID": "UNH"}, {"BOTSID": "LIN"})
            self.assertEqual(t.getcount(), nrsegmentslist[count], "Cmplines")
            self.assertEqual(count2, countlist[count], "Cmplines")
            self.assertEqual(count3, countlist[count], "Cmplines")
            count += 1
        self.assertEqual(
            out.getcountoccurrences({"BOTSID": "UNB"}, {"BOTSID": "UNH"}),
            count,
            "Cmplines",
        )
        self.assertEqual(
            inn.getcountoccurrences({"BOTSID": "UNB"}, {"BOTSID": "UNH"}),
            count,
            "Cmplines",
        )
        self.assertEqual(inn.getcount(), sum(nrsegmentslist, 4), "Cmplines")
        self.assertEqual(out.getcount(), sum(nrsegmentslist, 4), "Cmplines")

        # * get, getnozero, countmpath, sort**************************************
        for t in out.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}):
            self.assertRaises(botslib.MappingRootError, out.get, ())
            self.assertRaises(botslib.MappingRootError, out.getnozero, ())
            self.assertRaises(botslib.MappingRootError, out.get, 0)
            self.assertRaises(botslib.MappingRootError, out.getnozero, 0)
            t.sort({"BOTSID": "UNH"}, {"BOTSID": "LIN", "C212.7140": None})
            start = "0"
            for u in t.getloop({"BOTSID": "UNH"}, {"BOTSID": "LIN"}):
                nextstart = u.get({"BOTSID": "LIN", "C212.7140": None})
                self.failUnless(start < nextstart)
                start = nextstart
            t.sort({"BOTSID": "UNH"}, {"BOTSID": "LIN", "1082": None})
            start = "0"
            for u in t.getloop({"BOTSID": "UNH"}, {"BOTSID": "LIN"}):
                nextstart = u.get({"BOTSID": "LIN", "1082": None})
                self.failUnless(start < nextstart)
                start = nextstart

        self.assertRaises(botslib.MappingRootError, out.get, ())
        self.assertRaises(botslib.MappingRootError, out.getnozero, ())
        # ~ # self.assertRaises(botslib.MpathError,out.get,())

        first = True
        for t in out.getloop({"BOTSID": "UNB"}):
            if first:
                self.assertEqual(
                    "15",
                    t.getcountsum(
                        {"BOTSID": "UNB"},
                        {"BOTSID": "UNH"},
                        {"BOTSID": "LIN", "1082": None},
                    ),
                    "Cmplines",
                )
                self.assertEqual(
                    "8",
                    t.getcountsum(
                        {"BOTSID": "UNB"},
                        {"BOTSID": "UNH"},
                        {"BOTSID": "LIN"},
                        {"BOTSID": "QTY", "C186.6063": "47", "C186.6060": None},
                    ),
                    "Cmplines",
                )
                self.assertEqual(
                    "0",
                    t.getcountsum(
                        {"BOTSID": "UNB"},
                        {"BOTSID": "UNH"},
                        {"BOTSID": "LIN"},
                        {"BOTSID": "QTY", "C186.6063": "12", "C186.6060": None},
                    ),
                    "Cmplines",
                )
                self.assertEqual(
                    "54.4",
                    t.getcountsum(
                        {"BOTSID": "UNB"},
                        {"BOTSID": "UNH"},
                        {"BOTSID": "LIN"},
                        {"BOTSID": "MOA", "C516.5025": "203", "C516.5004": None},
                    ),
                    "Cmplines",
                )
                first = False
            else:
                self.assertEqual(
                    "1",
                    t.getcountsum(
                        {"BOTSID": "UNB"},
                        {"BOTSID": "UNH"},
                        {"BOTSID": "LIN"},
                        {"BOTSID": "QTY", "C186.6063": "47", "C186.6060": None},
                    ),
                    "Cmplines",
                )
                self.assertEqual(
                    "0",
                    t.getcountsum(
                        {"BOTSID": "UNB"},
                        {"BOTSID": "UNH"},
                        {"BOTSID": "LIN"},
                        {"BOTSID": "QTY", "C186.6063": "12", "C186.6060": None},
                    ),
                    "Cmplines",
                )
                self.assertEqual(
                    "0",
                    t.getcountsum(
                        {"BOTSID": "UNB"},
                        {"BOTSID": "UNH"},
                        {"BOTSID": "LIN"},
                        {"BOTSID": "MOA", "C516.5025": "203", "C516.5004": None},
                    ),
                    "Cmplines",
                )

    # ~ def testedifact02(self):
    # display query correct? incluuding propagating 'down the tree'?
    # ~ inn = inmessage.parse_edi_file(editype='edifact',messagetype='invoicwithenvelopetestquery',filename='botssys/infile/unitnode/nodetest01.edi')
    # ~ inn.root.processqueries({},2)
    # ~ inn.root.displayqueries()

    def testedifact03(self):
        # ~ #display query correct? incluuding propagating 'down the tree'?
        node.Node.fetchqueries = fetchqueries
        inn = inmessage.parse_edi_file(
            editype="edifact",
            messagetype="edifact",
            filename="botssys/infile/unitnode/0T0000000015.edi",
        )
        inn.root.processqueries({}, 2)
        inn.root.fetchqueries()
        # ~ print collectqueries
        comparequeries = {
            "UNH": {
                "reference": "UNHREF",
                "messagetype": "ORDERSD96AUNEAN008",
                "reference2": "UNBREF",
                "topartner": "PARTNER2",
                "alt": "50EAB",
                "alt2": "50E9",
                "frompartner": "PARTNER1",
            },
            "UNB": {
                "topartner": "PARTNER2",
                "reference2": "UNBREF",
                "reference": "UNBREF",
                "frompartner": "PARTNER1",
            },
            "UNZ": {
                "reference": "UNBREF",
                "reference2": "UNBREF",
                "topartner": "PARTNER2",
                "frompartner": "PARTNER1",
            },
        }
        self.assertEqual(comparequeries, collectqueries)
        # ~ inn.root.displayqueries()


if __name__ == "__main__":
    botsinit.generalinit("config")
    botsglobal.logger = botsinit.initenginelogging("engine")
    shutil.rmtree(
        "bots/botssys/infile/unitnode/output", ignore_errors=True
    )  # remove whole output directory
    os.mkdir("bots/botssys/infile/unitnode/output")
    unittest.main()
    unittest.main()
    unittest.main()
