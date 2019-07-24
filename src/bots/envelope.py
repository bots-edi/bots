# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys

if sys.version_info[0] > 2:
    basestring = unicode = str
import os
import shutil
from django.utils.translation import ugettext as _

# bots-modules
from . import botslib
from . import botsglobal
from . import outmessage
from .botsconfig import *


def mergemessages(startstatus, endstatus, idroute, rootidta=None):
    """ Merges and/or envelopes one or more messages to one file (status TRANSLATED---->MERGED).
        Attribute 'merge' indicates message should be merged with similar messages (or not).
        If merge is False: 1 message per envelope - no merging
        'merge' comes from db-ta; added in translation via from syntax of outgoing message (envelope, message, partner).
        Merge/not merge is implemented as separate loops: one for merge&envelope, another for enveloping only
    """
    if rootidta is None:
        rootidta = botsglobal.currentrun.get_minta4query()
    # **********for messages only to envelope (no merging)
    # editype,messagetype: needed to get right envelope
    # envelope: envelope to use
    # frompartner,topartner,testindicator,charset,nrmessages: needed for envelope (edifact, x12)
    # idta: ID of the db-ta
    # filename: file to envelope
    for row in botslib.query(
        """SELECT editype,messagetype,envelope,frompartner,topartner,testindicator,charset,nrmessages,idta,filename
                                FROM ta
                                WHERE idta>%(rootidta)s
                                AND status=%(status)s
                                AND statust=%(statust)s
                                AND merge=%(merge)s
                                AND idroute=%(idroute)s
                                ORDER BY idta
                                """,
        {
            "rootidta": rootidta,
            "status": startstatus,
            "statust": OK,
            "merge": False,
            "idroute": idroute,
        },
    ):
        try:
            ta_info = dict(row)
            ta_fromfile = botslib.OldTransaction(ta_info["idta"])
            ta_tofile = ta_fromfile.copyta(status=endstatus)  # copy db_ta
            ta_info["filename"] = unicode(
                ta_tofile.idta
            )  # create filename for enveloped message
            ta_info["idroute"] = idroute
            botsglobal.logger.debug(
                "Envelope 1 message editype: %(editype)s, messagetype: %(messagetype)s.",
                ta_info,
            )
            envelope(ta_info, [row[str("filename")]])
            ta_info["filesize"] = os.path.getsize(
                botslib.abspathdata(ta_info["filename"])
            )
        except:
            txt = botslib.txtexc()
            ta_tofile.update(statust=ERROR, errortext=txt)
        else:
            ta_tofile.update(
                statust=OK, **ta_info
            )  # selection is used to update enveloped message;
        finally:
            ta_fromfile.update(statust=DONE)

    # **********for messages to merge & envelope
    # editype,messagetype: needed to get right envelope
    # envelope: envelope to use
    # rsrv3 : user defined enveloping criterium
    # frompartner,topartner,testindicator,charset,nrmessages: needed for envelope (edifact, x12)
    for row in botslib.query(
        """SELECT editype,messagetype,envelope,rsrv3,frompartner,topartner,testindicator,charset,sum(nrmessages) as nrmessages
                                FROM ta
                                WHERE idta>%(rootidta)s
                                AND status=%(status)s
                                AND statust=%(statust)s
                                AND merge=%(merge)s
                                AND idroute=%(idroute)s
                                GROUP BY editype,messagetype,envelope,rsrv3,frompartner,topartner,testindicator,charset
                                ORDER BY editype,messagetype,envelope,rsrv3,frompartner,topartner,testindicator,charset
                                """,
        {
            "rootidta": rootidta,
            "status": startstatus,
            "statust": OK,
            "merge": True,
            "idroute": idroute,
        },
    ):
        try:
            ta_info = dict(row)
            ta_info["idroute"] = idroute
            # do another query to gather individual idta and filenames
            filename_list = []
            for row2 in botslib.query(
                """SELECT idta, filename
                                        FROM ta
                                        WHERE idta>%(rootidta)s
                                        AND status=%(status)s
                                        AND statust=%(statust)s
                                        AND merge=%(merge)s
                                        AND editype=%(editype)s
                                        AND messagetype=%(messagetype)s
                                        AND (frompartner=%(frompartner)s OR frompartner IS NULL)
                                        AND (topartner=%(topartner)s OR topartner IS NULL)
                                        AND testindicator=%(testindicator)s
                                        AND envelope=%(envelope)s
                                        AND charset=%(charset)s
                                        ORDER BY idta
                                        """,
                {
                    "rootidta": rootidta,
                    "status": startstatus,
                    "statust": OK,
                    "merge": True,
                    "editype": ta_info["editype"],
                    "messagetype": ta_info["messagetype"],
                    "frompartner": ta_info["frompartner"],
                    "topartner": ta_info["topartner"],
                    "testindicator": ta_info["testindicator"],
                    "charset": ta_info["charset"],
                    "rsrv3": ta_info["rsrv3"],
                    "envelope": ta_info["envelope"],
                },
            ):
                ta_fromfile = botslib.OldTransaction(
                    row2[str("idta")]
                )  # edi message to be merged/envelope
                if not filename_list:  # if first time in loop
                    # copy db_ta; parent=0 as enveloping works via child, not parent
                    ta2_tofile = ta_fromfile.copyta(status=endstatus, parent=0)
                    ta_info["filename"] = unicode(ta2_tofile.idta)
                ta_fromfile.update(
                    child=ta2_tofile.idta, statust=DONE
                )  # add child because of n->1 relation
                filename_list.append(row2[str("filename")])
            botsglobal.logger.debug(
                "Merge and envelope: editype: %(editype)s, messagetype: %(messagetype)s, %(nrmessages)s messages",
                ta_info,
            )
            envelope(ta_info, filename_list)
            ta_info["filesize"] = os.path.getsize(
                botslib.abspathdata(ta_info["filename"])
            )
        except:
            txt = botslib.txtexc()
            ta2_tofile.update(statust=ERROR, errortext=txt)
        else:
            ta2_tofile.update(statust=OK, **ta_info)


