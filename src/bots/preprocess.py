# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys

if sys.version_info[0] > 2:
    basestring = unicode = str
import os
import re
import zipfile
import string
from django.utils.translation import ugettext as _

# bots-modules
from . import botslib
from . import botsglobal
from .botsconfig import *


@botslib.log_session
def preprocess(routedict, function, status=FILEIN, rootidta=None, **argv):
    """ for preprocessing of files.
        these are NOT translations; translation involve grammars, mapping scripts etc. think of eg:
        - unzipping zipped files.
        - password protected files.
        Than the actual processing function is called.
        If errors occur during processing, no ta are left with status FILEIN !
        preprocess is called right after the in-communicatiation
    """
    if rootidta is None:
        rootidta = botsglobal.currentrun.get_minta4query()
    nr_files = 0
    for row in botslib.query(
        """SELECT idta,filename
                                FROM ta
                                WHERE idta>%(rootidta)s
                                AND status=%(status)s
                                AND statust=%(statust)s
                                AND idroute=%(idroute)s
                                AND fromchannel=%(fromchannel)s
                                """,
        {
            "status": status,
            "statust": OK,
            "idroute": routedict["idroute"],
            "fromchannel": routedict["fromchannel"],
            "rootidta": rootidta,
        },
    ):
        try:
            botsglobal.logger.debug(
                'Start preprocessing "%(name)s" for file "%(filename)s".',
                {"name": function.__name__, "filename": row[str("filename")]},
            )
            ta_from = botslib.OldTransaction(row[str("idta")])
            ta_from.filename = row[str("filename")]
            function(ta_from=ta_from, endstatus=status, routedict=routedict, **argv)
        except:
            txt = botslib.txtexc()
            ta_from.update(statust=ERROR, errortext=txt)
            ta_from.deletechildren()
        else:
            botsglobal.logger.debug(
                'OK preprocessing "%(name)s" for file "%(filename)s".',
                {"name": function.__name__, "filename": row[str("filename")]},
            )
            ta_from.update(statust=DONE)
            nr_files += 1
    return nr_files


@botslib.log_session
def postprocess(routedict, function, status=FILEOUT, rootidta=None, **argv):
    """ for postprocessing of files.
        these are NOT translations; translation involve grammars, mapping scripts etc. think of eg:
        - zip files.
        If errors occur during processing, no ta are left with status FILEOUT !
        postprocess is called right before the out-communicatiation
    """
    if rootidta is None:
        rootidta = botsglobal.currentrun.get_minta4query_routepart()
    nr_files = 0
    for row in botslib.query(
        """SELECT idta,filename
                                FROM ta
                                WHERE idta>%(rootidta)s
                                AND status=%(status)s
                                AND statust=%(statust)s
                                AND idroute=%(idroute)s
                                AND tochannel=%(tochannel)s
                                """,
        {
            "status": status,
            "statust": OK,
            "idroute": routedict["idroute"],
            "tochannel": routedict["tochannel"],
            "rootidta": rootidta,
        },
    ):
        try:
            botsglobal.logger.debug(
                'Start postprocessing "%(name)s" for file "%(filename)s".',
                {"name": function.__name__, "filename": row[str("filename")]},
            )
            ta_from = botslib.OldTransaction(row[str("idta")])
            ta_from.filename = row[str("filename")]
            function(ta_from=ta_from, endstatus=status, routedict=routedict, **argv)
        except:
            txt = botslib.txtexc()
            ta_from.update(statust=ERROR, errortext=txt)
            ta_from.deletechildren()
        else:
            botsglobal.logger.debug(
                'OK postprocessing "%(name)s" for file "%(filename)s".',
                {"name": function.__name__, "filename": row[str("filename")]},
            )
            ta_from.update(statust=DONE)
            nr_files += 1
    return nr_files


