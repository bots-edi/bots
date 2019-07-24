# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import copy
import datetime
import re
import django
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.utils.translation import ugettext as _
from . import models
from . import botsglobal
from .botsconfig import *


def safe_int(value):
    try:
        return int(value)
    except:
        return 0


def preparereport2view(post, runidta):
    terugpost = post.copy()
    thisrun = models.report.objects.get(idta=runidta)
    terugpost["datefrom"] = thisrun.ts
    try:
        nextrun = thisrun.get_next_by_ts()
        terugpost["dateuntil"] = nextrun.ts
    except:
        terugpost["dateuntil"] = datetimeuntil()
    return terugpost


def changepostparameters(post, soort):
    terugpost = post.copy()
    if soort == "confirm2in":
        for key in ["confirmtype", "confirmed", "fromchannel", "tochannel"]:
            terugpost.pop(key)
        terugpost["ineditype"] = terugpost.pop("editype")[0]
        terugpost["inmessagetype"] = terugpost.pop("messagetype")[0]
        # ~ terugpost['outeditype'] = ''
        # ~ terugpost['outmessagetype'] = ''
    elif soort == "confirm2out":
        for key in ["confirmtype", "confirmed", "fromchannel", "tochannel"]:
            terugpost.pop(key)
    elif soort == "out2in":
        terugpost["outeditype"] = terugpost.pop("editype")[0]
        terugpost["outmessagetype"] = terugpost.pop("messagetype")[0]
        # ~ terugpost['ineditype'] = ''
        # ~ terugpost['inmessagetype'] = ''
    elif soort == "out2confirm":
        for key in ["lastrun"]:
            terugpost.pop(key)
    elif soort == "in2out":
        terugpost["editype"] = terugpost.pop("outeditype")[0]
        terugpost["messagetype"] = terugpost.pop("outmessagetype")[0]
        for key in ["ineditype", "inmessagetype"]:
            terugpost.pop(key)
    elif soort == "in2confirm":
        terugpost["editype"] = terugpost.pop("outeditype")[0]
        terugpost["messagetype"] = terugpost.pop("outmessagetype")[0]
        for key in ["lastrun", "statust", "ineditype", "inmessagetype"]:
            terugpost.pop(key)
    elif soort == "2process":
        # when going to process, most parameters are deleted.
        for key in list(terugpost.keys()):
            if key not in ["datefrom", "dateuntil", "lastrun", "idroute"]:  # keep these
                terugpost.pop(key)
    elif soort == "fromprocess":
        pass  # is OK, all values are used
    terugpost["sortedby"] = "ts"
    terugpost["sortedasc"] = False
    terugpost["page"] = 1
    return terugpost


def django_trace_origin(idta, where):
    """ bots traces back all from the current step/ta_object.
        where is a dict that is used to indicate a condition.
        eg:  {'status':EXTERNIN}
        If bots finds a ta_object for which this is true, the ta_object is added to a list.
        The list is returned when all tracing is done, and contains all ta_object's for which 'where' is True
    """

    def trace_recurse(ta_object):
        """ recursive
            walk over ta_object's backward (to origin).
            if condition is met, add the ta_object to a list
        """
        for parent in get_parent(ta_object):
            donelijst.append(parent.idta)
            for key, value in where.items():
                if getattr(parent, key) != value:
                    break
            else:  # all where-criteria are true; check if we already have this ta_object
                teruglijst.append(parent)
            trace_recurse(parent)

    def get_parent(ta_object):
        """ yields the parents of a ta_object """
        if ta_object.parent:
            if ta_object.parent not in donelijst:  # search via parent
                yield models.ta.objects.get(idta=ta_object.parent)
        else:
            for parent in models.ta.objects.filter(
                idta__range=(ta_object.script, ta_object.idta), child=ta_object.idta
            ):
                if parent.idta in donelijst:
                    continue
                yield parent

    donelijst = []
    teruglijst = []
    ta_object = models.ta.objects.get(idta=idta)
    trace_recurse(ta_object)
    return teruglijst


def trace_document(pquery):
    """ trace forward & backwardfrom the current step/ta_object (status SPLITUP).
        gathers confirm information
    """

    def trace_forward(ta_object):
        """ recursive. walk over ta_object's forward (to exit). """
        if ta_object.child:
            child = models.ta.objects.get(idta=ta_object.child)
        else:
            try:
                child = models.ta.objects.filter(parent=ta_object.idta)[0]
            except IndexError:
                return  # no result, return
        if child.confirmasked:
            taorg.confirmtext += "%(confirmtype)s\n" % {
                "confirmasked": child.confirmasked,
                "confirmed": child.confirmed,
                "confirmtype": child.confirmtype,
            }
            taorg.confirmidta = child.confirmidta
        if child.status == EXTERNOUT:
            taorg.outgoing = child.idta
            taorg.channel = child.tochannel
        trace_forward(child)

    def trace_back(ta_object):
        """ recursive. walk over ta_object's backward (to origin).  """
        if ta_object.parent:
            parent = models.ta.objects.get(idta=ta_object.parent)
        else:
            try:
                parent = models.ta.objects.filter(
                    idta__range=(ta_object.script, ta_object.idta), child=ta_object.idta
                )[
                    0
                ]  # just get one parent
            except IndexError:
                return  # no result, return
        if parent.confirmasked:
            taorg.confirmtext += "%(confirmtype)s\n" % {
                "confirmasked": parent.confirmasked,
                "confirmed": parent.confirmed,
                "confirmtype": parent.confirmtype,
            }
            taorg.confirmidta = parent.confirmidta
        if parent.status == EXTERNIN:
            taorg.incoming = parent.idta
            taorg.channel = parent.fromchannel
        trace_back(parent)

    # main for trace_document*****************
    for taorg in pquery.object_list:
        taorg.confirmtext = ""
        if taorg.status == SPLITUP:
            trace_back(taorg)
        else:
            trace_forward(taorg)