def envelope(ta_info, ta_list):
    """ dispatch function for class Envelope and subclasses.
        editype, edimessage and envelope essential for enveloping.

        How is enveloping determined:
        1.  no enveloping: ta_info['envelope'] is '' (or None)
            -   file(s) is/are just copied.
            -   no user scripting for envelope.
        2.  user scripted: there is a file in bots/envelopescripts/ta_info['editype']/ta_info['envelope'].py (and has to have a class ta_info['envelope'])
            -   user exits extends/replaces default enveloping.
                syntax: grammar.editype.envelope (alt could be envelopescripts.editype.envelope; but this is inline with incoming)
                        grammar.editype.messagetype
        3.  default envelope: if ta_info['editype'] is a class in this module, use it.
                script: envelope.editype
                syntax: grammar.editype.envelope
                        grammar.editype.messagetype
    """
    userscript = scriptname = None
    if not ta_info["envelope"]:  # 1. no enveloping
        classtocall = noenvelope
    else:
        try:  # check for user scripted enveloping
            userscript, scriptname = botslib.botsimport(
                "envelopescripts", ta_info["editype"], ta_info["envelope"]
            )
            # 2. user scripted. If userscript does not have class ta_info['envelope']
            classtocall = getattr(userscript, ta_info["envelope"], None)
            # no error is given - file can have other functions in it.
        except botslib.BotsImportError:
            classtocall = None  # 3. default envelope
        if classtocall is None:
            try:
                classtocall = globals()[ta_info["editype"]]
            except KeyError:
                raise botslib.OutMessageError(
                    _('Not found envelope "%(envelope)s" for editype "%(editype)s".'),
                    ta_info,
                )
    env = classtocall(ta_info, ta_list, userscript, scriptname)
    env.run()