# regular expression for mailbag.
HEADER = re.compile(
    """
    \s*
    (
        (?P<edifact>
            (?P<UNA>
                U[\n\r]*N[\n\r]*A
                (?P<UNAstring>.+?)
            )?
            (?P<UNB>
                U[\n\r]*N[\n\r]*B
            )
            [\n\r]*
            (?P<field_sep>[^\n\r])
        )
        |
        (?P<tradacoms>
            (?P<STX>
                S[\n\r]*T[\n\r]*X
                [\n\r]*
                =
            )
        )
        |
        (?P<x12>
            I[\n\r]*S[\n\r]*A
        )
    )
    """,
    re.DOTALL | re.VERBOSE,
)


def mailbag(ta_from, endstatus, frommessagetype, **argv):
    """ 2 main functions:
        -   recognizes and distuinguishes several edi types: x12 edifact tradacoms ('mailbag' in, correct editype out)
        -   split up interchanges (edifact, x12, tradacoms)
        details:
        - edifact, x12 and tradacoms can be can be mixed
        - handle multiple UNA in one file, including different charsets.
        - handle multiple ISA's with different separators in one file
        in bots > 3.0.0 all mailbag, edifact, x12 and tradacoms go via mailbag.
    """
    edifile = botslib.readdata(filename=ta_from.filename, charset="iso-8859-1")
    startpos = 0
    nr_interchanges = 0
    while True:
        found = HEADER.match(edifile[startpos:])
        if found is None:
            if edifile[startpos:].strip(
                string.whitespace + "\x1A\x00"
            ):  # there is content...but not valid
                if nr_interchanges:  # found interchanges, but remainder is not valid
                    raise botslib.InMessageError(
                        _(
                            "[M50]: Found data not in a valid interchange at position %(pos)s."
                        ),
                        {"pos": startpos},
                    )
                else:  # no interchanges found, content is not a valid edifact/x12/tradacoms interchange
                    if (
                        frommessagetype == "mailbag"
                    ):  # if indicated 'mailbag': guess if this is an xml file.....
                        sniffxml = edifile[:25]
                        # to find first ' real' data; some char are because of BOM, UTF-16 etc
                        sniffxml = sniffxml.lstrip(
                            " \t\n\r\f\v\xFF\xFE\xEF\xBB\xBF\x00"
                        )
                        if sniffxml and sniffxml[0] == "<":
                            # is a xml file; inmessage.py can determine the right xml messagetype via xpath.
                            filesize = len(edifile)
                            ta_to = ta_from.copyta(
                                status=endstatus,
                                statust=OK,
                                filename=ta_from.filename,
                                editype="xml",
                                messagetype="mailbag",
                                filesize=filesize,
                            )
                            return
                    raise botslib.InMessageError(
                        _("[M51]: Edi file does not start with a valid interchange.")
                    )
            else:  # no parseble content
                if (
                    nr_interchanges
                ):  # OK: there are interchanges, but no new interchange is found.
                    return
                else:  # no edifact/x12/tradacoms envelope at all
                    raise botslib.InMessageError(
                        _("[M52]: Edi file contains only whitespace.")
                    )
        elif found.group("x12"):
            editype = "x12"
            headpos = startpos + found.start("x12")
            # determine field_sep and record_sep
            count = 0
            for char in edifile[
                headpos : headpos + 120
            ]:  # search first 120 characters to determine separators
                if char in "\r\n" and count != 105:
                    continue
                count += 1
                if count == 4:
                    field_sep = char
                elif count in [
                    7,
                    18,
                    21,
                    32,
                    35,
                    51,
                    54,
                    70,
                ]:  # extra checks for fixed ISA.
                    if char != field_sep:
                        raise botslib.InMessageError(
                            _(
                                '[M53]: Non-valid ISA header at position %(pos)s; position %(pos_element)s of ISA is "%(foundchar)s", expect here element separator "%(field_sep)s".'
                            ),
                            {
                                "pos": headpos,
                                "pos_element": unicode(count),
                                "foundchar": char,
                                "field_sep": field_sep,
                            },
                        )
                elif count == 106:
                    record_sep = char
                    break
            foundtrailer = re.search(
                """%(record_sep)s
                                        \s*
                                        I[\n\r]*E[\n\r]*A
                                        .+?
                                        %(record_sep)s
                                        """
                % {"record_sep": re.escape(record_sep)},
                edifile[headpos:],
                re.DOTALL | re.VERBOSE,
            )
            if not foundtrailer:
                foundtrailer2 = re.search(
                    """%(record_sep)s
                                            \s*
                                            I[\n\r]*E[\n\r]*A
                                            """
                    % {"record_sep": re.escape(record_sep)},
                    edifile[headpos:],
                    re.DOTALL | re.VERBOSE,
                )
                if foundtrailer2:
                    raise botslib.InMessageError(
                        _(
                            "[M60]: Found no segment terminator for IEA trailer at position %(pos)s."
                        ),
                        {"pos": foundtrailer2.start()},
                    )
                else:
                    raise botslib.InMessageError(
                        _(
                            "[M54]: Found no valid IEA trailer for the ISA header at position %(pos)s."
                        ),
                        {"pos": headpos},
                    )
        elif found.group("edifact"):
            editype = "edifact"
            headpos = startpos + found.start("edifact")
            # parse UNA. valid UNA: UNA:+.? '
            if found.group("UNA"):
                count = 0
                for char in found.group("UNAstring"):
                    if char in "\r\n":
                        continue
                    count += 1
                    if count == 2:
                        field_sep = char
                    elif count == 4:
                        escape = char
                    elif count == 6:
                        record_sep = char
                if count != 6 and len(found.group("UNAstring").rstrip()) != 6:
                    raise botslib.InMessageError(
                        _(
                            "[M55]: Non-valid UNA-segment at position %(pos)s. UNA-segment should be 6 positions."
                        ),
                        {"pos": headpos},
                    )
                if found.group("field_sep") != field_sep:
                    raise botslib.InMessageError(
                        _(
                            "[M56]: Data element separator used in edifact file differs from value indicated in UNA-segment."
                        )
                    )
            else:  # no UNA, interpret UNB
                if found.group("field_sep") == "+":
                    record_sep = "'"
                    escape = "?"
                # according to std this was preffered way...probably quite theoretic...but does no harm
                elif found.group("field_sep") == "\x1D":
                    record_sep = "\x1C"
                    escape = ""
                else:
                    raise botslib.InMessageError(
                        _(
                            "[M57]: Edifact file with non-standard separators. UNA segment should be used."
                        )
                    )
            # search trailer
            foundtrailer = re.search(
                """[^%(escape)s\n\r]       #char that is not escape or cr/lf
                                        [\n\r]*?                #maybe some cr/lf's
                                        %(record_sep)s          #segment separator
                                        \s*                     #whitespace between segments
                                        U[\n\r]*N[\n\r]*Z       #UNZ
                                        .+?                     #any chars
                                        [^%(escape)s\n\r]       #char that is not escape or cr/lf
                                        [\n\r]*?                #maybe some cr/lf's
                                        %(record_sep)s          #segment separator
                                        """
                % {"escape": escape, "record_sep": re.escape(record_sep)},
                edifile[headpos:],
                re.DOTALL | re.VERBOSE,
            )
            if not foundtrailer:
                raise botslib.InMessageError(
                    _(
                        "[M58]: Found no valid UNZ trailer for the UNB header at position %(pos)s."
                    ),
                    {"pos": headpos},
                )
        elif found.group("tradacoms"):
            editype = "tradacoms"
            # ~ field_sep = '='     #the tradacoms 'after-segment-tag-separator'
            record_sep = "'"
            escape = "?"
            headpos = startpos + found.start("STX")
            foundtrailer = re.search(
                """[^%(escape)s\n\r]       #char that is not escape or cr/lf
                                        [\n\r]*?                #maybe some cr/lf's
                                        %(record_sep)s          #segment separator
                                        \s*                     #whitespace between segments
                                        E[\n\r]*N[\n\r]*D
                                        .+?
                                        [^%(escape)s\n\r]       #char that is not escape or cr/lf
                                        [\n\r]*?                #maybe some cr/lf's
                                        %(record_sep)s          #segment separator
                                        """
                % {"escape": escape, "record_sep": re.escape(record_sep)},
                edifile[headpos:],
                re.DOTALL | re.VERBOSE,
            )
            if not foundtrailer:
                raise botslib.InMessageError(
                    _(
                        "[M59]: Found no valid END trailer for the STX header at position %(pos)s."
                    ),
                    {"pos": headpos},
                )
        # so: found an interchange (from headerpos until endpos)
        endpos = headpos + foundtrailer.end()
        ta_to = ta_from.copyta(
            status=endstatus
        )  # make transaction for translated message; gets ta_info of ta_frommes
        tofilename = unicode(ta_to.idta)
        filesize = len(edifile[headpos:endpos])
        tofile = botslib.opendata(tofilename, "wb", charset="iso-8859-1")
        tofile.write(edifile[headpos:endpos])
        tofile.close()
        # editype is now either edifact, x12 or tradacoms
        # frommessagetype is the original frommessagetype (from route).
        # frommessagetype would normally be edifact, x12, tradacoms or mailbag, but could also be eg ORDERSD96AUNEAN007.
        # If so, we want to preserve that.
        if frommessagetype != "mailbag" and frommessagetype != editype:
            messagetype = frommessagetype
        else:
            messagetype = editype
        ta_to.update(
            statust=OK,
            filename=tofilename,
            editype=editype,
            messagetype=messagetype,
            filesize=filesize,
        )  # update outmessage transaction with ta_info;
        startpos = endpos
        nr_interchanges += 1
        botsglobal.logger.debug(
            _('        File written: "%(tofilename)s".'), {"tofilename": tofilename}
        )


