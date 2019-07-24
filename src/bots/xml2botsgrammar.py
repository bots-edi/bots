# -*- coding: utf-8 -*-

"""Converts xml file to a bots grammar.
   Usage: c:\python27\python  bots-xml2botsgrammar.py  botssys/infile/test.xml botssys/infile/resultgrammar.py  -cconfig
   Try to have a 'completely filled' xml file.
"""
from __future__ import print_function
from __future__ import unicode_literals

import atexit
import copy
import click
import logging
import os
import sys

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from collections import OrderedDict

from . import botslib
from . import botsinit
from . import botsglobal
from . import inmessage
from . import outmessage
from . import node
from .botsconfig import ID, LEVEL, MAX, MIN


# classes used in inmessage for xml2botsgrammar.
# These classes are dynamically added to inmessage


class xmlforgrammar(inmessage.Inmessage):
    """class for ediobjects in XML. Uses ElementTree"""

    def initfromfile(self):
        filename = botslib.abspathdata(self.ta_info["filename"])
        self.ta_info["attributemarker"] = "__"
        parser = ET.XMLParser()
        # ElementTree: lexes, parses, makes etree; etree is quite similar
        # to bots-node trees but conversion is needed
        etree = ET.ElementTree()
        etreeroot = etree.parse(filename, parser)
        self.root = self._etree2botstree(etreeroot)  # convert etree to bots-nodes-tree

    def _use_botscontent(self, xmlnode):
        if self._is_record(xmlnode):
            if xmlnode.text is None:
                return False
            else:
                return not xmlnode.text.isspace()
        else:
            return True

    def _etree2botstree(self, xmlnode):
        newnode = node.Node(record=self._etreenode2botstreenode(xmlnode))
        for xmlchildnode in xmlnode:  # for every node in mpathtree
            if self._is_record(xmlchildnode):
                newnode.append(
                    self._etree2botstree(xmlchildnode)
                )  # add as a node/record
            else:
                # remark for generating grammars: empty strings should generate a field here
                if self._use_botscontent(xmlchildnode):
                    newnode.record[xmlchildnode.tag] = "1"  # add as a field
                # convert the xml-attributes of this 'xml-field' to fields in dict with attributemarker.
                newnode.record.update(
                    (xmlchildnode.tag + self.ta_info["attributemarker"] + key, value)
                    for key, value in xmlchildnode.items()
                )
        return newnode

    def _etreenode2botstreenode(self, xmlnode):
        """Build a OrderedDict from xml-node.
        Add BOTSID, xml-attributes (of 'record'), xmlnode.text as BOTSCONTENT."""
        build = OrderedDict(
            (xmlnode.tag + self.ta_info["attributemarker"] + key, value)
            for key, value in xmlnode.items()
        )  # convert xml attributes to fields.
        build["BOTSID"] = xmlnode.tag
        if self._use_botscontent(xmlnode):
            build["BOTSCONTENT"] = "1"
        return build

    def _is_record(self, xmlchildnode):
        return bool(len(xmlchildnode))


class xmlforgrammar_allrecords(inmessage.Inmessage):
    """Class for ediobjects in XML. Uses ElementTree"""

    def initfromfile(self):
        filename = botslib.abspathdata(self.ta_info["filename"])
        self.ta_info["attributemarker"] = "__"
        parser = ET.XMLParser()
        # ElementTree: lexes, parses, makes etree; etree is quite similar to bots-node trees but conversion is needed
        etree = ET.ElementTree()
        etreeroot = etree.parse(filename, parser)
        self.root = self._etree2botstree(etreeroot)  # convert etree to bots-nodes-tree

    def _etree2botstree(self, xmlnode):
        newnode = node.Node(record=self._etreenode2botstreenode(xmlnode))
        for xmlchildnode in xmlnode:  # for every node in mpathtree
            newnode.append(self._etree2botstree(xmlchildnode))  # add as a node/record
        return newnode

    def _etreenode2botstreenode(self, xmlnode):
        """ build a OrderedDict from xml-node. Add BOTSID, xml-attributes (of 'record'), xmlnode.text as BOTSCONTENT."""
        build = OrderedDict(
            (xmlnode.tag + self.ta_info["attributemarker"] + key, value)
            for key, value in xmlnode.items()
        )  # convert xml attributes to fields.
        build["BOTSID"] = xmlnode.tag
        if not self._is_record(xmlnode):
            build["BOTSCONTENT"] = "1"
        return build

    def _is_record(self, xmlchildnode):
        return bool(len(xmlchildnode))


# functions for mapping


def map_treewalker(node_instance, mpath):
    """ Generator function.
    """
    mpath.append(OrderedDict({"BOTSID": node_instance.record["BOTSID"]}))
    for childnode in node_instance.children:
        yield childnode, mpath[:]
        for terugnode, terugmpath in map_treewalker(childnode, mpath):
            yield terugnode, terugmpath
    mpath.pop()


def map_writefields(node_out, node_in, mpath):
    """ als fields of this level are written to node_out.
    """
    mpath_with_all_fields = copy.deepcopy(
        mpath
    )  # use a copy of mpath (do not want to change it)
    for key in node_in.record.keys():
        if key in ["BOTSID", "BOTSIDnr"]:  # skip these
            continue
        mpath_with_all_fields[-1][key] = "dummy"  # add key to the mpath
    node_out.put(*mpath_with_all_fields)  # write all fields.


# functions to convert out-tree to grammar