class Envelope(object):
    """ Base Class for enveloping; use subclasses."""

    def __init__(self, ta_info, ta_list, userscript, scriptname):
        self.ta_info = ta_info
        self.ta_list = ta_list
        self.userscript = userscript
        self.scriptname = scriptname

    def _openoutenvelope(self):
        """ make an outmessage object; read the grammar."""
        # self.ta_info contains information from ta: editype, messagetype,testindicator,charset,envelope
        self.out = outmessage.outmessage_init(**self.ta_info)  # make outmessage object.
        # read grammar for envelopesyntax. Remark: self.ta_info is not updated.
        self.out.messagegrammarread(typeofgrammarfile="envelope")

    def writefilelist(self, tofile):
        for filename in self.ta_list:
            fromfile = botslib.opendata(filename, "rb", self.ta_info["charset"])
            shutil.copyfileobj(fromfile, tofile, 1048576)
            fromfile.close()

    def filelist2absolutepaths(self):
        """ utility function; some classes need absolute filenames eg for xml-including"""
        return [botslib.abspathdata(filename) for filename in self.ta_list]

    def check_partners_are_known(self):
        """ check if partners are known."""
        if not self.ta_info["frompartner"]:
            raise botslib.OutMessageError(
                _('In enveloping "frompartner" unknown: "%(frompartner)s".'),
                self.ta_info,
            )
        if not self.ta_info["topartner"]:
            raise botslib.OutMessageError(
                _('In enveloping "topartner" unknown: "%(topartner)s".'), self.ta_info
            )

    def convert_partners(self):
        """ convert partnerID's according to syntax parameter IDmode.
        """
        IDmode = self.ta_info.get("IDmode", None)
        if IDmode is None:
            self.ta_info["frompartner_outer"] = self.ta_info["frompartner"]
            self.ta_info["frompartner_inner"] = self.ta_info["frompartner"]
            self.ta_info["topartner_outer"] = self.ta_info["topartner"]
            self.ta_info["topartner_inner"] = self.ta_info["topartner"]
            return
        frompartner = self.ta_info["frompartner"].split("|")
        topartner = self.ta_info["topartner"].split("|")
        if IDmode == "ISA_qualifier_GS":
            if len(frompartner) != 3:
                raise botslib.OutMessageError(
                    _(
                        'In enveloping "frompartner" is expected to have format "%(IDmode)s", but is "%(frompartner)s".'
                    ),
                    ta_info,
                )
            if len(topartner) != 3:
                raise botslib.OutMessageError(
                    _(
                        'In enveloping "topartner" is expected to have format "%(IDmode)s", but is "%(topartner)s".'
                    ),
                    ta_info,
                )
            self.ta_info["frompartner_outer"] = frompartner[0]
            self.ta_info["frompartner_qualifier"] = frompartner[1]
            self.ta_info["frompartner_inner"] = frompartner[2]
            self.ta_info["topartner_outer"] = topartner[0]
            self.ta_info["topartner_qualifier"] = topartner[1]
            self.ta_info["topartner_inner"] = topartner[2]
        elif IDmode in ["ISA_qualifier", "UNB_qualifier"]:
            if len(frompartner) != 2:
                raise botslib.OutMessageError(
                    _(
                        'In enveloping "frompartner" is expected to have format "%(IDmode)s", but is "%(frompartner)s".'
                    ),
                    ta_info,
                )
            if len(topartner) != 2:
                raise botslib.OutMessageError(
                    _(
                        'In enveloping "topartner" is expected to have format "%(IDmode)s", but is "%(topartner)s".'
                    ),
                    ta_info,
                )
            self.ta_info["frompartner_outer"] = frompartner[0]
            self.ta_info["frompartner_qualifier"] = frompartner[1]
            self.ta_info["frompartner_inner"] = frompartner[0]
            self.ta_info["topartner_outer"] = topartner[0]
            self.ta_info["topartner_qualifier"] = topartner[1]
            self.ta_info["topartner_inner"] = topartner[0]


