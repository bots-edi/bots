# -*- coding: utf-8 -*-



import sys
if sys.version_info[0] > 2:
    str = str = str
import os
import time
import shutil
import subprocess
import traceback
import socket
import django
from django.utils.translation import ugettext as _
from django.contrib import messages
from . import forms
from . import models
from . import viewlib
from . import botslib
from . import pluglib
from . import botsglobal
from . import py2html
from .botsconfig import *


def server_error(request, template_name='500.html'):
    ''' the 500 error handler.
        Templates: `500.html`
        Context: None
    '''
    exc_info = traceback.format_exc(None)
    botsglobal.logger.info(_('Ran into server error: "%(error)s"'), {'error': exc_info})
    temp = django.template.loader.get_template(template_name)  # You need to create a 500.html template.
    return django.http.HttpResponseServerError(temp.render(django.template.Context({'exc_info': exc_info})))


def index(request, *kw, **kwargs):
    ''' when using eg http://localhost:8080
        index can be reached without being logged in.
        most of the time user is redirected to '/home'
    '''
    return django.shortcuts.render(request, 'admin/base.html')


def home(request, *kw, **kwargs):
    return django.shortcuts.render(request, 'bots/about.html', {'botsinfo': botslib.botsinfo()})


def reports(request, *kw, **kwargs):
    if request.method == 'GET':
        if 'select' in request.GET:  # from menu:select->reports
            form = forms.SelectReports()
            return django.shortcuts.render(request, form.template, {'form': form})  # go to the SelectReports form
        else:  # from menu:run->report
            # go to default report-query using these default parameters
            cleaned_data = {'page': 1, 'sortedby': 'idta', 'sortedasc': False}
    else:  # request.method == 'POST'
        if 'fromselect' in request.POST:  # from SelectReports form
            formin = forms.SelectReports(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            #go to default report-query using parameters from select screen
        elif 'report2incoming' in request.POST:  # from ViewReports form using star view incoming
            request.POST = viewlib.preparereport2view(request.POST, viewlib.safe_int(request.POST['report2incoming']))
            return incoming(request)
        elif 'report2outgoing' in request.POST:  # from ViewReports form using star view outgoing
            request.POST = viewlib.preparereport2view(request.POST, viewlib.safe_int(request.POST['report2outgoing']))
            return outgoing(request)
        elif 'report2process' in request.POST:  # from ViewReports form using star view process errors
            request.POST = viewlib.preparereport2view(request.POST, viewlib.safe_int(request.POST['report2process']))
            return process(request)
        elif 'report2errors' in request.POST:  # from ViewReports form using star file errors
            newpost = viewlib.preparereport2view(request.POST, viewlib.safe_int(request.POST['report2errors']))
            newpost['statust'] = ERROR
            request.POST = newpost
            return incoming(request)
        elif 'report2commerrors' in request.POST:  # from ViewReports form using star communcation errors
            newpost = viewlib.preparereport2view(request.POST, viewlib.safe_int(request.POST['report2commerrors']))
            newpost['statust'] = ERROR
            request.POST = newpost
            return outgoing(request)
        else:  # from ViewReports form
            formin = forms.ViewReports(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            elif '2select' in request.POST:  # from ViewReports form using button change selection
                form = forms.SelectReports(formin.cleaned_data)
                return django.shortcuts.render(request, form.template, {'form': form})
            else:  # from ViewReports, next page etc
                viewlib.handlepagination(request.POST, formin.cleaned_data)
        cleaned_data = formin.cleaned_data
    #normal report-query with parameters
    query = models.report.objects.all()
    pquery = viewlib.filterquery(query, cleaned_data)
    form = forms.ViewReports(initial=cleaned_data)
    return django.shortcuts.render(request, form.template, {'form': form, 'queryset': pquery})


def incoming(request, *kw, **kwargs):
    if request.method == 'GET':
        if 'select' in request.GET:  # from menu:select->incoming
            form = forms.SelectIncoming()
            return django.shortcuts.render(request, form.template, {'form': form})  # go to the SelectIncoming form
        else:  # from menu:run->incoming
            #~ print('XXXXXX1',repr(request.GET))
            lastrun = bool(viewlib.safe_int(request.GET.get('lastrun', 0)))
            idroute = request.GET.get('idroute')
            cleaned_data = {'page': 1, 'sortedby': 'idta', 'sortedasc': False, 'lastrun': lastrun,
                            'idroute': idroute}  # go to default incoming-query using these default parameters
    else:  # request.method == 'POST'
        print('XXXXXX2')
        if 'fromselect' in request.POST:  # from SelectIncoming form
            formin = forms.SelectIncoming(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            #go to default report-query using parameters from select screen
        elif '2outgoing' in request.POST:  # from ViewIncoming form, using button 'outgoing (same selection)'
            request.POST = viewlib.changepostparameters(request.POST, soort='in2out')
            return outgoing(request)
        elif '2process' in request.POST:  # from ViewIncoming form, using button 'process errors (same selection)'
            request.POST = viewlib.changepostparameters(request.POST, soort='2process')
            return process(request)
        elif '2confirm' in request.POST:  # from ViewIncoming form, using button 'confirm (same selection)'
            request.POST = viewlib.changepostparameters(request.POST, soort='in2confirm')
            return confirm(request)
        else:  # from ViewIncoming form, check this form first
            formin = forms.ViewIncoming(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            elif '2select' in request.POST:  # from ViewIncoming form using button change selection
                form = forms.SelectIncoming(formin.cleaned_data)
                return django.shortcuts.render(request, form.template, {'form': form})
            elif 'delete' in request.POST:  # from ViewIncoming form using star delete
                if request.user.is_staff or request.user.is_superuser:
                    idta = viewlib.safe_int(request.POST['delete'])
                    #delete from filereport
                    models.filereport.objects.filter(idta=idta).delete()
                    #get ta_object
                    ta_object = models.ta.objects.get(idta=idta)
                    #delete as much as possible in ta table
                    viewlib.delete_from_ta(ta_object)
                else:
                    notification = _('No rights for this operation.')
                    botsglobal.logger.info(notification)
                    messages.add_message(request, messages.INFO, notification)
            elif 'retransmit' in request.POST:  # from ViewIncoming form using star rereceive
                idta = request.POST['retransmit']
                filereport = models.filereport.objects.get(idta=viewlib.safe_int(idta))
                if filereport.fromchannel:  # for resend files fromchannel has no value. (do not rereceive resend items)
                    filereport.retransmit = not filereport.retransmit
                    filereport.save()
            elif 'rereceiveall' in request.POST:  # from ViewIncoming form using button 'rereceive all'
                #select all objects with parameters and set retransmit
                query = models.filereport.objects.all()
                incomingfiles = viewlib.filterquery(query, formin.cleaned_data, paginate=False)
                # for resend files fromchannel has no value. (do not rereceive resend items)
                for incomingfile in incomingfiles:
                    if incomingfile.fromchannel:
                        incomingfile.retransmit = not incomingfile.retransmit
                        incomingfile.save()
            else:  # from ViewIncoming, next page etc
                viewlib.handlepagination(request.POST, formin.cleaned_data)
        cleaned_data = formin.cleaned_data
    #normal incoming-query with parameters
    query = models.filereport.objects.all()
    pquery = viewlib.filterquery(query, cleaned_data, incoming=True)
    form = forms.ViewIncoming(initial=cleaned_data)
    return django.shortcuts.render(request, form.template, {'form': form, 'queryset': pquery})


def outgoing(request, *kw, **kwargs):
    if request.method == 'GET':
        if 'select' in request.GET:  # from menu:select->outgoing
            form = forms.SelectOutgoing()
            return django.shortcuts.render(request, form.template, {'form': form})
        else:  # from menu:run->outgoing
            cleaned_data = {'page': 1, 'sortedby': 'idta', 'sortedasc': False, 'lastrun': bool(viewlib.safe_int(
                request.GET.get('lastrun', 0)))}  # go to default outgoing-query using these default parameters
    else:  # request.method == 'POST'
        if 'fromselect' in request.POST:  # from SelectOutgoing form
            formin = forms.SelectOutgoing(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            #go to default outgoing-query using parameters from select screen
        elif '2incoming' in request.POST:  # from ViewOutgoing form, using button 'incoming (same selection)'
            request.POST = viewlib.changepostparameters(request.POST, soort='out2in')
            return incoming(request)
        elif '2process' in request.POST:  # from ViewOutgoing form, using button 'process errors (same selection)'
            request.POST = viewlib.changepostparameters(request.POST, soort='2process')
            return process(request)
        elif '2confirm' in request.POST:  # from ViewOutgoing form, using button 'confirm (same selection)'
            request.POST = viewlib.changepostparameters(request.POST, soort='out2confirm')
            return confirm(request)
        else:  # from ViewOutgoing form, check this form first
            formin = forms.ViewOutgoing(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            elif '2select' in request.POST:  # from ViewOutgoing form using button change selection
                form = forms.SelectOutgoing(formin.cleaned_data)
                return django.shortcuts.render(request, form.template, {'form': form})
            elif 'retransmit' in request.POST:  # from ViewOutgoing form using star resend
                ta_object = models.ta.objects.get(idta=viewlib.safe_int(request.POST['retransmit']))
                if ta_object.statust != RESEND:  # can only resend last file
                    ta_object.retransmit = not ta_object.retransmit
                    ta_object.save()
            elif 'resendall' in request.POST:  # from ViewOutgoing form using button 'resend all'
                #select all objects with parameters and set retransmit
                query = models.ta.objects.filter(status=EXTERNOUT)
                outgoingfiles = viewlib.filterquery(query, formin.cleaned_data, paginate=False)
                for outgoingfile in outgoingfiles:  # can only resend last file
                    if outgoingfile.statust != RESEND:
                        outgoingfile.retransmit = not outgoingfile.retransmit
                        outgoingfile.save()
            elif 'noautomaticretry' in request.POST:  # from ViewOutgoing form using star 'no automaticretry'
                ta_object = models.ta.objects.get(idta=viewlib.safe_int(request.POST['noautomaticretry']))
                if ta_object.statust == ERROR:
                    ta_object.statust = NO_RETRY
                    ta_object.save()
            else:  # from ViewIncoming, next page etc
                viewlib.handlepagination(request.POST, formin.cleaned_data)
        cleaned_data = formin.cleaned_data
    #normal outgoing-query with parameters
    query = models.ta.objects.filter(status=EXTERNOUT)
    pquery = viewlib.filterquery(query, cleaned_data)
    form = forms.ViewOutgoing(initial=cleaned_data)
    return django.shortcuts.render(request, form.template, {'form': form, 'queryset': pquery})


def document(request, *kw, **kwargs):
    if request.method == 'GET':
        if 'select' in request.GET:  # from menu:select->document
            form = forms.SelectDocument()
            return django.shortcuts.render(request, form.template, {'form': form})
        else:  # from menu:run->document
            cleaned_data = {'page': 1, 'sortedby': 'idta', 'sortedasc': False}
            cleaned_data['lastrun'] = bool(viewlib.safe_int(request.GET.get('lastrun', 0)))
            cleaned_data['status'] = viewlib.safe_int(request.GET.get('status', 0))
            #go to default document-query using these default parameters
    else:  # request.method == 'POST'
        if 'fromselect' in request.POST:  # from SelectDocument form
            formin = forms.SelectDocument(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            #go to default document-query using parameters from select screen
        else:
            formin = forms.ViewDocument(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            elif '2select' in request.POST:  # coming from ViewDocument, change the selection criteria, go to select form
                form = forms.SelectDocument(formin.cleaned_data)
                return django.shortcuts.render(request, form.template, {'form': form})
            elif 'retransmit' in request.POST:  # coming from ViewDocument, no reportidta
                idta = request.POST['retransmit']
                filereport = models.filereport.objects.get(idta=viewlib.safe_int(idta))
                filereport.retransmit = not filereport.retransmit
                filereport.save()
            else:  # coming from ViewDocument, next page etc
                viewlib.handlepagination(request.POST, formin.cleaned_data)
        cleaned_data = formin.cleaned_data
    #normal document-query with parameters
    query = models.ta.objects.filter(django.db.models.Q(status=SPLITUP) | django.db.models.Q(status=TRANSLATED))
    pquery = viewlib.filterquery(query, cleaned_data)
    viewlib.trace_document(pquery)
    form = forms.ViewDocument(initial=cleaned_data)
    return django.shortcuts.render(request, form.template, {'form': form, 'queryset': pquery})


def process(request, *kw, **kwargs):
    if request.method == 'GET':
        if 'select' in request.GET:  # from menu:select->process
            form = forms.SelectProcess()
            return django.shortcuts.render(request, form.template, {'form': form})
        else:  # from menu:run->process
            cleaned_data = {'page': 1, 'sortedby': 'idta', 'sortedasc': False,
                            'lastrun': bool(viewlib.safe_int(request.GET.get('lastrun', 0)))}
            #go to default process-query using these default parameters
    else:  # request.method == 'POST'
        if 'fromselect' in request.POST:  # from SelectProcess form
            formin = forms.SelectProcess(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
        elif '2incoming' in request.POST:  # coming from ViewProcess, go to incoming form using same criteria
            request.POST = viewlib.changepostparameters(request.POST, soort='fromprocess')
            return incoming(request)
        elif '2outgoing' in request.POST:  # coming from ViewProcess, go to outgoing form using same criteria
            request.POST = viewlib.changepostparameters(request.POST, soort='fromprocess')
            return outgoing(request)
        else:
            formin = forms.ViewProcess(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            elif '2select' in request.POST:  # coming from ViewProcess, change the selection criteria, go to select form
                form = forms.SelectProcess(formin.cleaned_data)
                return django.shortcuts.render(request, form.template, {'form': form})
            else:  # coming from ViewProcess
                viewlib.handlepagination(request.POST, formin.cleaned_data)
        cleaned_data = formin.cleaned_data
    #normal process-query with parameters
    query = models.ta.objects.filter(status=PROCESS, statust=ERROR)
    pquery = viewlib.filterquery(query, cleaned_data)
    form = forms.ViewProcess(initial=cleaned_data)
    return django.shortcuts.render(request, form.template, {'form': form, 'queryset': pquery})


def detail(request, *kw, **kwargs):
    ''' in: the idta, either as parameter in or out.
        in: is idta of incoming file.
        out: idta of outgoing file, need to trace back for incoming file.
        return list of ta's for display in detail template.
        This list is formatted and ordered for display.
        first, get a tree (trace) starting with the incoming ta ;
        than make up the details for the trace
    '''
    if request.method == 'GET':
        if 'inidta' in request.GET:  # from incoming screen
            rootta = models.ta.objects.get(idta=viewlib.safe_int(request.GET['inidta']))
        else:  # from outgoing screen: trace back to EXTERNIN first
            rootta = viewlib.django_trace_origin(viewlib.safe_int(request.GET['outidta']), {'status': EXTERNIN})[0]
        viewlib.gettrace(rootta)
        detaillist = viewlib.trace2detail(rootta)
        return django.shortcuts.render(request, 'bots/detail.html', {'detaillist': detaillist, 'rootta': rootta})


def confirm(request, *kw, **kwargs):
    if request.method == 'GET':
        if 'select' in request.GET:  # from menu:select->confirm
            form = forms.SelectConfirm()
            return django.shortcuts.render(request, form.template, {'form': form})
        else:  # from menu:run->confirm
            cleaned_data = {'page': 1, 'sortedby': 'idta', 'sortedasc': False}
            #go to default confirm-query using these default parameters
    else:  # request.method == 'POST'
        if 'fromselect' in request.POST:  # from SelectConfirm form
            formin = forms.SelectConfirm(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
        elif '2incoming' in request.POST:  # coming from ViewConfirm, go to incoming form using same criteria
            request.POST = viewlib.changepostparameters(request.POST, soort='confirm2in')
            return incoming(request)
        elif '2outgoing' in request.POST:  # coming from ViewConfirm, go to outgoing form using same criteria
            request.POST = viewlib.changepostparameters(request.POST, soort='confirm2out')
            return outgoing(request)
        elif 'confirm' in request.POST:  # coming ViewConfirm, using star 'Manual confirm'
            ta_object = models.ta.objects.get(idta=viewlib.safe_int(request.POST['confirm']))
            if ta_object.confirmed == False and ta_object.confirmtype.startswith('ask'):
                ta_object.confirmed = True
                ta_object.confirmidta = '-1'   # to indicate a manual confirmation
                ta_object.save()
                messages.add_message(request, messages.INFO, _('Manual confirmed.'))
            else:
                messages.add_message(request, messages.INFO, _('Manual confirm not possible.'))
            # then just refresh the current view
            formin = forms.ViewConfirm(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
        else:
            formin = forms.ViewConfirm(request.POST)
            if not formin.is_valid():
                return django.shortcuts.render(request, formin.template, {'form': formin})
            elif '2select' in request.POST:  # coming from ViewConfirm, change the selection criteria, go to select form
                form = forms.SelectConfirm(formin.cleaned_data)
                return django.shortcuts.render(request, form.template, {'form': form})
            else:  # coming from ViewConfirm, next page etc
                viewlib.handlepagination(request.POST, formin.cleaned_data)
        cleaned_data = formin.cleaned_data
    #normal confirm-query with parameters
    query = models.ta.objects.filter(confirmasked=True)
    pquery = viewlib.filterquery(query, cleaned_data)
    form = forms.ViewConfirm(initial=cleaned_data)
    return django.shortcuts.render(request, form.template, {'form': form, 'queryset': pquery})


def filer(request, *kw, **kwargs):
    ''' handles bots file viewer. Only files in data dir of Bots are displayed.'''
    if request.method == 'GET':
        try:
            idta = request.GET['idta']
            if idta == 0:  # for the 'starred' file names (eg multiple output)
                raise Exception('to be caught')

            currentta = list(models.ta.objects.filter(idta=idta))[0]
            if request.GET['action'] == 'downl':
                response = django.http.HttpResponse(content_type=currentta.contenttype)
                if currentta.contenttype == 'text/html':
                    dispositiontype = 'inline'
                else:
                    dispositiontype = 'attachment'
                response['Content-Disposition'] = dispositiontype + '; filename=' + currentta.filename + '.txt'
                #~ response['Content-Length'] = os.path.getsize(absfilename)
                response.write(botslib.readdata_bin(currentta.filename))
                return response
            elif request.GET['action'] == 'previous':
                if currentta.parent:  # has a explicit parent
                    talijst = list(models.ta.objects.filter(idta=currentta.parent))
                else:  # get list of ta's referring to this idta as child
                    talijst = list(models.ta.objects.filter(idta__range=(
                        currentta.script, currentta.idta), child=currentta.idta))
            elif request.GET['action'] == 'this':
                if currentta.status == EXTERNIN:  # EXTERNIN can not be displayed, so go to first FILEIN
                    talijst = list(models.ta.objects.filter(parent=currentta.idta))
                elif currentta.status == EXTERNOUT:  # EXTERNOUT can not be displayed, so go to last FILEOUT
                    talijst = list(models.ta.objects.filter(idta=currentta.parent))
                else:
                    talijst = [currentta]
            elif request.GET['action'] == 'next':
                if currentta.child:  # has a explicit child
                    talijst = list(models.ta.objects.filter(idta=currentta.child))
                else:
                    talijst = list(models.ta.objects.filter(parent=currentta.idta))
            for ta_object in talijst:
                #determine if can display file
                if ta_object.filename and ta_object.filename.isdigit():
                    if ta_object.charset:
                        ta_object.content = botslib.readdata(
                            ta_object.filename, charset=ta_object.charset, errors='ignore')
                    # guess safe choice for charset. alt1: get charset by looking forward
                    # (until translation). alt2:try with utf-8, if error iso-8859-1
                    else:
                        ta_object.content = botslib.readdata(ta_object.filename, charset='us-ascii', errors='ignore')
                    ta_object.has_file = True
                    if ta_object.editype == 'x12':
                        ta_object.content = viewlib.indent_x12(ta_object.content)
                    elif ta_object.editype == 'edifact':
                        ta_object.content = viewlib.indent_edifact(ta_object.content)
                else:
                    ta_object.has_file = False
                    ta_object.content = _('No file available for display.')
                #determine has previous:
                if ta_object.parent or ta_object.status == MERGED:
                    ta_object.has_previous = True
                else:
                    ta_object.has_previous = False
                #determine: has next:
                if ta_object.status == EXTERNOUT or ta_object.statust in [OPEN, ERROR]:
                    ta_object.has_next = False
                else:
                    ta_object.has_next = True
            return django.shortcuts.render(request, 'bots/filer.html', {'idtas': talijst})
        except:
            return django.shortcuts.render(request, 'bots/filer.html', {'error_content': _('No such file.')})


def srcfiler(request, *kw, **kwargs):
    ''' handles bots source file viewer. display grammar, mapping, userscript etc.'''
    if request.method == 'GET':
        try:
            src = request.GET['src']
            if botsglobal.ini.get('directories', 'usersys') in src and src.endswith('.py'):  # only python source in usersys!

                with open(src) as f:
                    source = f.read()
                classified_text = py2html.analyze_python(source)
                html_source = py2html.html_highlight(classified_text)
                return django.shortcuts.render(request, 'bots/srcfiler.html', {'src': src, 'html_source': html_source})
            else:
                return django.shortcuts.render(request, 'bots/srcfiler.html', {'error_content': _('File %s not allowed.' % src)})
        except:
            return django.shortcuts.render(request, 'bots/srcfiler.html', {'error_content': _('No such file.')})


def logfiler(request, *kw, **kwargs):
    ''' handles bots log file viewer. display/download any file in logging directory.
    '''
    if request.method == 'GET':
        if 'log' in request.GET:
            log = request.GET['log']
        else:
            log = 'engine.log'
        logpath = botslib.join(botsglobal.ini.get('directories', 'botssys'), 'logging')
        logf = botslib.join(logpath, log)
        try:
            with open(logf) as f:
                logdata = f.read()
        except:
            logdata = _('No such file %s' % logf)

        if 'action' in request.GET and request.GET['action'] == 'download':
            response = django.http.HttpResponse(content_type='text/log')
            response['Content-Disposition'] = 'attachment; filename=' + log
            response.write(logdata)
            return response
        else:
            logfiles = sorted(os.listdir(logpath), key=lambda s: s.lower())
            return django.shortcuts.render(request, 'bots/logfiler.html', {'log': log, 'logdata': logdata, 'logfiles': logfiles})


def plugin(request, *kw, **kwargs):
    if request.method == 'GET':
        form = forms.UploadFileForm()
        return django.shortcuts.render(request, 'bots/plugin.html', {'form': form})
    else:
        if 'submit' in request.POST:  # coming from ViewIncoming, go to outgoing form using same criteria
            form = forms.UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                #write backup plugin first
                plugout_backup_core(request, *kw, **kwargs)
                #read the plugin
                try:
                    if pluglib.read_plugin(request.FILES['file'].temporary_file_path()):
                        messages.add_message(request, messages.INFO, _('Overwritten existing files.'))
                except Exception as msg:
                    notification = _('Error reading plugin: "%s".') % str(msg)
                    botsglobal.logger.error(notification)
                    messages.add_message(request, messages.INFO, notification)
                else:
                    notification = _('Plugin "%s" is read successful.') % request.FILES['file'].name
                    botsglobal.logger.info(notification)
                    messages.add_message(request, messages.INFO, notification)
                finally:
                    request.FILES['file'].close()  # seems to be needed according to django docs.
            else:
                messages.add_message(request, messages.INFO, _('No plugin read.'))
        return django.shortcuts.redirect('/home')


def plugin_index(request, *kw, **kwargs):
    if request.method == 'GET':
        return django.shortcuts.render(request, 'bots/plugin_index.html')
    else:
        if 'submit' in request.POST:  # coming from ViewIncoming, go to outgoing form using same criteria
            #write backup plugin first
            plugout_backup_core(request, *kw, **kwargs)
            #read the plugin
            try:
                pluglib.read_index('index')
            except Exception as msg:
                notification = _('Error reading configuration index file: "%s".') % str(msg)
                botsglobal.logger.error(notification)
                messages.add_message(request, messages.INFO, notification)
            else:
                notification = _('Configuration index file is read successful.')
                botsglobal.logger.info(notification)
                messages.add_message(request, messages.INFO, notification)
        return django.shortcuts.redirect('/home')


def plugout_index(request, *kw, **kwargs):
    if request.method == 'GET':
        filename = botslib.join(botsglobal.ini.get('directories', 'usersysabs'), 'index.py')
        botsglobal.logger.info(_('Start writing configuration index file "%(file)s".'), {'file': filename})
        try:
            dummy_for_cleaned_data = {'databaseconfiguration': True, 'umlists': botsglobal.ini.getboolean(
                'settings', 'codelists_in_plugin', True), 'databasetransactions': False}
            pluglib.make_index(dummy_for_cleaned_data, filename)
        except Exception as msg:
            notification = _('Error writing configuration index file: "%s".') % str(msg)
            botsglobal.logger.error(notification)
            messages.add_message(request, messages.INFO, notification)
        else:
            notification = _('Configuration index file "%s" is written successful.') % filename
            botsglobal.logger.info(notification)
            messages.add_message(request, messages.INFO, notification)
        return django.shortcuts.redirect('/home')


def plugout_backup(request, *kw, **kwargs):
    if request.method == 'GET':
        plugout_backup_core(request, *kw, **kwargs)
    return django.shortcuts.redirect('/home')


def plugout_backup_core(request, *kw, **kwargs):
    filename = botslib.join(botsglobal.ini.get('directories', 'botssys'),
                            'backup_plugin_%s.zip' % time.strftime('%Y%m%d%H%M%S'))
    botsglobal.logger.info(_('Start writing backup plugin "%(file)s".'), {'file': filename})
    try:
        dummy_for_cleaned_data = {'databaseconfiguration': True,
                                  'umlists': botsglobal.ini.getboolean('settings', 'codelists_in_plugin', True),
                                  'fileconfiguration': True,
                                  'infiles': False,
                                  'charset': True,
                                  'databasetransactions': False,
                                  'data': False,
                                  'logfiles': False,
                                  'config': False,
                                  'database': False,
                                  }
        pluglib.make_plugin(dummy_for_cleaned_data, filename)
    except Exception as msg:
        notification = 'Error writing backup plugin: "%s".' % str(msg)
        botsglobal.logger.error(notification)
        messages.add_message(request, messages.INFO, notification)
    else:
        notification = _('Backup plugin "%s" is written successful.') % filename
        botsglobal.logger.info(notification)
        messages.add_message(request, messages.INFO, notification)


def plugout(request, *kw, **kwargs):
    if request.method == 'GET':
        form = forms.PlugoutForm()
        return django.shortcuts.render(request, 'bots/plugout.html', {'form': form})
    else:
        if 'submit' in request.POST:
            form = forms.PlugoutForm(request.POST)
            if form.is_valid():
                filename = botslib.join(botsglobal.ini.get('directories', 'botssys'), 'plugin_temp.zip')
                botsglobal.logger.info(_('Start writing plugin "%(file)s".'), {'file': filename})
                try:
                    pluglib.make_plugin(form.cleaned_data, filename)
                except botslib.PluginError as msg:
                    botsglobal.logger.error(str(msg))
                    messages.add_message(request, messages.INFO, str(msg))
                else:
                    botsglobal.logger.info(_('Plugin "%(file)s" created successful.'), {'file': filename})
                    response = django.http.HttpResponse(open(filename, 'rb').read(), content_type='application/zip')
                    # response['Content-Length'] = os.path.getsize(filename)
                    response['Content-Disposition'] = 'attachment; filename=' + \
                        'plugin' + time.strftime('_%Y%m%d') + '.zip'
                    return response
    return django.shortcuts.redirect('/home')


def delete(request, *kw, **kwargs):
    if request.method == 'GET':
        form = forms.DeleteForm()
        return django.shortcuts.render(request, 'bots/delete.html', {'form': form})
    else:
        if 'submit' in request.POST:
            form = forms.DeleteForm(request.POST)
            if form.is_valid():
                from django.db import connection, transaction
                if form.cleaned_data['delconfiguration'] or form.cleaned_data['delcodelists'] or form.cleaned_data['deluserscripts']:
                    #write backup plugin first
                    plugout_backup_core(request, *kw, **kwargs)
                botsglobal.logger.info(_('Start deleting in configuration.'))
                if form.cleaned_data['deltransactions']:
                    #while testing with very big loads, deleting gave error. Using raw SQL solved this.
                    cursor = connection.cursor()
                    cursor.execute('''DELETE FROM ta''')
                    cursor.execute('''DELETE FROM filereport''')
                    cursor.execute('''DELETE FROM report''')
                    transaction.commit_unless_managed()
                    messages.add_message(request, messages.INFO, _('Transactions are deleted.'))
                    botsglobal.logger.info(_('Transactions are deleted.'))
                    #clean data files
                    deletefrompath = botsglobal.ini.get('directories', 'data', 'botssys/data')
                    shutil.rmtree(deletefrompath, ignore_errors=True)
                    botslib.dirshouldbethere(deletefrompath)
                    notification = _('Data files are deleted.')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                elif form.cleaned_data['delacceptance']:
                    from django.db.models import Min
                    list_file = []  # list of files for deletion in data-directory
                    report_idta_lowest = 0
                    # for each acceptance report. is not very efficient.
                    for acc_report in models.report.objects.filter(acceptance=1):
                        if not report_idta_lowest:
                            report_idta_lowest = acc_report.idta
                        # select 'next' report...
                        max_report_idta = models.report.objects.filter(
                            idta__gt=acc_report.idta).aggregate(Min('idta'))['idta__min']
                        if not max_report_idta:  # if report is report of last run, there is no next report
                            max_report_idta = sys.maxsize
                        # we have a idta-range now: from (and including) acc_report.idta till (and
                        # excluding) max_report_idta
                        list_file += models.ta.objects.filter(idta__gte=acc_report.idta, idta__lt=max_report_idta).exclude(
                            status=1).values_list('filename', flat=True).distinct()
                        models.ta.objects.filter(idta__gte=acc_report.idta,
                                                 idta__lt=max_report_idta).delete()  # delete ta in range
                        models.filereport.objects.filter(
                            idta__gte=acc_report.idta, idta__lt=max_report_idta).delete()  # delete filereports in range
                    if report_idta_lowest:
                        models.report.objects.filter(idta__gte=report_idta_lowest,
                                                     acceptance=1).delete()  # delete all acceptance reports
                        for filename in list_file:  # delete all files in data directory geenrated during acceptance testing
                            if filename.isdigit():
                                botslib.deldata(filename)
                    notification = _('Transactions from acceptance-testing deleted.')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                if form.cleaned_data['delconfiguration']:
                    models.confirmrule.objects.all().delete()
                    models.routes.objects.all().delete()
                    models.channel.objects.all().delete()
                    models.chanpar.objects.all().delete()
                    models.translate.objects.all().delete()
                    models.partner.objects.all().delete()
                    notification = _('Database configuration is deleted.')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                if form.cleaned_data['delcodelists']:
                    #while testing with very big loads, deleting gave error. Using raw SQL solved this.
                    cursor = connection.cursor()
                    cursor.execute('''DELETE FROM ccode''')
                    cursor.execute('''DELETE FROM ccodetrigger''')
                    transaction.commit_unless_managed()
                    notification = _('User code lists are deleted.')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                if form.cleaned_data['delpersist']:
                    cursor = connection.cursor()
                    cursor.execute('''DELETE FROM persist''')
                    transaction.commit_unless_managed()
                    notification = _('Persist data is deleted.')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                if form.cleaned_data['delinfile']:
                    deletefrompath = botslib.join(botsglobal.ini.get('directories', 'botssys', 'botssys'), 'infile')
                    shutil.rmtree(deletefrompath, ignore_errors=True)
                    notification = _('Files in botssys/infile are deleted.')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                if form.cleaned_data['deloutfile']:
                    deletefrompath = botslib.join(botsglobal.ini.get('directories', 'botssys', 'botssys'), 'outfile')
                    shutil.rmtree(deletefrompath, ignore_errors=True)
                    notification = _('Files in botssys/outfile are deleted.')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                if form.cleaned_data['deluserscripts']:
                    deletefrompath = botsglobal.ini.get('directories', 'usersysabs')
                    for root, dirs, files in os.walk(deletefrompath):
                        head, tail = os.path.split(root)
                        if tail == 'charsets':
                            del dirs[:]
                            continue
                        for bestand in files:
                            if bestand != '__init__.py':
                                os.remove(os.path.join(root, bestand))
                    notification = _('User scripts are deleted (in usersys).')
                    messages.add_message(request, messages.INFO, notification)
                    botsglobal.logger.info(notification)
                botsglobal.logger.info(_('Finished deleting in configuration.'))
    return django.shortcuts.redirect('/home')


def runengine(request, *kw, **kwargs):
    if request.method == 'GET':
        #needed to find out right arguments:
        # 1. python_executable_path. Problem in virtualenv. Use setting in bots.ini if there
        # 2. botsengine_path. Problem in apache. Use setting in bots.ini if there
        # 3. environment (config). OK
        # 4. commandstorun (eg --new) and routes. OK
        python_executable_path = botsglobal.ini.get('settings', 'python_executable_path', sys.executable)
        botsengine_path = botsglobal.ini.get('settings', 'botsengine_path', os.path.join(
            os.path.dirname(os.path.abspath(sys.argv[0])), 'bots-engine.py'))
        environment = '-c' + botsglobal.ini.get('directories', 'config_org')
        lijst = [python_executable_path, botsengine_path, environment]
        # get 4. commandstorun (eg --new) and routes via request
        if 'clparameter' in request.GET:
            lijst.append(request.GET['clparameter'])

        #either bots-engine is run directly or via jobqueue-server:
        # run bots-engine via jobqueue-server; reports back if job is queued
        if botsglobal.ini.getboolean('jobqueue', 'enabled', False):
            from . import job2queue
            terug = job2queue.send_job_to_jobqueue(lijst)
            messages.add_message(request, messages.INFO, job2queue.JOBQUEUEMESSAGE2TXT[terug])
            botsglobal.logger.info(job2queue.JOBQUEUEMESSAGE2TXT[terug])
        else:  # run bots-engine direct.; reports back if bots-engien is started succesful. **not reported: problems with running.
            botsglobal.logger.info(_('Run bots-engine with parameters: "%(parameters)s"'),
                                   {'parameters': str(lijst)})
            #first check if another instance of bots-engine is running/if port is free
            try:
                engine_socket = botslib.check_if_other_engine_is_running()
            except socket.error:
                notification = _(
                    'Trying to run "bots-engine", but another instance of "bots-engine" is running. Please try again later.')
                messages.add_message(request, messages.INFO, notification)
                botsglobal.logger.info(notification)
                return django.shortcuts.redirect('/home')
            else:
                engine_socket.close()  # and close the socket
            #run engine
            try:
                terug = subprocess.Popen(lijst).pid
            except Exception as msg:
                notification = _('Errors while trying to run bots-engine: "%s".') % msg
                messages.add_message(request, messages.INFO, notification)
                botsglobal.logger.info(notification)
            else:
                messages.add_message(request, messages.INFO, _('Bots-engine is started.'))
    return django.shortcuts.redirect('/home')


def sendtestmailmanagers(request, *kw, **kwargs):
    try:
        sendornot = botsglobal.ini.getboolean('settings', 'sendreportiferror', False)
    except botslib.BotsError:
        sendornot = False
    if not sendornot:
        notification = _(
            'Trying to send test mail, but in bots.ini, section [settings], "sendreportiferror" is not "True".')
        botsglobal.logger.info(notification)
        messages.add_message(request, messages.INFO, notification)
        return django.shortcuts.redirect('/home')

    from django.core.mail import mail_managers
    try:
        mail_managers(_('testsubject'), _('test content of report'))
    except:
        txt = botslib.txtexc()
        messages.add_message(request, messages.INFO, _('Sending test mail failed.'))
        botsglobal.logger.info(_('Sending test mail failed, error:\n%(txt)s'), {'txt': txt})
        return django.shortcuts.redirect('/home')
    notification = _('Sending test mail succeeded.')
    messages.add_message(request, messages.INFO, notification)
    botsglobal.logger.info(notification)
    return django.shortcuts.redirect('/home')