def tree2grammar(node_instance, structure, recorddefs):
    structure.append(
        {ID: node_instance.record["BOTSID"], MIN: 0, MAX: 99999, LEVEL: []}
    )
    recordlist = []
    for key in node_instance.record.keys():
        recordlist.append([key, "C", 256, "AN"])
    if node_instance.record["BOTSID"] in recorddefs:
        recorddefs[node_instance.record["BOTSID"]] = removedoublesfromlist(
            recorddefs[node_instance.record["BOTSID"]] + recordlist
        )
    else:
        recorddefs[node_instance.record["BOTSID"]] = recordlist
    for childnode in node_instance.children:
        tree2grammar(childnode, structure[-1][LEVEL], recorddefs)


def removedoublesfromlist(orglist):
    list2return = []
    for member in orglist:
        if member not in list2return:
            list2return.append(member)
    return list2return


# functions to write grammar to file***


def recorddefs2string(recorddefs, targetNamespace):
    result = ""
    for tag in sorted(recorddefs):
        result += "'%s%s':\n    [\n" % (targetNamespace, tag)
        for field in recorddefs[tag]:
            if field[0] in ["BOTSID", "BOTSCONTENT"]:
                field[1] = "M"
                result += "    ['%s', '%s', %s, '%s'],\n" % (
                    field[0],
                    field[1],
                    field[2],
                    field[3],
                )
        for field in recorddefs[tag]:
            if field[0].startswith(tag + "__"):
                result += "    ['%s', '%s', %s, '%s'],\n" % (
                    field[0],
                    field[1],
                    field[2],
                    field[3],
                )
        for field in recorddefs[tag]:
            if field[0] not in ["BOTSID", "BOTSIDnr", "BOTSCONTENT"] and not field[
                0
            ].startswith(tag + "__"):
                result += "    ['%s%s', '%s', %s, '%s'],\n" % (
                    targetNamespace,
                    field[0],
                    field[1],
                    field[2],
                    field[3],
                )
        result += "    ],\n"
    return result


def structure2string(structure, targetNamespace, level=0):
    result = ""
    for segment in structure:
        if LEVEL in segment and segment[LEVEL]:
            result += level * "    " + "{ID:'%s%s',MIN:%s,MAX:%s,LEVEL:[\n" % (
                targetNamespace,
                segment[ID],
                segment[MIN],
                segment[MAX],
            )
            result += structure2string(segment[LEVEL], targetNamespace, level + 1)
            result += level * "    " + "]},\n"
        else:
            result += level * "    " + "{ID:'%s%s',MIN:%s,MAX:%s},\n" % (
                targetNamespace,
                segment[ID],
                segment[MIN],
                segment[MAX],
            )
    return result


def grammar2file(botsgrammarfilename, structure, recorddefs, targetNamespace):
    if targetNamespace:
        targetNamespace = "{" + targetNamespace + "}"
    result = "structure = [\n"
    result += structure2string(structure, targetNamespace)
    result += "]\n\n"
    result += "recorddefs = {\n"
    result += recorddefs2string(recorddefs, targetNamespace)
    result += "}\n"

    result2 = "#Generated by bots open source edi translator.\nfrom bots.botsconfig import *\n"
    if targetNamespace:
        shortNamespace = "NS"
        result2 += shortNamespace + " = '" + targetNamespace + "'\n\n"
        result = result.replace("'" + targetNamespace, shortNamespace + "+'")
    result2 += result

    f = open(botsgrammarfilename, "wb")
    f.write(result2)
    f.close()
    print("grammar file is written:", botsgrammarfilename)


@click.command()
@click.option("--configdir", "-c", default="config", help="path to config-directory.")
@click.option(
    "--allrecords",
    "-a",
    is_flag=False,
    default=False,
    help="all xml elements as records.",
)
@click.option("--edifile", "-e", required=True, help="name of the xml file to read.")
@click.option(
    "--botsgrammarfilename",
    "-b",
    required=True,
    help="name of the grammar file to write.",
)
def start(configdir):
    """Creates a grammar from an xml file.
    """
    botsinit.generalinit(
        configdir
    )  # find locating of bots, configfiles, init paths etc.
    process_name = "xml2botsgrammar"
    botsglobal.logger = botsinit.initenginelogging(process_name)
    atexit.register(logging.shutdown)

    targetNamespace = ""

    # add classes for handling editype xml to inmessage
    if allrecords:
        #  editype = 'xmlforgrammar_allrecords'
        inmessage.xmlforgrammar = xmlforgrammar_allrecords
    else:
        #  editype = 'xmlforgrammar'
        inmessage.xmlforgrammar = xmlforgrammar
    # make inmessage object: read the xml file
    inn = inmessage.parse_edi_file(
        editype="xmlforgrammar", messagetype="", filename=edifile
    )
    inn.checkforerrorlist()  # no exception if infile has been lexed and parsed OK else raises an error
    # make outmessage object; nothing is 'filled' yet. In mapping tree is filled; nothing is written to file.
    out = outmessage.outmessage_init(
        editype="xmlnocheck", messagetype="", filename="", divtext="", topartner=""
    )

    # mapping: make 'normalised' out-tree suited for writing as a grammar***
    mpath_root = [
        OrderedDict({"BOTSID": inn.root.record["BOTSID"], "BOTSIDnr": "1"})
    ]  # handle root
    out.put(*mpath_root)
    map_writefields(out, inn.root, mpath_root)

    # walk tree; write results to out-tree
    mpath_start = []
    for node_instance, mpath in map_treewalker(inn.root, mpath_start):
        mpath.append(OrderedDict({"BOTSID": node_instance.record["BOTSID"]}))
        if out.get(*mpath) is None:  # if node does not exist: write it.
            out.put(*mpath)
        map_writefields(out, node_instance, mpath)
    # mapping is done

    # convert out-tree to grammar
    structure = []
    recorddefs = {}
    tree2grammar(out.root, structure, recorddefs)

    # write grammar to file
    grammar2file(botsgrammarfilename, structure, recorddefs, targetNamespace)


if __name__ == "__main__":
    start()