class noenvelope(Envelope):
    """ Only copies the input files to one output file."""

    def run(self):
        botslib.tryrunscript(
            self.userscript, self.scriptname, "ta_infocontent", ta_info=self.ta_info
        )
        if len(self.ta_list) > 1:
            tofile = botslib.opendata(
                self.ta_info["filename"], "wb", self.ta_info["charset"]
            )
            self.writefilelist(tofile)
            tofile.close()
        else:
            self.ta_info["filename"] = self.ta_list[0]


class fixed(noenvelope):
    pass


class csv(noenvelope):
    def run(self):
        if self.ta_info["envelope"] == "csvheader":
            # ~ Adds first line to csv files with fieldnames; than write files.
            self._openoutenvelope()
            botslib.tryrunscript(
                self.userscript, self.scriptname, "ta_infocontent", ta_info=self.ta_info
            )

            tofile = botslib.opendata(
                self.ta_info["filename"], "wb", self.ta_info["charset"]
            )
            headers = dict(
                (field[ID], field[ID])
                for field in self.out.defmessage.structure[0][FIELDS]
            )
            self.out.put(headers)
            self.out.tree2records(self.out.root)
            tofile.write(self.out.record2string(self.out.lex_records[0:1]))
            self.writefilelist(tofile)
            tofile.close()
        else:
            super(csv, self).run()


class edifact(Envelope):
    """ Generate UNB and UNZ segment; fill with data, write to interchange-file."""

    def run(self):
        self.check_partners_are_known()
        self._openoutenvelope()
        self.ta_info.update(self.out.ta_info)
        botslib.tryrunscript(
            self.userscript, self.scriptname, "ta_infocontent", ta_info=self.ta_info
        )

        # version dependent enveloping
        if self.ta_info["version"] < "4":
            date = botslib.strftime("%y%m%d")
            reserve = " "
        else:
            date = botslib.strftime("%Y%m%d")
            reserve = self.ta_info["reserve"]

        # UNB reference is counter is per sender or receiver
        if botsglobal.ini.getboolean("settings", "interchangecontrolperpartner", False):
            self.ta_info["reference"] = unicode(
                botslib.unique("unbcounter_" + self.ta_info["topartner"])
            )
        else:
            self.ta_info["reference"] = unicode(
                botslib.unique("unbcounter_" + self.ta_info["frompartner"])
            )
        # testindicator is more complex:
        if (
            self.ta_info["testindicator"] and self.ta_info["testindicator"] != "0"
        ):  # first check value from ta; do not use default
            testindicator = "1"
        elif self.ta_info["UNB.0035"] != "0":  # than check values from grammar
            testindicator = "1"
        else:
            testindicator = ""
        # build the envelope segments (that is, the tree from which the segments will be generated)
        self.out.put(
            {
                "BOTSID": "UNB",
                "S001.0001": self.ta_info["charset"],
                "S001.0002": self.ta_info["version"],
                "S002.0004": self.ta_info["frompartner"],
                "S003.0010": self.ta_info["topartner"],
                "S004.0017": date,
                "S004.0019": botslib.strftime("%H%M"),
                "0020": self.ta_info["reference"],
            }
        )
        # the following fields are conditional; do not write these when empty
        # string (separator compression does take empty strings into account)
        for field in (
            "S001.0080",
            "S001.0133",
            "S002.0007",
            "S002.0008",
            "S002.0042",
            "S003.0007",
            "S003.0014",
            "S003.0046",
            "S005.0022",
            "S005.0025",
            "0026",
            "0029",
            "0031",
            "0032",
        ):
            if self.ta_info["UNB." + field]:
                self.out.put({"BOTSID": "UNB", field: self.ta_info["UNB." + field]})
        if testindicator:
            self.out.put({"BOTSID": "UNB", "0035": testindicator})
        self.out.put(
            {"BOTSID": "UNB"},
            {
                "BOTSID": "UNZ",
                "0036": self.ta_info["nrmessages"],
                "0020": self.ta_info["reference"],
            },
        )  # dummy segment; is not used
        # user exit
        botslib.tryrunscript(
            self.userscript,
            self.scriptname,
            "envelopecontent",
            ta_info=self.ta_info,
            out=self.out,
        )
        # convert the tree into segments; here only the UNB is written (first segment)
        self.out.checkmessage(self.out.root, self.out.defmessage)
        self.out.checkforerrorlist()
        self.out.tree2records(self.out.root)
        # start doing the actual writing:
        tofile = botslib.opendata(
            self.ta_info["filename"], "wb", self.ta_info["charset"]
        )
        if self.ta_info["forceUNA"] or self.ta_info["charset"] != "UNOA":
            tofile.write(
                "UNA"
                + self.ta_info["sfield_sep"]
                + self.ta_info["field_sep"]
                + self.ta_info["decimaal"]
                + self.ta_info["escape"]
                + reserve
                + self.ta_info["record_sep"]
                + self.ta_info["add_crlfafterrecord_sep"]
            )
        tofile.write(self.out.record2string(self.out.lex_records[0:1]))
        self.writefilelist(tofile)
        tofile.write(self.out.record2string(self.out.lex_records[1:2]))
        tofile.close()