def gettrace(ta_object):
    """ recursive. Builds a tree of ta's (a trace) for parameter ta_object.
        children are a list in ta.
    """
    if ta_object.child:  # has a explicit child
        ta_object.talijst = [models.ta.objects.get(idta=ta_object.child)]
    else:  # search in ta_object-table who is reffering to ta_object
        ta_object.talijst = list(models.ta.objects.filter(parent=ta_object.idta))
    for child in ta_object.talijst:
        gettrace(child)


def delete_from_ta(ta_object):
    """ try to delete in ta table as much as possible.
        until a MERGE, this is easy.
        but a MERGE can contain messages from other infiles...
        in that case, just leave the MERGE
    """

    def gather_tas_before_merge(ta_object):
        """ loop over ta tree untill MERGE.
            put all ta status MERGE in one list, others in deletelist
        """
        if ta_object.status == MERGED:
            tas_merge.append(ta_object)
            return
        else:
            tas_for_deletion.append(ta_object)
        if ta_object.child:  # has a explicit child
            tmp_list = [models.ta.objects.get(idta=ta_object.child)]
        else:  # search in ta_object-table who is reffering to ta_object
            tmp_list = list(models.ta.objects.filter(parent=ta_object.idta))
        for child in tmp_list:
            gather_tas_before_merge(child)

    def gather_tas_after_merge(ta_object):
        tas_for_deletion.append(ta_object)
        if ta_object.child:  # has a explicit child
            tmp_list = [models.ta.objects.get(idta=ta_object.child)]
        else:  # search in ta_object-table who is reffering to ta_object
            tmp_list = list(models.ta.objects.filter(parent=ta_object.idta))
        for child in tmp_list:
            gather_tas_after_merge(child)

    tas_for_deletion = []
    tas_merge = []
    gather_tas_before_merge(ta_object)
    tas_merge = list(set(tas_merge))  # one MERGE only once in list
    for ta_merge in tas_merge:  # for each MERGE ta:
        # if all included files in the MERGED file are to be deleted, MERGED can be deleted
        # select all db-ta_object's included in MERGED ta_object
        for includedta in models.ta.objects.filter(
            idta__range=(ta_merge.script, ta_merge.idta), child=ta_merge.idta
        ):
            if includedta not in tas_for_deletion:
                break
        else:
            gather_tas_after_merge(ta_merge)
    for ta_object in tas_for_deletion:
        ta_object.delete()


def trace2detail(ta_object):
    def newbranche(ta_object, level=0):
        def dota(ta_object, isfirststep=False):
            levelindicator = (level) * "| "
            if isfirststep and level:
                ta_object.ind = levelindicator[:-2] + "___"
            elif ta_object.status == FILEOUT and ta_object.nrmessages > 1:
                ta_object.ind = levelindicator
            elif ta_object.status == EXTERNOUT:
                if levelindicator:
                    ta_object.ind = levelindicator[:-2] + "o=="
                else:
                    ta_object.ind = levelindicator[:-2]
            else:
                ta_object.ind = levelindicator
            # ~ ta_object.action = models.ta.objects.only('filename').get(idta=ta_object.script)
            ta_object.channel = ta_object.fromchannel
            if ta_object.tochannel:
                ta_object.channel = ta_object.tochannel
            detaillist.append(ta_object)
            lengtetalijst = len(ta_object.talijst)
            if lengtetalijst > 1:
                for child in ta_object.talijst:
                    newbranche(child, level=level + 1)
            elif lengtetalijst == 1:
                dota(ta_object.talijst[0])

        # start new level
        dota(ta_object, isfirststep=True)

    detaillist = []
    newbranche(ta_object)
    return detaillist


def datetimefrom():
    terug = datetime.datetime.today() - datetime.timedelta(
        days=botsglobal.ini.getint("settings", "maxdays", 30)
    )
    return terug.strftime("%Y-%m-%d 00:00:00")


def datetimeuntil():
    terug = datetime.datetime.today()
    return terug.strftime("%Y-%m-%d 23:59:59")


