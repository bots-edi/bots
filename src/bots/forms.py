# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import django
from django.utils.translation import ugettext as _
#***********
from . import models
from . import viewlib
from . import botsglobal

HIDDENINPUT = django.forms.widgets.HiddenInput


class Select(django.forms.Form):
    datefrom = django.forms.DateTimeField(initial=viewlib.datetimefrom)
    dateuntil = django.forms.DateTimeField(initial=viewlib.datetimeuntil)
    page = django.forms.IntegerField(required=False, initial=1, widget=HIDDENINPUT())
    sortedby = django.forms.CharField(initial='ts', widget=HIDDENINPUT())
    sortedasc = django.forms.BooleanField(initial=False, required=False, widget=HIDDENINPUT())


class View(django.forms.Form):
    datefrom = django.forms.DateTimeField(required=False, initial=viewlib.datetimefrom, widget=HIDDENINPUT())
    dateuntil = django.forms.DateTimeField(required=False, initial=viewlib.datetimeuntil, widget=HIDDENINPUT())
    page = django.forms.IntegerField(required=False, initial=1, widget=HIDDENINPUT())
    sortedby = django.forms.CharField(required=False, initial='ts', widget=HIDDENINPUT())
    sortedasc = django.forms.BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectReports(Select):
    template = 'bots/selectform.html'
    action = '/reports/'
    status = django.forms.ChoiceField(choices=[models.DEFAULT_ENTRY, ('1', 'Error'), ('0', 'Done')], required=False, initial='')


class ViewReports(View):
    template = 'bots/reports.html'
    action = '/reports/'
    status = django.forms.IntegerField(required=False, initial='', widget=HIDDENINPUT())