class tradacoms(Envelope):
    """ Generate STX and END segment; fill with appropriate data, write to interchange file."""

    def run(self):
        self.check_partners_are_known()
        self._openoutenvelope()
        self.ta_info.update(self.out.ta_info)
        botslib.tryrunscript(
            self.userscript, self.scriptname, "ta_infocontent", ta_info=self.ta_info
        )
        # prepare data for envelope
        if botsglobal.ini.getboolean("settings", "interchangecontrolperpartner", False):
            self.ta_info["reference"] = unicode(
                botslib.unique("stxcounter_" + self.ta_info["topartner"])
            )
        else:
            self.ta_info["reference"] = unicode(
                botslib.unique("stxcounter_" + self.ta_info["frompartner"])
            )
        # build the envelope segments (that is, the tree from which the segments will be generated)
        self.out.put(
            {
                "BOTSID": "STX",
                "STDS1": self.ta_info["STX.STDS1"],
                "STDS2": self.ta_info["STX.STDS2"],
                "FROM.01": self.ta_info["frompartner"],
                "UNTO.01": self.ta_info["topartner"],
                "TRDT.01": botslib.strftime("%y%m%d"),
                "TRDT.02": botslib.strftime("%H%M%S"),
                "SNRF": self.ta_info["reference"],
            }
        )
        if self.ta_info["STX.FROM.02"]:
            self.out.put({"BOTSID": "STX", "FROM.02": self.ta_info["STX.FROM.02"]})
        if self.ta_info["STX.UNTO.02"]:
            self.out.put({"BOTSID": "STX", "UNTO.02": self.ta_info["STX.UNTO.02"]})
        if self.ta_info["STX.APRF"]:
            self.out.put({"BOTSID": "STX", "APRF": self.ta_info["STX.APRF"]})
        if self.ta_info["STX.PRCD"]:
            self.out.put({"BOTSID": "STX", "PRCD": self.ta_info["STX.PRCD"]})
        self.out.put(
            {"BOTSID": "STX"}, {"BOTSID": "END", "NMST": self.ta_info["nrmessages"]}
        )  # dummy segment; is not used
        # user exit
        botslib.tryrunscript(
            self.userscript,
            self.scriptname,
            "envelopecontent",
            ta_info=self.ta_info,
            out=self.out,
        )
        # convert the tree into segments; here only the STX is written (first segment)
        self.out.checkmessage(self.out.root, self.out.defmessage)
        self.out.checkforerrorlist()
        self.out.tree2records(self.out.root)

        # start doing the actual writing:
        tofile = botslib.opendata(
            self.ta_info["filename"], "wb", self.ta_info["charset"]
        )
        tofile.write(self.out.record2string(self.out.lex_records[0:1]))
        self.writefilelist(tofile)
        tofile.write(self.out.record2string(self.out.lex_records[1:2]))
        tofile.close()