def botsunzip(ta_from, endstatus, password=None, pass_non_zip=False, **argv):
    """ unzip file;
        editype & messagetype are unchanged.
    """
    try:
        myzipfile = zipfile.ZipFile(
            botslib.abspathdata(filename=ta_from.filename), mode="r"
        )
    except zipfile.BadZipfile:
        botsglobal.logger.debug(_("File is not a zip-file."))
        if pass_non_zip:  # just pass the file
            botsglobal.logger.debug(_('"pass_non_zip" is True, just pass the file.'))
            ta_to = ta_from.copyta(status=endstatus, statust=OK)
            return
        raise botslib.InMessageError(_("File is not a zip-file."))

    if password:
        myzipfile.setpassword(password)
    for info_file_in_zip in myzipfile.infolist():
        if (
            info_file_in_zip.filename[-1] == "/"
        ):  # check if this is a dir; if so continue
            continue
        ta_to = ta_from.copyta(status=endstatus)
        tofilename = unicode(ta_to.idta)
        content = myzipfile.read(info_file_in_zip.filename)  # read file in zipfile
        filesize = len(content)
        tofile = botslib.opendata_bin(tofilename, "wb")
        tofile.write(content)
        tofile.close()
        ta_to.update(
            statust=OK, filename=tofilename, filesize=filesize
        )  # update outmessage transaction with ta_info;
        botsglobal.logger.debug(
            _('        File written: "%(tofilename)s".'), {"tofilename": tofilename}
        )
    myzipfile.close()