def handlepagination(requestpost, cleaned_data):
    """ use requestpost to set criteria for pagination in cleaned_data"""
    if "first" in requestpost:
        cleaned_data["page"] = 1
    elif "previous" in requestpost:
        cleaned_data["page"] = cleaned_data["page"] - 1
    elif "next" in requestpost:
        cleaned_data["page"] = cleaned_data["page"] + 1
    elif "last" in requestpost:
        cleaned_data["page"] = sys.maxsize
    elif "order" in requestpost:  # change the sorting order
        if (
            requestpost["order"] == cleaned_data["sortedby"]
        ):  # sort same row, but desc->asc etc
            cleaned_data["sortedasc"] = not cleaned_data["sortedasc"]
        else:
            cleaned_data["sortedby"] = requestpost["order"].lower()
            if cleaned_data["sortedby"] == "ts":
                cleaned_data["sortedasc"] = False
            else:
                cleaned_data["sortedasc"] = True


def getidtalastrun():
    return models.filereport.objects.all().aggregate(
        django.db.models.Max("reportidta")
    )["reportidta__max"]


def filterquery(query, org_cleaned_data, incoming=False, paginate=True):
    """ filter query using the data of the form (mostly in hidden fields).
        parameter 'paginate' controls if pagination is used or not.
    """
    cleaned_data = copy.copy(
        org_cleaned_data
    )  # copy because it it destroyed in setting up query
    page = cleaned_data.pop("page")  # do not use this in query, use in paginator
    if "dateuntil" in cleaned_data:
        query = query.filter(ts__lt=cleaned_data.pop("dateuntil"))
    if "datefrom" in cleaned_data:
        query = query.filter(ts__gte=cleaned_data.pop("datefrom"))
    if "sortedby" in cleaned_data:
        query = query.order_by(
            {True: "", False: "-"}[cleaned_data.pop("sortedasc")]
            + cleaned_data.pop("sortedby")
        )
    if "lastrun" in cleaned_data:
        if cleaned_data.pop("lastrun"):
            idtalastrun = getidtalastrun()
            if idtalastrun:  # if no result (=None): there are no filereports.
                if incoming:  # detect if incoming; do other selection
                    query = query.filter(reportidta=idtalastrun)
                else:
                    query = query.filter(idta__gt=idtalastrun)
    if "frompartner" in cleaned_data and cleaned_data["frompartner"]:
        query = frompartnerquery(query, cleaned_data.pop("frompartner"))
    if "topartner" in cleaned_data and cleaned_data["topartner"]:
        query = topartnerquery(query, cleaned_data.pop("topartner"))
    if "infilename" in cleaned_data and cleaned_data["infilename"]:
        query = query.filter(infilename__contains=cleaned_data.pop("infilename"))
    if "filename" in cleaned_data and cleaned_data["filename"]:
        query = query.filter(filename__contains=cleaned_data.pop("filename"))
    for key, value in list(cleaned_data.items()):
        if not value:
            del cleaned_data[key]
    query = query.filter(**cleaned_data)
    if paginate:
        paginator = Paginator(query, botsglobal.ini.getint("settings", "limit", 30))
        try:
            return paginator.page(page)
        except (EmptyPage, InvalidPage):  # page does not exist: use last page
            lastpage = paginator.num_pages
            org_cleaned_data["page"] = lastpage  # change value in form as well
            return paginator.page(lastpage)
    else:  # do not use paginator; return everything
        return query


def frompartnerquery(query, idpartner):
    # return the appropriate query according to partner type
    # if group: select partners in the group
    # else: select the partner
    isgroup = models.partner.objects.values_list("isgroup", flat=True).filter(
        idpartner=idpartner
    )
    if isgroup[0]:
        return query.filter(
            frompartner__in=models.partner.objects.values_list(
                "idpartner", flat=True
            ).filter(group=idpartner)
        )
    else:
        return query.filter(frompartner=idpartner)


def topartnerquery(query, idpartner):
    isgroup = models.partner.objects.values_list("isgroup", flat=True).filter(
        idpartner=idpartner
    )
    if isgroup[0]:
        return query.filter(
            topartner__in=models.partner.objects.values_list(
                "idpartner", flat=True
            ).filter(group=idpartner)
        )
    else:
        return query.filter(topartner=idpartner)


def indent_x12(content):
    if content.count("\n") > 6:
        return content
    count = 0
    for char in content[:200].lstrip():
        if char in "\r\n" and count != 105:  # pos 105: is record_sep, could be \r\n
            continue
        count += 1
        if count == 106:
            sep = char
            break
    else:
        return content
    if sep.isalnum() or sep.isspace():
        return content
    return content.replace(sep, sep + "\n")


EDIFACT_INDENT = re.compile(
    """
    (?<!\?)     #if no preceding escape (?)
    '           #apostrophe
    (?![\n\r])  #if no following CR of LF
    """,
    re.VERBOSE,
)


def indent_edifact(content):
    """ three options:
        1 is already indented (each segment on separate line)
        2 block mode: lines of fixed lengths eg 80 chars
        3 one string, one line
    """
    if content.count("\n") > 4:
        return content
    return EDIFACT_INDENT.sub("'\n", content)