class templatehtml(Envelope):
    """ class for outputting edi as html (browser, email).
        Uses a genshi-template for the enveloping/merging.
    """

    def run(self):
        try:
            from genshi.template import TemplateLoader
        except:
            raise ImportError(
                'Dependency failure: editype "templatehtml" requires python library "genshi".'
            )
        self._openoutenvelope()
        self.ta_info.update(self.out.ta_info)
        botslib.tryrunscript(
            self.userscript, self.scriptname, "ta_infocontent", ta_info=self.ta_info
        )
        if not self.ta_info["envelope-template"]:
            raise botslib.OutMessageError(
                _(
                    'While enveloping in "%(editype)s.%(messagetype)s": syntax option "envelope-template" not filled; is required.'
                ),
                self.ta_info,
            )
        templatefile = botslib.abspath(
            self.__class__.__name__, self.ta_info["envelope-template"]
        )
        ta_list = self.filelist2absolutepaths()
        try:
            botsglobal.logger.debug(
                'Start writing envelope to file "%(filename)s".', self.ta_info
            )
            loader = TemplateLoader(auto_reload=False)
            tmpl = loader.load(templatefile)
        except:
            txt = botslib.txtexc()
            raise botslib.OutMessageError(
                _('While enveloping in "%(editype)s.%(messagetype)s", error:\n%(txt)s'),
                {
                    "editype": self.ta_info["editype"],
                    "messagetype": self.ta_info["messagetype"],
                    "txt": txt,
                },
            )
        try:
            filehandler = botslib.opendata_bin(self.ta_info["filename"], "wb")
            stream = tmpl.generate(data=ta_list)
            stream.render(
                method="xhtml", encoding=self.ta_info["charset"], out=filehandler
            )
        except:
            txt = botslib.txtexc()
            raise botslib.OutMessageError(
                _('While enveloping in "%(editype)s.%(messagetype)s", error:\n%(txt)s'),
                {
                    "editype": self.ta_info["editype"],
                    "messagetype": self.ta_info["messagetype"],
                    "txt": txt,
                },
            )
        finally:
            filehandler.close()