class SelectIncoming(Select):
    template = 'bots/selectform.html'
    action = '/incoming/'
    statust = django.forms.ChoiceField(choice=[models.DEFAULT_ENTRY, ('1', 'Error'),
                                        ('3', 'Done')], required=False, initial='')
    idroute = django.forms.ChoiceField(choice=[], required=False, initial='')
    fromchannel = django.forms.ChoiceField(choice=[], required=False)
    frompartner = django.forms.ChoiceField(choice=[], required=False)
    topartner = django.forms.ChoiceField(choice=[], required=False)
    ineditype = django.forms.ChoiceField(choice=models.EDITYPESLIST, required=False)
    inmessagetype = django.forms.ChoiceField(choice=[], required=False)
    outeditype = django.forms.ChoiceField(choice=models.EDITYPESLIST, required=False)
    outmessagetype = django.forms.ChoiceField(choice=[], required=False)
    infilename = django.forms.CharField(required=False, label='Filename', max_length=70)
    lastrun = django.forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(SelectIncoming, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['inmessagetype'].choices = models.getinmessagetypes()
        self.fields['outmessagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['fromchannel'].choices = models.getfromchannels()


class ViewIncoming(View):
    template = 'bots/incoming.html'
    action = '/incoming/'
    statust = django.forms.IntegerField(required=False, initial='', widget=HIDDENINPUT())
    idroute = django.forms.CharField(required=False, widget=HIDDENINPUT())
    fromchannel = django.forms.CharField(required=False, widget=HIDDENINPUT())
    frompartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    topartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    ineditype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    inmessagetype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    outeditype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    outmessagetype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    infilename = django.forms.CharField(required=False, widget=HIDDENINPUT(), max_length=256)
    lastrun = django.forms.BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectDocument(Select):
    template = 'bots/selectform.html'
    action = '/document/'
    status = django.forms.TypedChoiceField(
        [(0, '---------'), (320, _('Document-in')), (330, _('Document-out'))], required=False, initial=0, coerce=int)
    idroute = django.forms.ChoiceField(choice=[], required=False, initial='')
    frompartner = django.forms.ChoiceField(choice=[], required=False)
    topartner = django.forms.ChoiceField(choice=[], required=False)
    editype = django.forms.ChoiceField(choice=models.EDITYPESLIST, required=False)
    messagetype = django.forms.ChoiceField(required=False)
    lastrun = django.forms.BooleanField(required=False, initial=False)
    reference = django.forms.CharField(required=False, label='Reference', max_length=70)

    def __init__(self, *args, **kwargs):
        super(SelectDocument, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()


class ViewDocument(View):
    template = 'bots/document.html'
    action = '/document/'
    status = django.forms.IntegerField(required=False, initial=0, widget=HIDDENINPUT())
    idroute = django.forms.CharField(required=False, widget=HIDDENINPUT())
    frompartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    topartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    editype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    messagetype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    lastrun = django.forms.BooleanField(required=False, initial=False, widget=HIDDENINPUT())
    reference = django.forms.CharField(required=False, widget=HIDDENINPUT())


class SelectOutgoing(Select):
    template = 'bots/selectform.html'
    action = '/outgoing/'
    statust = django.forms.ChoiceField(choice=[models.DEFAULT_ENTRY, ('1', 'Error'),
                                        ('3', 'Done'), ('4', 'Resend')], required=False, initial='')
    idroute = django.forms.ChoiceField(choice=[], required=False, initial='')
    tochannel = django.forms.ChoiceField(choice=[], required=False)
    frompartner = django.forms.ChoiceField(choice=[], required=False)
    topartner = django.forms.ChoiceField(choice=[], required=False)
    editype = django.forms.ChoiceField(choice=models.EDITYPESLIST, required=False)
    messagetype = django.forms.ChoiceField(required=False)
    filename = django.forms.CharField(required=False, label='Filename', max_length=256)
    lastrun = django.forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(SelectOutgoing, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['tochannel'].choices = models.gettochannels()


class ViewOutgoing(View):
    template = 'bots/outgoing.html'
    action = '/outgoing/'
    statust = django.forms.IntegerField(required=False, initial='', widget=HIDDENINPUT())
    idroute = django.forms.CharField(required=False, widget=HIDDENINPUT())
    tochannel = django.forms.CharField(required=False, widget=HIDDENINPUT())
    frompartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    topartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    editype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    messagetype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    filename = django.forms.CharField(required=False, widget=HIDDENINPUT())
    lastrun = django.forms.BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectProcess(Select):
    template = 'bots/selectform.html'
    action = '/process/'
    idroute = django.forms.ChoiceField(choice=[], required=False, initial='')
    lastrun = django.forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(SelectProcess, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()


class ViewProcess(View):
    template = 'bots/process.html'
    action = '/process/'
    idroute = django.forms.CharField(required=False, widget=HIDDENINPUT())
    lastrun = django.forms.BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectConfirm(Select):
    template = 'bots/selectform.html'
    action = '/confirm/'
    confirmtype = django.forms.ChoiceField(choice=models.CONFIRMTYPELIST, required=False, initial='0')
    confirmed = django.forms.ChoiceField(choice=[('0', 'All runs'), ('1', 'Current run'),
                                          ('2', 'Last run')], required=False, initial='0')
    idroute = django.forms.ChoiceField(choice=[], required=False, initial='')
    editype = django.forms.ChoiceField(choice=models.EDITYPESLIST, required=False)
    messagetype = django.forms.ChoiceField(choice=[], required=False)
    frompartner = django.forms.ChoiceField(choice=[], required=False)
    topartner = django.forms.ChoiceField(choice=[], required=False)
    fromchannel = django.forms.ChoiceField(choice=[], required=False)
    tochannel = django.forms.ChoiceField(choice=[], required=False)

    def __init__(self, *args, **kwargs):
        super(SelectConfirm, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getallmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['fromchannel'].choices = models.getfromchannels()
        self.fields['tochannel'].choices = models.gettochannels()


class ViewConfirm(View):
    template = 'bots/confirm.html'
    action = '/confirm/'
    confirmtype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    confirmed = django.forms.CharField(required=False, widget=HIDDENINPUT())
    idroute = django.forms.CharField(required=False, widget=HIDDENINPUT())
    editype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    messagetype = django.forms.CharField(required=False, widget=HIDDENINPUT())
    frompartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    topartner = django.forms.CharField(required=False, widget=HIDDENINPUT())
    fromchannel = django.forms.CharField(required=False, widget=HIDDENINPUT())
    tochannel = django.forms.CharField(required=False, widget=HIDDENINPUT())


class UploadFileForm(django.forms.Form):
    file = django.forms.FileField(label='Plugin to read', required=True,
                                  widget=django.forms.widgets.FileInput(attrs={'size': '100'}))


class PlugoutForm(django.forms.Form):
    databaseconfiguration = django.forms.BooleanField(
        required=False, initial=True, label='Database configuration', help_text='Routes, channels, translations, partners, etc. from the database.')
    umlists = django.forms.BooleanField(required=False, initial=True, label='User code lists',
                                        help_text='Your user code data from the database.')
    fileconfiguration = django.forms.BooleanField(
        required=False, initial=True, label='Script files', help_text='[bots/usersys] Grammars, mapping scrips, routes scripts, etc.')
    infiles = django.forms.BooleanField(required=False, initial=True, label='Input files',
                                        help_text='[bots/botssys/infile] Example/test edi files.')
    charset = django.forms.BooleanField(required=False, initial=False, label='Edifact character sets',
                                        help_text='[bots/usersys/charsets] Seldom needed, only if changed.')
    databasetransactions = django.forms.BooleanField(required=False, initial=False, label='Database transactions',
                                                     help_text='Transaction details of all bots runs from the database. Only for support purposes, on request. May generate a very large plugin!')
    data = django.forms.BooleanField(required=False, initial=False, label='All transaction files',
                                     help_text='[bots/botssys/data] Copies of all incoming, intermediate and outgoing files. Only for support purposes, on request. May generate a very large plugin!')
    logfiles = django.forms.BooleanField(required=False, initial=False, label='Log files',
                                         help_text='[bots/botssys/logging] Log files from engine, webserver etc. Only for support purposes, on request.')
    config = django.forms.BooleanField(required=False, initial=False, label='Configuration files',
                                       help_text='[bots/config] Your customised configuration files. Only for support purposes, on request.')
    database = django.forms.BooleanField(required=False, initial=False, label='SQLite database',
                                         help_text='[bots/botssys/sqlitedb] Entire database file. Only for support purposes, on request.')


class DeleteForm(django.forms.Form):
    delacceptance = django.forms.BooleanField(required=False, label='Delete transactions in acceptance testing',
                                              initial=True, help_text='Delete runs, reports, incoming, outgoing, data files from acceptance testing.')
    deltransactions = django.forms.BooleanField(
        required=False, label='Delete transactions', initial=True, help_text='Delete runs, reports, incoming, outgoing, data files.')
    deloutfile = django.forms.BooleanField(required=False, label='Delete botssys/outfiles',
                                           initial=False, help_text='Delete files in botssys/outfile.')
    delcodelists = django.forms.BooleanField(
        required=False, label='Delete user code lists', initial=False, help_text='Delete user code lists.')
    deluserscripts = django.forms.BooleanField(required=False, label='Delete all user scripts', initial=False,
                                               help_text='Delete all scripts in usersys (grammars, mappings etc) except charsets.')
    delinfile = django.forms.BooleanField(required=False, label='Delete botssys/infiles',
                                          initial=False, help_text='Delete files in botssys/infile.')
    delconfiguration = django.forms.BooleanField(
        required=False, label='Delete configuration', initial=False, help_text='Delete routes, channels, translations, partners etc.')
    delpersist = django.forms.BooleanField(required=False, label='Delete persist',
                                           initial=False, help_text='Delete the persist information.')