def botszip(ta_from, endstatus, **argv):
    """ zip file;
        editype & messagetype are unchanged.
    """
    ta_to = ta_from.copyta(status=endstatus)
    tofilename = unicode(ta_to.idta)
    pluginzipfilehandler = zipfile.ZipFile(
        botslib.abspathdata(filename=tofilename), "w", zipfile.ZIP_DEFLATED
    )
    pluginzipfilehandler.write(
        botslib.abspathdata(filename=ta_from.filename), ta_from.filename
    )
    pluginzipfilehandler.close()
    ta_to.update(
        statust=OK, filename=tofilename
    )  # update outmessage transaction with ta_info;


def extractpdf(ta_from, endstatus, **argv):
    """ Try to extract text content of a PDF file to a csv.
        You know this is not a great idea, right? But we'll do the best we can anyway!
        Page and line numbers are added to each row.
        Columns and rows are based on the x and y coordinates of each text element within tolerance allowed.
        Multiple text elements may combine to make one field, some PDFs have every character separated!
        You may need to experiment with x_group and y_group values, but defaults seem ok for most files.
        Output csv is UTF-8 encoded - The csv module doesn't directly support reading and writing Unicode
        If the PDF is just an image, all bets are off. Maybe try OCR, good luck with that!
        Mike Griffin 14/12/2011
    """
    from pdfminer.pdfinterp import PDFResourceManager, process_pdf
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams, LTContainer, LTText, LTTextBox
    import csv

    class CsvConverter(TextConverter):
        def __init__(self, *args, **kwargs):
            TextConverter.__init__(self, *args, **kwargs)

        def receive_layout(self, ltpage):

            # recursively get every text element and it's coordinates
            def render(item):
                if isinstance(item, LTContainer):
                    for child in item:
                        render(child)
                elif isinstance(item, LTText):
                    (unused1, unused2, x, y) = item.bbox

                    # group the y values (rows) within group tolerance
                    for v in yv:
                        if y > v - y_group and y < v + y_group:
                            y = v
                    yv.append(y)

                    line = lines[int(-y)]
                    line[x] = item.get_text().encode("utf-8")

            from collections import defaultdict

            lines = defaultdict(lambda: {})

            yv = []
            render(ltpage)

            lineid = 0
            for y in sorted(lines.keys()):
                line = lines[y]
                lineid += 1
                csvdata = [
                    ltpage.pageid,
                    lineid,
                ]  # first 2 columns are page and line numbers

                # group the x values (fields) within group tolerance
                p = 0
                field_txt = ""
                for x in sorted(line.keys()):
                    gap = x - p
                    if p > 0 and gap > x_group:
                        csvdata.append(field_txt)
                        field_txt = ""
                    field_txt += line[x]
                    p = x
                csvdata.append(field_txt)
                csvout.writerow(csvdata)
            if lineid == 0:
                raise botslib.InMessageError(
                    _("PDF text extraction failed, it may contain just image(s)?")
                )

    # get some optional parameters
    x_group = argv.get("x_group", 10)  # group text closer than this as one field
    y_group = argv.get("y_group", 5)  # group lines closer than this as one line
    password = argv.get("password", "")
    quotechar = argv.get("quotechar", '"')
    field_sep = argv.get("field_sep", ",")
    escape = argv.get("escape", "\\")
    charset = argv.get("charset", "utf-8")
    if not escape:
        doublequote = True
    else:
        doublequote = False

    try:
        pdf_stream = botslib.opendata_bin(ta_from.filename, "rb")
        ta_to = ta_from.copyta(status=endstatus)
        tofilename = unicode(ta_to.idta)
        csv_stream = botslib.opendata_bin(tofilename, "wb")
        csvout = csv.writer(
            csv_stream,
            quotechar=quotechar,
            delimiter=field_sep,
            doublequote=doublequote,
            escapechar=escape,
        )

        # Process PDF
        rsrcmgr = PDFResourceManager(caching=True)
        device = CsvConverter(rsrcmgr, csv_stream, codec=charset)
        process_pdf(
            rsrcmgr,
            device,
            pdf_stream,
            pagenos=set(),
            password=password,
            caching=True,
            check_extractable=True,
        )

        device.close()
        pdf_stream.close()
        csv_stream.close()
        filesize = os.path.getsize(botslib.abspathdata(tofilename))
        ta_to.update(
            statust=OK, filename=tofilename, filesize=filesize
        )  # update outmessage transaction with ta_info;
        botsglobal.logger.debug(
            _('        File written: "%(tofilename)s".'), {"tofilename": tofilename}
        )
    except:
        txt = botslib.txtexc()
        botsglobal.logger.error(
            _("PDF extraction failed, may not be a PDF file? Error:\n%(txt)s"),
            {"txt": txt},
        )
        raise botslib.InMessageError(
            _("PDF extraction failed, may not be a PDF file? Error:\n%(txt)s"),
            {"txt": txt},
        )