class x12(Envelope):
    """ Generate envelope segments; fill with appropriate data, write to interchange-file."""

    def run(self):
        self.check_partners_are_known()
        self._openoutenvelope()  # and read grammar - including partner specific syntax
        self.ta_info.update(self.out.ta_info)
        self.convert_partners()
        botslib.tryrunscript(
            self.userscript, self.scriptname, "ta_infocontent", ta_info=self.ta_info
        )
        # test indicator can either be from configuration (self.ta_info['ISA15'])
        # or by mapping (self.ta_info['testindicator']); mapping overrules.
        if (
            self.ta_info["testindicator"] and self.ta_info["testindicator"] != "0"
        ):  # '0' is default value (in db)
            testindicator = self.ta_info["testindicator"]
        else:
            testindicator = self.ta_info["ISA15"]
        # frompartner
        # use ISA06 if defined in syntax, else frompartner_outer
        isa06sender = self.ta_info.get("ISA06", self.ta_info["frompartner_outer"])
        isa06sender = isa06sender.ljust(15)  # add spaces; is fixed length
        isa05qualifier = self.ta_info.get(
            "frompartner_qualifier", self.ta_info["ISA05"]
        )
        gs02sender = self.ta_info.get("GS02", self.ta_info["frompartner_inner"])
        # topartner
        # use ISA06 if defined in syntax, else frompartner_outer
        isa08receiver = self.ta_info.get("ISA08", self.ta_info["topartner_outer"])
        isa08receiver = isa08receiver.ljust(15)  # add spaces; is fixed length
        isa07qualifier = self.ta_info.get("topartner_qualifier", self.ta_info["ISA07"])
        gs03receiver = self.ta_info.get("GS03", self.ta_info["topartner_inner"])
        # isa_counter
        if botsglobal.ini.getboolean("settings", "interchangecontrolperpartner", False):
            self.ta_info["reference"] = unicode(
                botslib.unique("isacounter_" + self.ta_info["topartner_outer"])
            )
        else:
            self.ta_info["reference"] = unicode(
                botslib.unique("isacounter_" + self.ta_info["frompartner_outer"])
            )
        # date and time
        senddate = botslib.strftime("%Y%m%d")
        sendtime = botslib.strftime("%H%M")
        # build the envelope segments (generate tree from which the segments will be generated)
        self.out.put(
            {
                "BOTSID": "ISA",
                "ISA01": self.ta_info["ISA01"],
                "ISA02": self.ta_info["ISA02"],
                "ISA03": self.ta_info["ISA03"],
                "ISA04": self.ta_info["ISA04"],
                "ISA05": isa05qualifier,
                "ISA06": isa06sender,
                "ISA07": isa07qualifier,
                "ISA08": isa08receiver,
                "ISA09": senddate[2:],
                "ISA10": sendtime,
                "ISA11": self.ta_info[
                    "ISA11"
                ],  # if ISA version > 00403, replaced by reprtion separator
                "ISA12": self.ta_info["version"],
                "ISA13": self.ta_info["reference"],
                "ISA14": self.ta_info["ISA14"],
                "ISA15": testindicator,
            },
            strip=False,
        )  # MIND: strip=False: ISA fields shoudl not be stripped as it is fixed-length
        self.out.put(
            {"BOTSID": "ISA"},
            {"BOTSID": "IEA", "IEA01": "1", "IEA02": self.ta_info["reference"]},
        )
        gs08messagetype = self.ta_info["messagetype"][3:]
        if gs08messagetype[:6] < "004010":
            pass
        else:
            senddate = senddate[2:]
        self.out.put(
            {"BOTSID": "ISA"},
            {
                "BOTSID": "GS",
                "GS01": self.ta_info["functionalgroup"],
                "GS02": gs02sender,
                "GS03": gs03receiver,
                "GS04": senddate,
                "GS05": sendtime,
                "GS06": self.ta_info["reference"],
                "GS07": self.ta_info["GS07"],
                "GS08": gs08messagetype,
            },
        )
        self.out.put(
            {"BOTSID": "ISA"},
            {"BOTSID": "GS"},
            {
                "BOTSID": "GE",
                "GE01": self.ta_info["nrmessages"],
                "GE02": self.ta_info["reference"],
            },
        )
        # user exit
        botslib.tryrunscript(
            self.userscript,
            self.scriptname,
            "envelopecontent",
            ta_info=self.ta_info,
            out=self.out,
        )
        # convert the tree into segments; here only the UNB is written (first segment)
        self.out.checkmessage(self.out.root, self.out.defmessage)
        self.out.checkforerrorlist()
        self.out.tree2records(self.out.root)
        # start doing the actual writing:
        tofile = botslib.opendata(
            self.ta_info["filename"], "wb", self.ta_info["charset"]
        )
        isa_string = self.out.record2string(self.out.lex_records[0:1])
        # ISA has the used separators at certain positions. Bots would give errors
        # for this (can not use sep as data) or compress these away. So this is
        # hardcoded.
        if self.ta_info["version"] < "00403":
            isa_string = (
                isa_string[:103]
                + self.ta_info["field_sep"]
                + self.ta_info["sfield_sep"]
                + isa_string[103:]
            )
        else:
            isa_string = (
                isa_string[:82]
                + self.ta_info["reserve"]
                + isa_string[83:103]
                + self.ta_info["field_sep"]
                + self.ta_info["sfield_sep"]
                + isa_string[103:]
            )
        tofile.write(isa_string)  # write ISA
        tofile.write(self.out.record2string(self.out.lex_records[1:2]))  # write GS
        self.writefilelist(tofile)
        tofile.write(
            self.out.record2string(self.out.lex_records[2:])
        )  # write GE and IEA
        tofile.close()


class jsonnocheck(noenvelope):
    pass


class json(noenvelope):
    pass


class xmlnocheck(noenvelope):
    pass


class xml(noenvelope):
    pass


class db(noenvelope):
    pass


class raw(noenvelope):
    pass
