from __future__ import unicode_literals
from __future__ import print_function
import sys
if sys.version_info[0] > 2:
    basestring = unicode = str
import os
import posixpath
import time
import datetime
import glob
import shutil
import fnmatch
import zipfile
import json as simplejson
import email
import email.utils
import email.generator
import email.message
import email.header
import email.encoders
import smtplib
import ftplib
import socket
import ssl
if os.name == 'nt':
    import msvcrt
elif os.name == 'posix':
    import fcntl
from django.utils.translation import ugettext as _
#bots-modules
from . import botslib
from . import botsglobal
from .botsconfig import *

@botslib.log_session
def run(idchannel,command,idroute,rootidta=None):
    '''run a communication session (dispatcher for communication functions).'''
    if rootidta is None:
        rootidta = botsglobal.currentrun.get_minta4query()
    for row in botslib.query('''SELECT *
                                FROM channel
                                WHERE idchannel=%(idchannel)s''',
                                {'idchannel':idchannel}):
        channeldict = dict(row)   #convert to real dictionary ()
        botsglobal.logger.debug('Start communication channel "%(idchannel)s" type %(type)s %(inorout)s.',channeldict)
        #for acceptance testing bots has an option to turn of external communication in channels
        if botsglobal.ini.getboolean('acceptance','runacceptancetest',False):
            #override values in channels for acceptance testing.
            #testpath is used to 'trigger' this: if testpath has value, use acceptance.
            if channeldict['testpath']:
                channeldict['path'] = channeldict['testpath']    #use the testpath to specify where to find acceptance  tests.
                channeldict['remove'] = False    #never remove during acceptance testing
                if channeldict['type'] in ['file','mimefile','trash']:
                    pass #do nothing, same type
                elif channeldict['type'] in ['smtp','smtps','smtpstarttls','pop3','pop3s','pop3apop','imap4','imap4s']:
                    channeldict['type'] = 'mimefile'
                else:   #channeldict['type'] in ['ftp','ftps','ftpis','sftp','xmlrpc','ftp','ftp','communicationscript','db',]
                    channeldict['type'] = 'file'
            botsglobal.logger.debug('Channel "%(idchannel)s" adapted for acceptance test: type "%(type)s", testpath "%(testpath)s".',channeldict)
                
        #update communication/run process with idchannel
        ta_run = botslib.OldTransaction(botslib._Transaction.processlist[-1])
        if channeldict['inorout'] == 'in':
            ta_run.update(fromchannel=channeldict['idchannel'])
        else:
            ta_run.update(tochannel=channeldict['idchannel'])

        try:
            userscript,scriptname = botslib.botsimport('communicationscripts',channeldict['idchannel'])
        except botslib.BotsImportError:       #communicationscript is not there; other errors like syntax errors are not catched
            userscript = scriptname = None
        #get the communication class to use:
        if userscript and hasattr(userscript,channeldict['type']):          #check communication class in userscript (sub classing)
            classtocall = getattr(userscript,channeldict['type'])
        elif userscript and hasattr(userscript,'UserCommunicationClass'):   #check for communication class called 'UserCommunicationClass' in userscript. 20110920: Obsolete, depreciated. Keep this for now.
            classtocall = getattr(userscript,'UserCommunicationClass')       #20130206: does have advantages...like for testing etc (no dependent upon type)
        else:
            classtocall = globals()[channeldict['type']]                    #get the communication class from this module

        comclass = classtocall(channeldict,idroute,userscript,scriptname,command,rootidta) #call the class for this type of channel
        comclass.run()
        botsglobal.logger.debug('Finished communication channel "%(idchannel)s" type %(type)s %(inorout)s.',channeldict)
        break   #there can only be one channel; this break takes care that if found, the 'else'-clause is skipped
    else:
        raise botslib.CommunicationError(_('Channel "%(idchannel)s" is unknown.'),{'idchannel':idchannel})


class _comsession(object):
    ''' Abstract class for communication-session. Use only subclasses.
        Subclasses are called by dispatcher function 'run'
        Often 'idroute' is passed as a parameter. This is ONLY because of the @botslib.log_session-wrapper!
        use self.idroute!!
    '''
    def __init__(self,channeldict,idroute,userscript,scriptname,command,rootidta):
        self.channeldict = channeldict
        self.idroute = idroute
        self.userscript = userscript
        self.scriptname = scriptname
        self.command = command
        self.rootidta = rootidta

    def run(self):
        if self.channeldict['inorout'] == 'out':
            self.precommunicate()
            self.connect()
            self.outcommunicate()
            self.disconnect()
            self.archive()
        else:   #incommunication
            if self.command == 'new': #only in-communicate for new run
                #handle maxsecondsperchannel: use global value from bots.ini unless specified in channel. (In database this is field 'rsrv2'.)
                self.maxsecondsperchannel = self.channeldict['rsrv2'] if self.channeldict['rsrv2'] is not None and self.channeldict['rsrv2'] > 0 else botsglobal.ini.getint('settings','maxsecondsperchannel',sys.maxsize)
                try:
                    self.connect()
                except:     #in-connection failed. note that no files are received yet. useful if scheduled quite often, and you do nto want error-report eg when server is down. 
                    #max_nr_retry : get this from channel. should be integer, but only textfields where left. so might be ''/None->use 0
                    max_nr_retry = int(self.channeldict['rsrv1']) if self.channeldict['rsrv1'] else 0
                    if max_nr_retry:
                        domain = ('#' + self.channeldict['idchannel'] + '_failure')[:35] 
                        nr_retry = botslib.unique(domain)  #update nr_retry in database
                        if nr_retry >= max_nr_retry:
                            botslib.unique(domain,updatewith=0)    #reset nr_retry to zero
                            #raises exception
                        else:
                            return  #just return if max_nr_retry is not reached
                    raise
                else:   #in-connection OK
                    #max_nr_retry : get this from channel. should be integer, but only textfields where left. so might be ''/None->use 0
                    max_nr_retry = int(self.channeldict['rsrv1']) if self.channeldict['rsrv1'] else 0
                    if max_nr_retry:
                        domain = 'bots_communication_failure_' + self.channeldict['idchannel']
                        botslib.unique(domain,updatewith=0)    #set nr_retry to zero 
                self.incommunicate()
                self.disconnect()
            self.postcommunicate()
            self.archive()

    def archive(self):
        ''' after the communication channel has ran, archive received of send files.
            archivepath is the root directory for the archive (for this channel).
            within the archivepath files are stored by default as [archivepath]/[date]/[unique_filename]
            
        '''
        if not self.channeldict['archivepath']:
            return  #do not archive if not indicated
        if botsglobal.ini.getboolean('acceptance','runacceptancetest',False): 
            return  #do not archive in acceptance testing
        if self.channeldict['filename'] and self.channeldict['type'] in ('file','ftp','ftps','ftpis','sftp','mimefile','communicationscript'):
            archiveexternalname = botsglobal.ini.getboolean('settings','archiveexternalname',False) #use external filename in archive 
        else:
            archiveexternalname = False
        if self.channeldict['inorout'] == 'in':
            status = FILEIN
            statust = OK
            channel = 'fromchannel'
        else:
            if archiveexternalname:
                status = EXTERNOUT
            else:
                status = FILEOUT
            statust = DONE
            channel = 'tochannel'
        #user script can manipulate archivepath
        if self.userscript and hasattr(self.userscript,'archivepath'):
            archivepath = botslib.runscript(self.userscript,self.scriptname,'archivepath',channeldict=self.channeldict)
        else:
            archivepath = botslib.join(self.channeldict['archivepath'],time.strftime('%Y%m%d'))
        archivezip = botsglobal.ini.getboolean('settings','archivezip',False)   #archive to zip or not
        if archivezip:
            archivepath += '.zip'
        checkedifarchivepathisthere = False  #for a outchannel that is less used, lots of empty dirs will be created. This var is used to check within loop if dir exist, but this is only checked one time.
        for row in botslib.query('''SELECT filename,idta
                                    FROM  ta
                                    WHERE idta>%(rootidta)s
                                    AND   status=%(status)s
                                    AND   statust=%(statust)s
                                    AND   ''' + channel + '''=%(idchannel)s
                                    ''',
                                    {'idchannel':self.channeldict['idchannel'],'status':status,
                                    'statust':statust,'rootidta':self.rootidta}):
            if not checkedifarchivepathisthere:
                if archivezip:
                    botslib.dirshouldbethere(os.path.dirname(archivepath))
                    archivezipfilehandler = zipfile.ZipFile(archivepath,'a',zipfile.ZIP_DEFLATED)
                else:
                    botslib.dirshouldbethere(archivepath)
                checkedifarchivepathisthere = True

            if archiveexternalname:
                if self.channeldict['inorout'] == 'in':
                    # we have internal filename, get external
                    absfilename = botslib.abspathdata(row[str('filename')])
                    taparent = botslib.OldTransaction(idta=row[str('idta')])
                    ta_list = botslib.trace_origin(ta=taparent,where={'status':EXTERNIN})
                    if ta_list:
                        archivename = os.path.basename(ta_list[-1].filename)
                    else:
                        archivename = row[str('filename')]
                else:
                    # we have external filename, get internal
                    archivename = os.path.basename(row[str('filename')])
                    taparent = botslib.OldTransaction(idta=row[str('idta')])
                    ta_list = botslib.trace_origin(ta=taparent,where={'status':FILEOUT})
                    absfilename = botslib.abspathdata(ta_list[0].filename)
            else:
                # use internal name in archive
                absfilename = botslib.abspathdata(row[str('filename')])
                archivename = os.path.basename(row[str('filename')])

            if self.userscript and hasattr(self.userscript,'archivename'):
                archivename = botslib.runscript(self.userscript,self.scriptname,'archivename',channeldict=self.channeldict,idta=row[str('idta')],filename=absfilename)

            if archivezip:
                archivezipfilehandler.write(absfilename,archivename)
            else:
                # if a file of the same name already exists, add a timestamp
                if os.path.isfile(botslib.join(archivepath,archivename)):
                    archivename = os.path.splitext(archivename)[0] + time.strftime('_%H%M%S') + os.path.splitext(archivename)[1]
                shutil.copy(absfilename,botslib.join(archivepath,archivename))

        if archivezip and checkedifarchivepathisthere:
            archivezipfilehandler.close()

    def postcommunicate(self):
        pass

    def precommunicate(self):
        pass

    def file2mime(self):
        ''' convert 'plain' files into email (mime-document).
            1 edi file always in 1 mail.
            from status FILEOUT to FILEOUT
        '''
        #select files with right statust, status and channel.
        for row in botslib.query('''SELECT idta,filename,frompartner,topartner,charset,contenttype,editype,frommail,tomail,cc
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                    AND status=%(status)s
                                    AND statust=%(statust)s
                                    AND tochannel=%(idchannel)s
                                    ''',
                                    {'idchannel':self.channeldict['idchannel'],'status':FILEOUT,
                                    'statust':OK,'idroute':self.idroute,'rootidta':self.rootidta}):
            try:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to = ta_from.copyta(status=FILEOUT)
                ta_to.synall()  #needed for user exits: get all parameters of ta_to from database;
                confirmtype = ''
                confirmasked = False
                charset = row[str('charset')]

                if row[str('editype')] == 'email-confirmation': #outgoing MDN: message is already assembled
                    outfilename = row[str('filename')]
                else:   #assemble message: headers and payload. Bots uses simple MIME-envelope; by default payload is an attachment
                    message = email.message.Message()
                    #set frompartner/sender/'from' header
                    frommail = row[str('frommail')]
                    if not frommail:
                        frommail,ccfrom_not_used_variable = self.idpartner2mailaddress(row[str('frompartner')])    #lookup email address for partnerID
                    message.add_header('From', frommail)

                    #set topartner/receiver/'to' header
                    if self.userscript and hasattr(self.userscript,'getmailaddressforreceiver'):    #user exit to determine to-address/receiver
                        tomail,ccto = botslib.runscript(self.userscript,self.scriptname,'getmailaddressforreceiver',channeldict=self.channeldict,ta=ta_to)
                    elif row[str('tomail')]:
                        tomail = row[str('tomail')]
                        ccto = row[str('cc')]
                    else:
                        tomail,ccto = self.idpartner2mailaddress(row[str('topartner')])          #lookup email address for partnerID
                    message.add_header('To',tomail)
                    if ccto:
                        message.add_header('CC',ccto)

                    if botsglobal.ini.getboolean('acceptance','runacceptancetest',False):
                        reference = '123message-ID email should be unique123'
                        email_datetime = email.utils.formatdate(timeval=time.mktime(time.strptime('2013-01-23 01:23:45', '%Y-%m-%d %H:%M:%S')),localtime=True)
                    else:
                        reference = email.utils.make_msgid(unicode(ta_to.idta))    #use transaction idta in message id.
                        email_datetime = email.utils.formatdate(localtime=True)
                    message.add_header('Message-ID',reference)
                    message.add_header('Date',email_datetime)
                    ta_to.update(frommail=frommail,tomail=tomail,cc=ccto,reference=reference[:70])  #update now (in order to use correct & updated ta_to in userscript)
                                                                                                    #20150326  for now field 'reference' is max 70
                    #set Disposition-Notification-To: ask/ask not a a MDN?
                    if botslib.checkconfirmrules('ask-email-MDN',idroute=self.idroute,idchannel=self.channeldict['idchannel'],
                                                                frompartner=row[str('frompartner')],topartner=row[str('topartner')]):
                        message.add_header('Disposition-Notification-To',frommail)
                        confirmtype = 'ask-email-MDN'
                        confirmasked = True

                    #set subject
                    if botsglobal.ini.getboolean('acceptance','runacceptancetest',False):
                        subject = '12345678'
                    else:
                        subject = unicode(row[str('idta')])
                    content = botslib.readdata_bin(row[str('filename')])     #get attachment from data file
                    if self.userscript and hasattr(self.userscript,'subject'):    #user exit to determine subject
                        subject = botslib.runscript(self.userscript,self.scriptname,'subject',channeldict=self.channeldict,ta=ta_to,subjectstring=subject,content=content)
                    message.add_header('Subject',subject)

                    #set MIME-version
                    message.add_header('MIME-Version','1.0')

                    #set attachment filename
                    filename_mask = self.channeldict['filename'] if self.channeldict['filename'] else '*'
                    attachmentfilename = self.filename_formatter(filename_mask,ta_to)
                    #is message send as body or attachment?
                    if attachmentfilename and self.channeldict['sendmdn'] != 'body':
                        #there is an field in channel for this: 'sendmdn' (in interface this is called: 'as body or as attachment')
                        #another option is to use user scripting (set attachmentfilename - or not)
                        #user scripting can also be used to set - within one channel - one message as  body other as attachment.
                        #send as attachment: if 'As body or attachment' is not 'body' AND there is an attachmentfilename
                        #send as body: if 'As body or attachment' is 'body' or if there is not attachmentfilename
                        #attachmentfilename can be set to None or '' via user exit 'filename'
                        message.add_header('Content-Disposition','attachment',filename=attachmentfilename)

                    #set Content-Type and charset
                    charset = self.convertcodecformime(charset)
                    message.add_header('Content-Type',row[str('contenttype')].lower(),charset=charset)          #contenttype is set in grammar.syntax

                    #set/change email header in user scripting
                    if self.userscript and hasattr(self.userscript,'headers'):
                        botslib.runscript(self.userscript,self.scriptname,'headers',message=message,channeldict=self.channeldict,ta=ta_to,content=content)

                    #set attachment/payload; the Content-Transfer-Encoding is set by python encoder
                    message.set_payload(content)   #do not use charset; this lead to unwanted encodings...bots always uses base64
                    if self.channeldict['askmdn'] == 'never':       #channeldict['askmdn'] is the Mime encoding
                        email.encoders.encode_7or8bit(message)      #no encoding; but the Content-Transfer-Encoding is set to 7-bit or 8-bt
                    elif self.channeldict['askmdn'] == 'ascii' and charset == 'us-ascii':
                        pass        #do nothing: ascii is default encoding
                    else:           #if Mime encoding is 'always' or  (Mime encoding == 'ascii' and charset!='us-ascii'): use base64
                        email.encoders.encode_base64(message)

                    #*******write email to file***************************
                    outfilename = unicode(ta_to.idta)
                    outfile = botslib.opendata_bin(outfilename, 'wb')
                    if sys.version_info[0] > 2:
                        generator = email.generator.BytesGenerator(outfile, mangle_from_=False, maxheaderlen=78)
                    else:
                        generator = email.generator.Generator(outfile, mangle_from_=False, maxheaderlen=78)
                    generator.flatten(message,unixfrom=False)
                    outfile.close()
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt)
            else:
                ta_to.update(statust=OK,filename=outfilename,confirmtype=confirmtype,confirmasked=confirmasked,charset=charset)
            finally:
                ta_from.update(statust=DONE)
        return

    def mime2file(self):
        ''' convert emails (mime-documents) to 'plain' files.
            from status FILEIN to FILEIN
            process emails:
            -   extract information (eg sender-address)
            -   generate MDN (if asked and OK from bots-configuration)
            -   process MDN
            -   save 'attachments' as files
            -   filter emails/attachments based on contenttype
            -   email-address should be know by bots (can be turned off)
        '''
        whitelist_multipart = ['multipart/mixed','multipart/digest','multipart/signed','multipart/report','message/rfc822','multipart/alternative','multipart/related']
        whitelist_major = ['text','application']
        blacklist_contenttype = ['text/html','text/enriched','text/rtf','text/richtext','application/postscript','text/vcard','text/css']
        def savemime(msg):
            ''' save contents of email as separate files.
                is a nested function.
                3x filtering:
                -   whitelist of multipart-contenttype
                -   whitelist of body-contentmajor
                -   blacklist of body-contentytpe
            '''
            nrmimesaved = 0     #count nr of valid 'attachments'
            contenttype     = msg.get_content_type()
            if msg.is_multipart():
                if contenttype in whitelist_multipart:
                    for part in msg.get_payload():
                        nrmimesaved += savemime(part)
            else:    #is not a multipart
                if msg.get_content_maintype() not in whitelist_major or contenttype in blacklist_contenttype:
                    return 0
                content = msg.get_payload(decode=True)
                if not content or content.isspace():
                    return 0
                charset = msg.get_content_charset('ascii')
                if self.userscript and hasattr(self.userscript,'accept_incoming_attachment'):
                    accept_attachment = botslib.runscript(self.userscript,self.scriptname,'accept_incoming_attachment',channeldict=self.channeldict,ta=ta_from,charset=charset,content=content,contenttype=contenttype)
                    if not accept_attachment:
                        return 0
                filesize = len(content)
                ta_file = ta_from.copyta(status=FILEIN)
                outfilename = unicode(ta_file.idta)
                outfile = botslib.opendata_bin(outfilename, 'wb')
                outfile.write(content)
                outfile.close()
                nrmimesaved += 1
                ta_file.update(statust=OK,
                                contenttype=contenttype,
                                filename=outfilename,
                                filesize=filesize)
            return nrmimesaved
        #*****************end of nested function savemime***************************
        @botslib.log_session
        def mdnreceive():
            tmp = msg.get_param('reporttype')
            if tmp is None or email.utils.collapse_rfc2231_value(tmp)!='disposition-notification':    #invalid MDN
                raise botslib.CommunicationInError(_('Received email-MDN with errors.'))
            for part in msg.get_payload():
                if part.get_content_type()=='message/disposition-notification':
                    originalmessageid = part['original-message-id']
                    if originalmessageid is not None:
                        break
            else:   #invalid MDN: 'message/disposition-notification' not in email
                raise botslib.CommunicationInError(_('Received email-MDN with errors.'))
            botslib.changeq('''UPDATE ta
                               SET confirmed=%(confirmed)s, confirmidta=%(confirmidta)s
                               WHERE reference=%(reference)s
                               AND status=%(status)s
                               AND confirmasked=%(confirmasked)s
                               AND confirmtype=%(confirmtype)s
                               ''',
                                {'status':FILEOUT,'reference':originalmessageid,'confirmed':True,'confirmtype':'ask-email-MDN','confirmidta':ta_from.idta,'confirmasked':True})
            #for now no checking if processing was OK.....
            #performance: not good. Index should be on the reference.
        @botslib.log_session
        def mdnsend(ta_from):
            if not botslib.checkconfirmrules('send-email-MDN',idroute=self.idroute,idchannel=self.channeldict['idchannel'],
                                                            frompartner=frompartner,topartner=topartner):
                return 0 #do not send
            #make message
            message = email.message.Message()
            message.add_header('From',tomail)
            dispositionnotificationto = email.utils.parseaddr(msg['disposition-notification-to'])[1]
            message.add_header('To', dispositionnotificationto)
            message.add_header('Subject', 'Return Receipt (displayed) - '+subject)
            message.add_header('MIME-Version','1.0')
            message.add_header('Content-Type','multipart/report',reporttype='disposition-notification')
            #~ message.set_type('multipart/report')
            #~ message.set_param('reporttype','disposition-notification')

            #make human readable message
            humanmessage = email.message.Message()
            humanmessage.add_header('Content-Type', 'text/plain')
            humanmessage.set_payload('This is an return receipt for the mail that you send to '+tomail)
            message.attach(humanmessage)

            #make machine readable message
            machinemessage = email.message.Message()
            machinemessage.add_header('Content-Type', 'message/disposition-notification')
            machinemessage.add_header('Original-Message-ID', reference)
            nep = email.message.Message()
            machinemessage.attach(nep)
            message.attach(machinemessage)

            #write email to file;
            ta_mdn = botslib.NewTransaction(status=MERGED)  #new transaction for group-file
            
            if botsglobal.ini.getboolean('acceptance','runacceptancetest',False):
                mdn_reference = '123message-ID email should be unique123'
                mdn_datetime = email.utils.formatdate(timeval=time.mktime(time.strptime('2013-01-23 01:23:45', '%Y-%m-%d %H:%M:%S')),localtime=True)
            else:
                mdn_reference = email.utils.make_msgid(unicode(ta_mdn.idta))    #we first have to get the mda-ta to make this reference
                mdn_datetime = email.utils.formatdate(localtime=True)
            message.add_header('Date',mdn_datetime)
            message.add_header('Message-ID', mdn_reference)
            
            mdnfilename = unicode(ta_mdn.idta)
            mdnfile = botslib.opendata_bin(mdnfilename, 'wb')
            if sys.version_info[0] > 2:
                generator = email.generator.BytesGenerator(mdnfile, mangle_from_=False, maxheaderlen=78)
            else:
                generator = email.generator.Generator(mdnfile, mangle_from_=False, maxheaderlen=78)
            generator.flatten(message,unixfrom=False)
            mdnfile.close()
            ta_mdn.update(statust=OK,
                            idroute=self.idroute,
                            filename=mdnfilename,
                            editype='email-confirmation',
                            frompartner=topartner,
                            topartner=frompartner,
                            frommail=tomail,
                            tomail=dispositionnotificationto,
                            reference=mdn_reference,
                            content='multipart/report',
                            fromchannel=self.channeldict['idchannel'],
                            charset='ascii',
                            parent=ta_from.idta)
            return ta_mdn.idta
        #*****************end of nested function dispositionnotification***************************
        #get received mails for channel
        for row in botslib.query('''SELECT idta,filename
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                    AND status=%(status)s
                                    AND statust=%(statust)s
                                    AND fromchannel=%(fromchannel)s
                                    ''',
                                    {'status':FILEIN,'statust':OK,'rootidta':self.rootidta,
                                    'fromchannel':self.channeldict['idchannel'],'idroute':self.idroute}):
            try:
                #default values for sending MDN; used to update ta if MDN is not asked
                confirmtype = ''
                confirmed = False
                confirmasked = False
                confirmidta = 0
                #read & parse email
                ta_from = botslib.OldTransaction(row[str('idta')])
                infile = botslib.opendata_bin(row[str('filename')], 'rb')
                if sys.version_info[0] > 2:
                    msg = email.message_from_binary_file(infile)   #read and parse mail
                else:
                    msg = email.message_from_file(infile)   #read and parse mail
                infile.close()
                #******get information from email (sender, receiver etc)***********************************************************
                reference       = self.checkheaderforcharset(msg['message-id'])  or ''
                subject = self.checkheaderforcharset(msg['subject']) or ''
                contenttype     = self.checkheaderforcharset(msg.get_content_type())
                
                #frompartner
                frommail        = self.checkheaderforcharset(email.utils.parseaddr(msg['from'])[1])
                frompartner = ''
                if not self.channeldict['starttls']:    #authorise frompartner or skip authorisation. starttls in channeldict is: 'no check on "from:" email adress'
                    frompartner = self.mailaddress2idpartner(frommail)
                    if frompartner is None:
                        raise botslib.CommunicationInError(_('"From" emailaddress(es) %(email)s not authorised/unknown for channel "%(idchannel)s".'),
                                                            {'email':frommail,'idchannel':self.channeldict['idchannel']})
                #topartner, cc
                list_to_address = [self.checkheaderforcharset(address) for name_not_used_variable,address in email.utils.getaddresses(msg.get_all('to', []))] 
                list_cc_address = [self.checkheaderforcharset(address) for name_not_used_variable,address in email.utils.getaddresses(msg.get_all('cc', []))] 
                cc_content      = ','.join(address for address in (list_to_address + list_cc_address))      #in cc feild geos complete list of addresses.
                if not self.channeldict['apop']:      #authorise topartner or skip authorisation. 'apop' in channeldict is: 'no check on "to:" email adress'
                    for address in list_to_address:   #all tos-addresses are checked; only one needs to be authorised.
                        topartner =  self.mailaddress2idpartner(address)
                        tomail = address
                        if topartner is not None:   #if topartner found: break out of loop
                            break
                    else:   #if no valid topartner: generate error
                        raise botslib.CommunicationInError(_('"To" emailaddress(es) %(email)s not authorised/unknown for channel "%(idchannel)s".'),
                                                            {'email':list_to_address,'idchannel':self.channeldict['idchannel']})
                else:
                    topartner = ''
                    tomail = list_to_address[0] if list_to_address else ''
 
                #update transaction of mail with information found in mail
                ta_from.update(frommail=frommail,   #why save now not later: when saving the attachments need the amil-header-info to be in ta (copyta)
                                tomail=tomail,
                                reference=reference[:70],  #20150326  for now field 'reference' is max 70
                                contenttype=contenttype,
                                frompartner=frompartner,
                                topartner=topartner,
                                cc = cc_content,
                                rsrv1 = subject[:35])
                if contenttype == 'multipart/report':   #process received MDN confirmation
                    mdnreceive()
                else:
                    if 'disposition-notification-to' in msg:  #sender requests a MDN
                        confirmidta = mdnsend(ta_from)
                        if confirmidta:
                            confirmtype = 'send-email-MDN'
                            confirmed = True
                            confirmasked = True
                    nrmimesaved = savemime(msg)
                    if not nrmimesaved:
                        raise botslib.CommunicationInError (_('No valid attachment in received email'))
            except:
                txt = botslib.txtexc()
                ta_from.update(statust=ERROR,errortext=txt)
                ta_from.deletechildren()
            else:
                ta_from.update(statust=DONE,confirmtype=confirmtype,confirmed=confirmed,confirmasked=confirmasked,confirmidta=confirmidta)
        return

    @staticmethod
    def checkheaderforcharset(org_header):
        ''' correct handling of charset for email headers that are saved in database.
        ''' 
        header,encoding = email.header.decode_header(org_header)[0]    #for subjects with non-ascii content special notation exists in MIME-standard
        try:
            if encoding is not None:
                return header.decode(encoding)                       #decode (to unicode)
            #test if valid; use case: spam... need to test because database-storage will give errors otherwise. 
            header.encode('utf8')
            return header
        except:
            raise botslib.CommunicationInError(_('Email header invalid - probably issues with characterset.'))
                        
    def mailaddress2idpartner(self,mailaddress):
        ''' lookup email address to see if know in configuration. '''
        mailaddress_lower = mailaddress.lower()
        #first check in chanpar email-addresses for this channel
        for row in botslib.query('''SELECT chanpar.idpartner_id as idpartner
                                    FROM chanpar,channel,partner
                                    WHERE chanpar.idchannel_id=channel.idchannel
                                    AND chanpar.idpartner_id=partner.idpartner
                                    AND partner.active=%(active)s
                                    AND chanpar.idchannel_id=%(idchannel)s
                                    AND LOWER(chanpar.mail)=%(mail)s''',
                                    {'active':True,'idchannel':self.channeldict['idchannel'],'mail':mailaddress_lower}):
            return row[str('idpartner')]
        #if not found, check in partner-tabel (is less specific).
        for row in botslib.query('''SELECT idpartner
                                    FROM partner
                                    WHERE active=%(active)s
                                    AND LOWER(mail) = %(mail)s ''',
                                    {'active':True,'mail':mailaddress_lower}):
            return row[str('idpartner')]
        return None     #indicate email address is unknown


    def idpartner2mailaddress(self,idpartner):
        for row in botslib.query('''SELECT chanpar.mail as mail,chanpar.cc as cc
                                    FROM chanpar,channel,partner
                                    WHERE chanpar.idchannel_id=channel.idchannel
                                    AND chanpar.idpartner_id=partner.idpartner
                                    AND partner.active=%(active)s
                                    AND chanpar.idchannel_id=%(idchannel)s
                                    AND chanpar.idpartner_id=%(idpartner)s''',
                                    {'active':True,'idchannel':self.channeldict['idchannel'],'idpartner':idpartner}):
            if row[str('mail')]:
                return row[str('mail')],row[str('cc')]
        for row in botslib.query('''SELECT mail,cc
                                    FROM partner
                                    WHERE active=%(active)s
                                    AND idpartner=%(idpartner)s''',
                                    {'active':True,'idpartner':idpartner}):
            if row[str('mail')]:
                return row[str('mail')],row[str('cc')]
        raise botslib.CommunicationOutError(_('No mail-address for partner "%(partner)s" (channel "%(idchannel)s").'),
                                                {'partner':idpartner,'idchannel':self.channeldict['idchannel']})

    def connect(self):
        pass

    def disconnect(self):
        pass

    @staticmethod
    def convertcodecformime(codec_in):
        convertdict = {
            'ascii' : 'us-ascii',
            'unoa' : 'us-ascii',
            'unob' : 'us-ascii',
            'unoc' : 'iso-8859-1',
            }
        codec_in = codec_in.lower().replace('_','-')
        return convertdict.get(codec_in,codec_in)


    def filename_formatter(self,filename_mask,ta):
        ''' Output filename generation from template filename configured in the channel
            Basically python's string.Formatter is used; see http://docs.python.org/library/string.html
            As in string.Formatter, substitution values are surrounded by braces; format specifiers can be used.
            Any ta value can be used
              eg. {botskey}, {alt}, {editype}, {messagetype}, {topartner}
            Next to the value in ta you can use:
            -   * : an unique number (per outchannel) using an asterisk; since bots3.3: {unique}
            -   {datetime}  use datetime with a valid strftime format: 
                eg. {datetime:%Y%m%d}, {datetime:%H%M%S}
            -   {infile} use the original incoming filename; use name and extension, or either part separately:
                eg. {infile}, {infile:name}, {infile:ext}
            -   {overwrite}  if file wit hfielname exists: overwrite it (instead of appending)
            
            Exampels of usage:
                {botskey}_{unique}.idoc        use incoming order number, add unique number, use extension '.idoc'
                {unique}_{infile}              passthrough incoming filename & extension, prepend with unique number
                {infile:name}_{unique}.txt     passthrough incoming filename, add unique number but change extension to .txt
                {editype}-{messagetype}-{datetime:%Y%m%d}-{unique}.{infile:ext}
                                        use editype, messagetype, date and unique number with extension from the incoming file
                {topartner}/{messagetype}/{unique}.edi
                                        Usage of subdirectories in the filename, they must already exist. In the example:
                                        sort into folders by partner and messagetype.
                        
            Note1: {botskey} can only be used if merge is False for that messagetype
        '''
        class infilestr(str):
            ''' class for the {infile} parameter '''
            def __format__(self, format_spec):
                if not format_spec:
                    return unicode(self)
                name,ext = os.path.splitext(unicode(self))
                if format_spec == 'ext':
                    if ext.startswith('.'):
                        ext = ext[1:]
                    return ext 
                if format_spec == 'name':
                    return name 
                raise botslib.CommunicationOutError(_('Error in format of "{filename}": unknown format: "%(format)s".'),
                                                    {'format':format_spec})
        #handling of the 'unique' part in the filename
        #this was astriks ('*') in bots<-3.2, is now {unique}. Reason for change: more options in format via python formatstrings
        #old way (asteriks) will keep working 
        ta.unique = unicode(botslib.unique(self.channeldict['idchannel']))  #create unique part for attachment-filename; stoe in ta-obejct so is assesible for {unique}
        tofilename = filename_mask.replace('*','{unique}')                  #replace 'old' way of making filenames unique by new way.
        ta.synall()
        if '{infile' in tofilename:
            ta_list = botslib.trace_origin(ta=ta,where={'status':EXTERNIN})
            if ta_list:
                ta.infilename = infilestr(os.path.basename(ta_list[-1].filename))
            else:
                ta.infilename = ''
        if '{datetime' in tofilename:
            if botsglobal.ini.getboolean('acceptance','runacceptancetest',False):
                ta.datetime = datetime.datetime.strptime('2013-01-23 01:23:45', '%Y-%m-%d %H:%M:%S')
            else:
                ta.datetime = datetime.datetime.now()
        try:
            tofilename = tofilename.format(infile=ta.infilename,**ta.__dict__)   #do the actual formatting 
        except:
            txt = botslib.txtexc()
            raise botslib.CommunicationOutError(_('Error in formatting outgoing filename "%(filename)s". Error: "%(error)s".'),
                                                    {'filename':tofilename,'error':txt})
        if self.userscript and hasattr(self.userscript,'filename'):
            return botslib.runscript(self.userscript,self.scriptname,'filename',channeldict=self.channeldict,filename=tofilename,ta=ta)
        else:
            return tofilename


class file(_comsession):
    def connect(self):
        if self.channeldict['lockname']:        #directory locking: create lock-file. If the lockfile is already present an exception is raised.
            self.lockname = botslib.join(self.channeldict['path'],self.channeldict['lockname'])
            lock = os.open(self.lockname,os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            os.close(lock)

    @botslib.log_session
    def incommunicate(self):
        ''' gets files from filesystem.
        '''
        frompath = botslib.join(self.channeldict['path'],self.channeldict['filename'])
        filelist = sorted(filename for filename in glob.iglob(frompath) if os.path.isfile(filename))
        startdatetime = datetime.datetime.now()
        remove_ta = False
        for fromfilename in filelist:
            try:
                ta_from = botslib.NewTransaction(filename=fromfilename,
                                                status=EXTERNIN,
                                                fromchannel=self.channeldict['idchannel'],
                                                idroute=self.idroute)
                ta_to =   ta_from.copyta(status=FILEIN)
                remove_ta = True
                #open fromfile, syslock if indicated
                fromfile = open(fromfilename,'rb')
                filesize = os.fstat(fromfile.fileno()).st_size
                if self.channeldict['syslock']:
                    if os.name == 'nt':
                        msvcrt.locking(fromfile.fileno(), msvcrt.LK_LOCK, 0x0fffffff)
                    elif os.name == 'posix':
                        fcntl.lockf(fromfile.fileno(), fcntl.LOCK_SH|fcntl.LOCK_NB)
                    else:
                        raise botslib.LockedFileError(_('Can not do a systemlock on this platform'))
                #open tofile
                tofilename = unicode(ta_to.idta)
                tofile = botslib.opendata_bin(tofilename, 'wb')
                #copy
                shutil.copyfileobj(fromfile,tofile,1048576)
                tofile.close()
                fromfile.close()
            except:
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='file-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
            else:
                ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                ta_from.update(statust=DONE)
                if self.channeldict['remove']:
                    os.remove(fromfilename)
            finally:
                remove_ta = False
                if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                    break

    @botslib.log_session
    def outcommunicate(self):
        ''' does output of files to filesystem. To be used via send-dispatcher.
            Output is either:
            1.  1 outputfile, messages are appended; filename is a fixed name
            2.  to directory; new file for each db-ta; if file exits: overwrite. File has to have a unique name.
        '''
        #check if output dir exists, else create it.
        outputdir = botslib.join(self.channeldict['path'])
        botslib.dirshouldbethere(outputdir)
        #get right filename_mask & determine if fixed name (append) or files with unique names
        filename_mask = self.channeldict['filename'] if self.channeldict['filename'] else '*'
        if '{overwrite}' in filename_mask:
            filename_mask = filename_mask.replace('{overwrite}','')
            mode = 'wb'
        else:
            mode = 'ab'
        #select the db-ta's for this channel
        for row in botslib.query('''SELECT idta,filename,numberofresends
                                       FROM ta
                                      WHERE idta>%(rootidta)s
                                        AND status=%(status)s
                                        AND statust=%(statust)s
                                        AND tochannel=%(tochannel)s
                                        ORDER BY idta
                                        ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,
                                    'status':FILEOUT,'statust':OK}):
            try:    #for each db-ta:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to =   ta_from.copyta(status=EXTERNOUT)
                #open tofile, incl syslock if indicated
                tofilename = self.filename_formatter(filename_mask,ta_from)
                tofilename = botslib.join(outputdir,tofilename)
                tofile = open(tofilename, mode)
                if self.channeldict['syslock']:
                    if os.name == 'nt':
                        msvcrt.locking(tofile.fileno(), msvcrt.LK_LOCK, 0x0fffffff)
                    elif os.name == 'posix':
                        fcntl.lockf(tofile.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
                    else:
                        raise botslib.LockedFileError(_('Can not do a systemlock on this platform'))
                #open fromfile
                fromfile = botslib.opendata_bin(row[str('filename')], 'rb')
                #copy
                shutil.copyfileobj(fromfile,tofile,1048576)
                fromfile.close()
                tofile.close()
                #Rename filename after writing file.
                #Function: safe file writing: do not want another process to read the file while it is being written.
                #This is safe because file rename is atomic within same file system (?what about network shares?)
                if self.channeldict['mdnchannel']:
                    tofilename_old = tofilename
                    tofilename = botslib.rreplace(tofilename_old,self.channeldict['mdnchannel'])
                    os.rename(tofilename_old,tofilename)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename=tofilename,numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)

    def disconnect(self):
        #delete directory-lockfile
        if self.channeldict['lockname']:
            os.remove(self.lockname)


class pop3(_comsession):
    def connect(self):
        import poplib
        self.session = poplib.POP3(host=self.channeldict['host'],port=int(self.channeldict['port']))
        self.session.set_debuglevel(botsglobal.ini.getint('settings','pop3debug',0))    #if used, gives information about session (on screen), for debugging pop3
        self.session.user(self.channeldict['username'])
        self.session.pass_(self.channeldict['secret'])

    @botslib.log_session
    def incommunicate(self):
        ''' Fetch messages from Pop3-mailbox.
            A bad connection is tricky, because mails are actually only deleted on the server when QUIT is successful.
            A solution would be to connect, fetch, delete and quit for each mail, but this might introduce other problems.
            So: keep a list of idta received OK.
            If QUIT is not successful than delete these ta's
        '''
        self.listoftamarkedfordelete = []
        maillist = self.session.list()[1]     #get list of messages #alt: (response, messagelist, octets) = popsession.list()     #get list of messages
        startdatetime = datetime.datetime.now()
        remove_ta = False
        for mail in maillist:
            try:
                ta_from = botslib.NewTransaction(filename='pop3://'+self.channeldict['username']+'@'+self.channeldict['host'],
                                                    status=EXTERNIN,
                                                    fromchannel=self.channeldict['idchannel'],idroute=self.idroute)
                ta_to =   ta_from.copyta(status=FILEIN)
                remove_ta = True
                tofilename = unicode(ta_to.idta)
                mailid = int(mail.split()[0])  #first 'word' is the message number/ID
                maillines = self.session.retr(mailid)[1]        #alt: (header, messagelines, octets) = popsession.retr(messageID)
                content = b'\n'.join(maillines)
                filesize = len(content)
                tofile = botslib.opendata_bin(tofilename, 'wb')
                tofile.write(content)
                tofile.close()
                if self.channeldict['remove']:      #on server side mail is marked to be deleted. The pop3-server will actually delete the file if the QUIT commnd is receieved!
                    self.session.dele(mailid)
                    #add idta's of received mail in a list. If connection is not OK, QUIT command to POP3 server will not work. deleted mail will still be on server.
                    self.listoftamarkedfordelete += [ta_from.idta,ta_to.idta]

            except:         #something went wrong for this mail.
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='pop3-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
                #test connection. if connection is not OK stop fetching mails.
                try:
                    self.session.noop()
                except:
                    self.session = None     #indicate session is not valid anymore
                    break
            else:
                ta_to.update(statust=OK,filename=tofilename,filesize=filesize)
                ta_from.update(statust=DONE)
            finally:
                remove_ta = False
                if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                    break

    def disconnect(self):
        try:
            if not self.session:
                raise Exception(_('Pop3 connection not OK'))
            resp = self.session.quit()     #pop3 server will now actually delete the mails
            if not resp.startswith(b'+'):
                raise Exception(_('QUIT command to POP3 server failed'))
        except Exception:   #connection is gone. Delete everything that is received to avoid double receiving.
            botslib.ErrorProcess(functionname='pop3-incommunicate',errortext='Could not fetch emails via POP3; probably communication problems',channeldict=self.channeldict)
            for idta in self.listoftamarkedfordelete:
                ta = botslib.OldTransaction(idta)
                ta.delete()

    @botslib.log_session
    def postcommunicate(self):
        self.mime2file()

class pop3s(pop3):
    def connect(self):
        import poplib
        self.session = poplib.POP3_SSL(host=self.channeldict['host'],port=int(self.channeldict['port']),keyfile=self.channeldict['keyfile'],certfile=self.channeldict['certfile'])
        self.session.set_debuglevel(botsglobal.ini.getint('settings','pop3debug',0))    #if used, gives information about session (on screen), for debugging pop3
        self.session.user(self.channeldict['username'])
        self.session.pass_(self.channeldict['secret'])

class pop3apop(pop3):
    def connect(self):
        import poplib
        self.session = poplib.POP3(host=self.channeldict['host'],port=int(self.channeldict['port']))
        self.session.set_debuglevel(botsglobal.ini.getint('settings','pop3debug',0))    #if used, gives information about session (on screen), for debugging pop3
        self.session.apop(self.channeldict['username'],self.channeldict['secret'])    #python handles apop password encryption


class imap4(_comsession):
    ''' Fetch email from IMAP server.
    '''
    def connect(self):
        import imaplib
        imaplib.Debug = botsglobal.ini.getint('settings','imap4debug',0)    #if used, gives information about session (on screen), for debugging imap4
        self.session = imaplib.IMAP4(host=self.channeldict['host'],port=int(self.channeldict['port']))
        self.session.login(self.channeldict['username'],self.channeldict['secret'])

    @botslib.log_session
    def incommunicate(self):
        ''' Fetch messages from imap4-mailbox.
        '''
        # path may contain a mailbox name, otherwise use INBOX
        if self.channeldict['path']:
            mailbox_name = self.channeldict['path']
        else:
            mailbox_name = 'INBOX'

        response, data = self.session.select(mailbox_name)
        if response != 'OK': # eg. mailbox does not exist
            raise botslib.CommunicationError(mailbox_name + ': ' + data[0])

        # Get the message UIDs that should be read
        response, data = self.session.uid('search', None, '(UNDELETED)')
        if response != 'OK': # have never seen this happen, but just in case!
            raise botslib.CommunicationError(mailbox_name + ': ' + data[0])

        maillist = data[0].split()
        startdatetime = datetime.datetime.now()
        remove_ta = False
        for mail in maillist:
            try:
                ta_from = botslib.NewTransaction(filename='imap4://'+self.channeldict['username']+'@'+self.channeldict['host'],
                                                    status=EXTERNIN,
                                                    fromchannel=self.channeldict['idchannel'],idroute=self.idroute)
                ta_to =   ta_from.copyta(status=FILEIN)
                remove_ta = True
                filename = unicode(ta_to.idta)
                # Get the message (header and body)
                response, msg_data = self.session.uid('fetch',mail, '(RFC822)')
                filehandler = botslib.opendata_bin(filename, 'wb')
                filesize = len(msg_data[0][1])
                filehandler.write(msg_data[0][1])
                filehandler.close()
                # Flag message for deletion AND expunge. Direct expunge has advantages for bad (internet)connections.
            except:
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='imap4-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
            else:
                ta_to.update(statust=OK,filename=filename,filesize=filesize)
                ta_from.update(statust=DONE)
                if self.channeldict['remove']:
                    self.session.uid('store',mail, '+FLAGS', r'(\Deleted)')
                    self.session.expunge()
            finally:
                remove_ta = False
                if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                    break

        self.session.close()        #Close currently selected mailbox. This is the recommended command before 'LOGOUT'.

    @botslib.log_session
    def postcommunicate(self):
        self.mime2file()

    def disconnect(self):
        self.session.logout()

class imap4s(imap4):
    def connect(self):
        import imaplib
        imaplib.Debug = botsglobal.ini.getint('settings','imap4debug',0)    #if used, gives information about session (on screen), for debugging imap4
        self.session = imaplib.IMAP4_SSL(host=self.channeldict['host'],port=int(self.channeldict['port']),keyfile=self.channeldict['keyfile'],certfile=self.channeldict['certfile'])
        self.session.login(self.channeldict['username'],self.channeldict['secret'])


class smtp(_comsession):
    @botslib.log_session
    def precommunicate(self):
        self.file2mime()

    def connect(self):
        self.session = smtplib.SMTP(host=self.channeldict['host'],port=int(self.channeldict['port'])) #make connection
        self.session.set_debuglevel(botsglobal.ini.getint('settings','smtpdebug',0))    #if used, gives information about session (on screen), for debugging smtp
        self.login()

    def login(self):
        if self.channeldict['username'] and self.channeldict['secret']:
            try:
                #error in python 2.6.4....user and password can not be unicode
                self.session.login(str(self.channeldict['username']),str(self.channeldict['secret']))
            except smtplib.SMTPAuthenticationError:
                raise botslib.CommunicationOutError(_('SMTP server did not accept user/password combination.'))
            except:
                txt = botslib.txtexc()
                raise botslib.CommunicationOutError(_('SMTP login failed. Error:\n%(txt)s'),{'txt':txt})

    @botslib.log_session
    def outcommunicate(self):
        ''' does smtp-session.
            SMTP does not allow rollback. So if the sending of a mail fails, other mails may have been send.
        '''
        #send messages
        for row in botslib.query('''SELECT idta,filename,frommail,tomail,cc,numberofresends
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                    AND status=%(status)s
                                    AND statust=%(statust)s
                                    AND tochannel=%(tochannel)s
                                    ''',
                                    {'status':FILEOUT,'statust':OK,'rootidta':self.rootidta,
                                    'tochannel':self.channeldict['idchannel']}):
            try:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to = ta_from.copyta(status=EXTERNOUT)
                addresslist = row[str('tomail')].split(',') + row[str('cc')].split(',')
                addresslist = [x.strip() for x in addresslist if x.strip()]
                sendfile = botslib.opendata_bin(row[str('filename')], 'rb')
                msg = sendfile.read()
                sendfile.close()
                self.session.sendmail(row[str('frommail')], addresslist, msg)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,filename='smtp://'+self.channeldict['username']+'@'+self.channeldict['host'],numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename='smtp://'+self.channeldict['username']+'@'+self.channeldict['host'],numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)

    def disconnect(self):
        try:    #Google gives/gave error closing connection. Not a real problem.
            self.session.quit()
        except socket.sslerror:     #for a starttls connection
            self.session.close()
        except:
            pass

class smtps(smtp):
    def connect(self):
        self.session = smtplib.SMTP_SSL(host=self.channeldict['host'],port=int(self.channeldict['port']),keyfile=self.channeldict['keyfile'],certfile=self.channeldict['certfile']) #make connection
        self.session.set_debuglevel(botsglobal.ini.getint('settings','smtpdebug',0))    #if used, gives information about session (on screen), for debugging smtp
        self.login()

class smtpstarttls(smtp):
    def connect(self):
        self.session = smtplib.SMTP(host=self.channeldict['host'],port=int(self.channeldict['port'])) #make connection
        self.session.set_debuglevel(botsglobal.ini.getint('settings','smtpdebug',0))    #if used, gives information about session (on screen), for debugging smtp
        self.session.ehlo()
        self.session.starttls(keyfile=self.channeldict['keyfile'],certfile=self.channeldict['certfile'])
        self.session.ehlo()
        self.login()


class mimefile(file):
    @botslib.log_session
    def postcommunicate(self):
        self.mime2file()
    @botslib.log_session
    def precommunicate(self):
        self.file2mime()

class ftp(_comsession):
    def connect(self):
        botslib.settimeout(botsglobal.ini.getint('settings','ftptimeout',10))
        self.session = ftplib.FTP()
        self.session.set_debuglevel(botsglobal.ini.getint('settings','ftpdebug',0))   #set debug level (0=no, 1=medium, 2=full debug)
        self.session.set_pasv(not self.channeldict['ftpactive']) #active or passive ftp
        self.session.connect(host=self.channeldict['host'],port=int(self.channeldict['port']))
        self.session.login(user=self.channeldict['username'],passwd=self.channeldict['secret'],acct=self.channeldict['ftpaccount'])
        self.set_cwd()

    def set_cwd(self):
        self.dirpath = self.session.pwd()
        if self.channeldict['path']:
            self.dirpath = posixpath.normpath(posixpath.join(self.dirpath,self.channeldict['path']))
            try:
                self.session.cwd(self.dirpath)           #set right path on ftp-server
            except:
                self.session.mkd(self.dirpath)           #set right path on ftp-server; no nested directories
                self.session.cwd(self.dirpath)           #set right path on ftp-server

    @botslib.log_session
    def incommunicate(self):
        ''' do ftp: receive files. To be used via receive-dispatcher.
            each to be imported file is transaction.
            each imported file is transaction.
        '''
        def writeline_callback(line):
            ''' inline function to write to file for non-binary ftp
            '''
            tofile.write(line + '\n')
        startdatetime = datetime.datetime.now()
        files = []
        try:            #some ftp servers give errors when directory is empty; catch these errors here
            files = self.session.nlst()
        except (ftplib.error_perm,ftplib.error_temp) as msg:
            if unicode(msg)[:3] not in ['550','450']:
                raise

        lijst = fnmatch.filter(files,self.channeldict['filename'])
        remove_ta = False
        for fromfilename in lijst:  #fetch messages from ftp-server.
            try:
                ta_from = botslib.NewTransaction(filename='ftp:/'+posixpath.join(self.dirpath,fromfilename),
                                                    status=EXTERNIN,
                                                    fromchannel=self.channeldict['idchannel'],
                                                    idroute=self.idroute)
                ta_to =   ta_from.copyta(status=FILEIN)
                remove_ta = True
                tofilename = unicode(ta_to.idta)
                try:
                    if self.channeldict['ftpbinary']:
                        tofile = botslib.opendata_bin(tofilename, 'wb')
                        self.session.retrbinary('RETR ' + fromfilename, tofile.write)
                    else:
                        tofile = botslib.opendata(tofilename, 'wb',charset='latin-1')   #python3 gives back a 'string'.
                        self.session.retrlines('RETR ' + fromfilename, writeline_callback)
                except ftplib.error_perm as msg:
                    if unicode(msg)[:3] in ['550',]:     #we are trying to download a directory...
                        raise botslib.BotsError('To be catched')
                    else:
                        raise
                tofile.close()
                filesize = os.path.getsize(botslib.abspathdata(tofilename))
                if not filesize:
                    raise botslib.BotsError('To be catched; directory (or empty file)')
            except botslib.BotsError:   #directory or empty file; handle exception but generate no error.
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
            except:
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='ftp-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
            else:
                ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                ta_from.update(statust=DONE)
                if self.channeldict['remove']:
                    self.session.delete(fromfilename)
            finally:
                remove_ta = False
                if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                    break

    @botslib.log_session
    def outcommunicate(self):
        ''' do ftp: send files. To be used via receive-dispatcher.
            each to be send file is transaction.
            each send file is transaction.
            NB: ftp command APPE should be supported by server
        '''
        #get right filename_mask & determine if fixed name (append) or files with unique names
        filename_mask = self.channeldict['filename'] if self.channeldict['filename'] else '*'
        if '{overwrite}' in filename_mask:
            filename_mask = filename_mask.replace('{overwrite}','')
            mode = 'STOR '
        else:
            mode = 'APPE '
        for row in botslib.query('''SELECT idta,filename,numberofresends
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                      AND status=%(status)s
                                      AND statust=%(statust)s
                                      AND tochannel=%(tochannel)s
                                        ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,
                                    'status':FILEOUT,'statust':OK}):
            try:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to = ta_from.copyta(status=EXTERNOUT)
                tofilename = self.filename_formatter(filename_mask,ta_from)
                fromfile = botslib.opendata_bin(row[str('filename')], 'rb')
                if self.channeldict['ftpbinary']:
                    self.session.storbinary(mode + tofilename, fromfile)
                else:
                    self.session.storlines(mode + tofilename, fromfile)
                fromfile.close()
                #Rename filename after writing file.
                #Function: safe file writing: do not want another process to read the file while it is being written.
                if self.channeldict['mdnchannel']:
                    tofilename_old = tofilename
                    tofilename = botslib.rreplace(tofilename_old,self.channeldict['mdnchannel'])
                    self.session.rename(tofilename_old,tofilename)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,filename='ftp:/'+posixpath.join(self.dirpath,tofilename),numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename='ftp:/'+posixpath.join(self.dirpath,tofilename),numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)

    def disconnect(self):
        try:
            self.session.quit()
        except:
            self.session.close()
        botslib.settimeout(botsglobal.ini.getint('settings','globaltimeout',10))

class ftps(ftp):
    ''' explicit ftps as defined in RFC 2228 and RFC 4217.
        standard port to connect to is as in normal FTP (port 21)
        ftps is supported by python >= 2.7
    '''
    def connect(self):
        if not hasattr(ftplib,'FTP_TLS'):
            raise botslib.CommunicationError(_('ftps is not supported by your python version, use >=2.7'))
        botslib.settimeout(botsglobal.ini.getint('settings','ftptimeout',10))
        self.session = ftplib.FTP_TLS(keyfile=self.channeldict['keyfile'],certfile=self.channeldict['certfile'])
        self.session.set_debuglevel(botsglobal.ini.getint('settings','ftpdebug',0))   #set debug level (0=no, 1=medium, 2=full debug)
        self.session.set_pasv(not self.channeldict['ftpactive']) #active or passive ftp
        self.session.connect(host=self.channeldict['host'],port=int(self.channeldict['port']))
        self.session.auth()
        self.session.login(user=self.channeldict['username'],passwd=self.channeldict['secret'],acct=self.channeldict['ftpaccount'])
        self.session.prot_p()
        self.set_cwd()


#sub classing of ftplib for ftpis
if hasattr(ftplib,'FTP_TLS'):
    class Ftp_tls_implicit(ftplib.FTP_TLS):
        ''' FTPS implicit is not directly supported by python; python>=2.7 supports only ftps explicit.
            So class ftplib.FTP_TLS is sub-classed here, with the needed modifications.
            (code is nicked from ftplib.ftp v. 2.7; additions/changes are indicated)
            '''
        def connect(self, host='', port=0, timeout=-999):
            #added hje 20110713: directly use SSL in FTPIS
            #end added
            if host != '':
                self.host = host
            if port > 0:
                self.port = port
            if timeout != -999:
                self.timeout = timeout
            self.sock = socket.create_connection((self.host, self.port), self.timeout)
            self.af = self.sock.family
            #added hje 20110713: directly use SSL in FTPIS
            self.sock = ssl.wrap_socket(self.sock, self.keyfile, self.certfile,ssl_version=self.ssl_version)
            #end added
            if sys.version_info[0] > 2:
                self.file = self.sock.makefile('r', encoding=self.encoding)
            else:
                self.file = self.sock.makefile('rb')
            self.welcome = self.getresp()
            return self.welcome
        def prot_p(self):
            #Inovis FTPIS gives errors on 'PBSZ 0' and 'PROT P', vsftp does not work without these commands.
            #These errors are just catched, nothing is done with them.
            try:
                self.voidcmd('PBSZ 0')
            except ftplib.error_perm:
                pass
            try:
                resp = self.voidcmd('PROT P')
            except ftplib.error_perm:
                resp = None
            self._prot_p = True
            return resp


class ftpis(ftp):
    ''' FTPS implicit; is not defined in a RFC.
        standard port to connect is port 990.
        FTPS implicit is not supported by python.
        python>=2.7 supports ftps explicit.
        So used is the sub-class Ftp_tls_implicit.
        Tested with Inovis and VSFTPd.
        Python library FTP_TLS uses ssl_version = ssl.PROTOCOL_TLSv1
        Inovis seems to need PROTOCOL_SSLv3
        This is 'solved' by using 'parameters' in the channel.
        ~ ssl.PROTOCOL_SSLv2  = 0
        ~ ssl.PROTOCOL_SSLv3  = 1
        ~ ssl.PROTOCOL_SSLv23 = 2
        ~ ssl.PROTOCOL_TLSv1  = 3
    '''
    def connect(self):
        if not hasattr(ftplib,'FTP_TLS'):
            raise botslib.CommunicationError(_('ftpis is not supported by your python version, use >=2.7'))
        botslib.settimeout(botsglobal.ini.getint('settings','ftptimeout',10))
        self.session = Ftp_tls_implicit(keyfile=self.channeldict['keyfile'],certfile=self.channeldict['certfile'])
        if self.channeldict['parameters']:
            self.session.ssl_version = int(self.channeldict['parameters'])
        self.session.set_debuglevel(botsglobal.ini.getint('settings','ftpdebug',0))   #set debug level (0=no, 1=medium, 2=full debug)
        self.session.set_pasv(not self.channeldict['ftpactive']) #active or passive ftp
        self.session.connect(host=self.channeldict['host'],port=int(self.channeldict['port']))
        #~ self.session.auth()
        self.session.login(user=self.channeldict['username'],passwd=self.channeldict['secret'],acct=self.channeldict['ftpaccount'])
        self.session.prot_p()
        self.set_cwd()


class sftp(_comsession):
    ''' SFTP: SSH File Transfer Protocol (SFTP is not FTP run over SSH, SFTP is not Simple File Transfer Protocol)
        standard port to connect to is port 22.
        requires paramiko and pycrypto to be installed
        based on class ftp and ftps above with code from demo_sftp.py which is included with paramiko
        Mike Griffin 16/10/2010
        Henk-jan ebbers 20110802: when testing I found that the transport also needs to be closed. So changed transport ->self.transport, and close this in disconnect
        henk-jan ebbers 20111019: disabled the host_key part for now (but is very interesting). Is not tested; keys should be integrated in bots also for other protocols.
        henk-jan ebbers 20120522: hostkey and privatekey can now be handled in user exit.
    '''
    def connect(self):
        # check dependencies
        try:
            import paramiko
        except:
            raise ImportError(_('Dependency failure: communicationtype "sftp" requires python library "paramiko".'))
        try:
            from Crypto import Cipher
        except:
            raise ImportError(_('Dependency failure: communicationtype "sftp" requires python library "pycrypto".'))
        # setup logging if required
        ftpdebug = botsglobal.ini.getint('settings','ftpdebug',0)
        if ftpdebug > 0:
            log_file = botslib.join(botsglobal.ini.get('directories','logging'),'sftp.log')
            # Convert ftpdebug to paramiko logging level (1=20=info, 2=10=debug)
            paramiko.util.log_to_file(log_file, 30-(ftpdebug*10))

        # Get hostname and port to use
        hostname = self.channeldict['host']
        try:
            port = int(self.channeldict['port'])
        except:
            port = 22 # default port for sftp

        if self.userscript and hasattr(self.userscript,'hostkey'):
            hostkey = botslib.runscript(self.userscript,self.scriptname,'hostkey',channeldict=self.channeldict)
        else:
            hostkey = None
        if self.userscript and hasattr(self.userscript,'privatekey'):
            privatekeyfile,pkeytype,pkeypassword = botslib.runscript(self.userscript,self.scriptname,'privatekey',channeldict=self.channeldict)
            if pkeytype == 'RSA':
                pkey = paramiko.RSAKey.from_private_key_file(filename=privatekeyfile,password=pkeypassword)
            else:
                pkey = paramiko.DSSKey.from_private_key_file(filename=privatekeyfile,password=pkeypassword)
        else:
            pkey = None

        if self.channeldict['secret']:  #if password is empty string: use None. Else error can occur.
            secret = self.channeldict['secret']
        else:
            secret = None
        # now, connect and use paramiko Transport to negotiate SSH2 across the connection
        self.transport = paramiko.Transport((hostname,port))
        self.transport.connect(username=self.channeldict['username'],password=secret,hostkey=hostkey,pkey=pkey)
        self.session = paramiko.SFTPClient.from_transport(self.transport)
        channel = self.session.get_channel()
        channel.settimeout(botsglobal.ini.getint('settings','ftptimeout',10))
        self.set_cwd()

    def set_cwd(self):
        self.session.chdir('.') # getcwd does not work without this chdir first!
        self.dirpath = self.session.getcwd()
        if self.channeldict['path']:
            self.dirpath = posixpath.normpath(posixpath.join(self.dirpath,self.channeldict['path']))
            try:
                self.session.chdir(self.dirpath)
            except:
                self.session.mkdir(self.dirpath)
                self.session.chdir(self.dirpath)

    def disconnect(self):
        self.session.close()
        self.transport.close()
        

    @botslib.log_session
    def incommunicate(self):
        ''' do ftp: receive files. To be used via receive-dispatcher.
            each to be imported file is transaction.
            each imported file is transaction.
        '''
        startdatetime = datetime.datetime.now()
        files = self.session.listdir('.')
        lijst = fnmatch.filter(files,self.channeldict['filename'])
        remove_ta = False
        for fromfilename in lijst:  #fetch messages from sftp-server.
            try:
                ta_from = botslib.NewTransaction(filename='sftp:/'+posixpath.join(self.dirpath,fromfilename),
                                                    status=EXTERNIN,
                                                    fromchannel=self.channeldict['idchannel'],
                                                    idroute=self.idroute)
                ta_to =   ta_from.copyta(status=FILEIN)
                remove_ta = True
                tofilename = unicode(ta_to.idta)
                fromfile = self.session.open(fromfilename, 'r')    # SSH treats all files as binary. paramiko doc says: b-flag is ignored
                content = fromfile.read()
                filesize = len(content)
                tofile = botslib.opendata_bin(tofilename, 'wb')
                tofile.write(content)
                tofile.close()
                fromfile.close()
            except:
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='sftp-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
            else:
                ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                ta_from.update(statust=DONE)
                if self.channeldict['remove']:
                    self.session.remove(fromfilename)
            finally:
                remove_ta = False
                if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                    break

    @botslib.log_session
    def outcommunicate(self):
        ''' do ftp: send files. To be used via receive-dispatcher.
            each to be send file is transaction.
            each send file is transaction.
        '''
        #get right filename_mask & determine if fixed name (append) or files with unique names
        filename_mask = self.channeldict['filename'] if self.channeldict['filename'] else '*'
        if '{overwrite}' in filename_mask:
            filename_mask = filename_mask.replace('{overwrite}','')
            mode = 'w'
        else:
            mode = 'a'
        for row in botslib.query('''SELECT idta,filename,numberofresends
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                      AND status=%(status)s
                                      AND statust=%(statust)s
                                      AND tochannel=%(tochannel)s
                                        ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,
                                    'status':FILEOUT,'statust':OK}):
            try:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to = ta_from.copyta(status=EXTERNOUT)
                tofilename = self.filename_formatter(filename_mask,ta_from)
                fromfile = botslib.opendata_bin(row[str('filename')], 'rb')
                tofile = self.session.open(tofilename, mode)    # SSH treats all files as binary. paramiko doc says: b-flag is ignored
                tofile.write(fromfile.read())
                tofile.close()
                fromfile.close()
                #Rename filename after writing file.
                #Function: safe file writing: do not want another process to read the file while it is being written.
                if self.channeldict['mdnchannel']:
                    tofilename_old = tofilename
                    tofilename = botslib.rreplace(tofilename_old,self.channeldict['mdnchannel'])
                    self.session.rename(tofilename_old,tofilename)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,filename='sftp:/'+posixpath.join(self.dirpath,tofilename),numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename='sftp:/'+posixpath.join(self.dirpath,tofilename),numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)


class xmlrpc(_comsession):
    ''' General xmlrpc implementation. Xmlrpc is often quite specific.
        Probably you will have to script your own xmlrpc class, but this is a good starting point.
        From channel is used: usernaem, secret, host, port, path. Path is the function to be used/called.
    '''
    def connect(self):
        try:
            import xmlrpclib
        except ImportError:
            import xmlrpc.client as xmlrpclib
        uri = 'http://%(username)s%(secret)s@%(host)s:%(port)s'%self.channeldict
        self.filename = 'http://%(username)s@%(host)s:%(port)s'%self.channeldict    #used as 'filename' in reports etc
        session = xmlrpclib.ServerProxy(uri)
        self.xmlrpc_call = getattr(session,self.channeldict['path'])                #self.xmlrpc_call is called in communication

    @botslib.log_session
    def incommunicate(self):
        startdatetime = datetime.datetime.now()
        remove_ta = False
        while True:
            try:
                content = self.xmlrpc_call()
                if content is None:
                    break   #nothing (more) to receive.
                ta_from = botslib.NewTransaction(filename=self.filename,
                                                    status=EXTERNIN,
                                                    fromchannel=self.channeldict['idchannel'],
                                                    idroute=self.idroute)
                ta_to =   ta_from.copyta(status=FILEIN)
                remove_ta = True
                tofilename = unicode(ta_to.idta)
                tofile = botslib.opendata_bin(tofilename, 'wb')
                simplejson.dump(content, tofile, skipkeys=False, ensure_ascii=False, check_circular=False)
                tofile.close()
                filesize = os.path.getsize(botslib.abspathdata(tofilename))
            except:
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='xmlprc-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
                break   #break out of while loop (else this would be endless)
            else:
                ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                ta_from.update(statust=DONE)
            finally:
                remove_ta = False
                if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                    break

    @botslib.log_session
    def outcommunicate(self):
        ''' do xml-rpc: send files. To be used via receive-dispatcher.
            each to be send file is transaction.
            each send file is transaction.
        '''
        for row in botslib.query('''SELECT idta,filename,charset,numberofresends
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                    AND status=%(status)s
                                    AND statust=%(statust)s
                                    AND tochannel=%(tochannel)s ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,
                                    'status':FILEOUT,'statust':OK}):
            try:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to =   ta_from.copyta(status=EXTERNOUT)
                fromfile = botslib.opendata(row[str('filename')], 'rb',row[str('charset')])
                content = fromfile.read()
                fromfile.close()
                response = self.xmlrpc_call(content)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename=self.filename,numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)


class db(_comsession):
    ''' communicate with a database; directly read or write from a database.
        the user HAS to provide a userscript file in usersys/communicationscripts that does the actual import/export using **some** python database library.
        the userscript file should contain:
        - connect
        - (for incoming) incommunicate
        - (for outgoing) outcommunicate
        - disconnect
        Other parameters are passed, use them for your own convenience.
        Bots 'pickles' the results returned from the userscript (and unpickles for the translation).
    '''
    def connect(self):
        if self.userscript is None:
            raise botslib.BotsImportError(_('Channel "%(idchannel)s" is type "db", but no communicationscript exists.'),
                                {'idchannel':self.channeldict['idchannel']})
        #check functions bots assumes to be present in userscript:
        if not hasattr(self.userscript,'connect'):
            raise botslib.ScriptImportError(_('No function "connect" in imported communicationscript "%(communicationscript)s".'),
                                                {'communicationscript':self.scriptname})
        if self.channeldict['inorout'] == 'in' and not hasattr(self.userscript,'incommunicate'):
            raise botslib.ScriptImportError(_('No function "incommunicate" in imported communicationscript "%(communicationscript)s".'),
                                                {'communicationscript':self.scriptname})
        if self.channeldict['inorout'] == 'out' and not hasattr(self.userscript,'outcommunicate'):
            raise botslib.ScriptImportError(_('No function "outcommunicate" in imported communicationscript "%(communicationscript)s".'),
                                                {'communicationscript':self.scriptname})
        if not hasattr(self.userscript,'disconnect'):
            raise botslib.ScriptImportError(_('No function "disconnect" in imported communicationscript "%(communicationscript)s".'),
                                            {'communicationscript':self.scriptname})

        self.dbconnection = botslib.runscript(self.userscript,self.scriptname,'connect',channeldict=self.channeldict)

    @botslib.log_session
    def incommunicate(self):
        ''' read data from database.
            communication user script return 'db_objects'.
            This can be one edi-message or several edi-messages.
            if db_objects is a list or tuple is passed: each element of list/tuple is treated as seperate edi-message; each message is pickled and saved.
            if db_objects is None, nothing is done
            else: one message; the object is pickled and saved.
            So if you want all information from userscript to be passed as one edi message: pass as dict, eg {'data': <list of queries>}
        '''
        db_objects = botslib.runscript(self.userscript,self.scriptname,'incommunicate',channeldict=self.channeldict,dbconnection=self.dbconnection)
        if not db_objects:      #there should be a useful db_objects; if not just return (do nothing)
            return              
        if not isinstance(db_objects,(list,tuple)):
            db_objects = [db_objects]   #a list or tuple is expected: pack received object in a list (list with one member). 

        remove_ta = False
        for db_object in db_objects:
            try:
                ta_from = botslib.NewTransaction(filename=self.channeldict['path'],
                                                    status=EXTERNIN,
                                                    fromchannel=self.channeldict['idchannel'],
                                                    idroute=self.idroute)
                ta_to = ta_from.copyta(status=FILEIN)
                remove_ta = True
                tofilename = unicode(ta_to.idta)
                botslib.writedata_pickled(tofilename,db_object)
                filesize = os.path.getsize(botslib.abspathdata(tofilename))
            except:
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='db-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
            else:
                ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                ta_from.update(statust=DONE)
            finally:
                remove_ta = False

    @botslib.log_session
    def outcommunicate(self):
        ''' read file; pass unpickled object to user script.
        '''
        for row in botslib.query('''SELECT idta,filename,numberofresends
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                    AND status=%(status)s
                                    AND statust=%(statust)s
                                    AND tochannel=%(tochannel)s ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,'status':FILEOUT,'statust':OK}):
            try:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to = ta_from.copyta(status=EXTERNOUT)
                db_object = botslib.readdata_pickled(filename=self.ta_info['filename'])
                botslib.runscript(self.userscript,self.scriptname,'outcommunicate',channeldict=self.channeldict,dbconnection=self.dbconnection,db_object=db_object)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,filename=self.channeldict['path'],numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename=self.channeldict['path'],numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)

    def disconnect(self):
        botslib.runscript(self.userscript,self.scriptname,'disconnect',channeldict=self.channeldict,dbconnection=self.dbconnection)



class communicationscript(_comsession):
    ''' 
    For running an userscript for communication.
    Examples of use:
    - call external communication program
    - call external program that extract messages from ERP-database
    - call external program that imports messages in ERP system
    - communication method not available in Bots ***or use sub-classing for this***
    - specialised I/O wishes; eg specific naming of output files. (eg including partner name) ***beter: use sub-classing or have more user exits***
    place of communicationscript: bots/usersys/communicationscripts
    name of communicationscript: same name as channel (the channelID)
    in this communicationscript some functions will be called:
    -   connect (required)
    -   main (optional, 'main' should handle files one by one)
    -   disconnect  (required)
    arguments: dict 'channel' which has all channel attributes
    more parameters/data for communicationscript:   hard code this in communicationscript; or use bots.ini
    Different ways of working:
    1. for incoming files (bots receives the files):
        1.1 connect puts all files in a directory, there is no 'main' function. bots can remove the files (if you use the 'remove' switch of the channel).
        1.2 connect only builds the connection, 'main' is a generator that passes the messages one by one (using 'yield'). bots can remove the files (if you use the 'remove' switch of the channel).
    2. for outgoing files (bots sends the files):
        2.1 if there is a 'main' function: the 'main' function is called by bots after writing each file. bots can remove the files (if you use the 'remove' switch of the channel).
        2.2 no 'main' function: the processing of all the files can be done in 'disconnect'. bots can remove the files (if you use the 'remove' switch of the channel).
    ''' 
    def connect(self):
        if self.userscript is None or not botslib.tryrunscript(self.userscript,self.scriptname,'connect',channeldict=self.channeldict):
            raise botslib.BotsImportError(_('Channel "%(idchannel)s" is type "communicationscript", but no communicationscript exists.') ,
                                {'idchannel':self.channeldict})


    @botslib.log_session
    def incommunicate(self):
        startdatetime = datetime.datetime.now()
        if hasattr(self.userscript,'main'): #process files one by one; communicationscript has to be a generator
            remove_ta = False
            for fromfilename in botslib.runscriptyield(self.userscript,self.scriptname,'main',channeldict=self.channeldict):
                try:
                    ta_from = botslib.NewTransaction(filename = fromfilename,
                                                    status = EXTERNIN,
                                                    fromchannel = self.channeldict['idchannel'],
                                                    idroute = self.idroute)
                    ta_to = ta_from.copyta(status = FILEIN)
                    remove_ta = True
                    #open fromfile
                    fromfile = open(fromfilename, 'rb')
                    filesize = os.fstat(fromfile.fileno()).st_size
                    #open tofile
                    tofilename = unicode(ta_to.idta)
                    tofile = botslib.opendata_bin(tofilename, 'wb')
                    #copy
                    shutil.copyfileobj(fromfile,tofile,1048576)
                    fromfile.close()
                    tofile.close()
                except:
                    txt = botslib.txtexc()
                    botslib.ErrorProcess(functionname='communicationscript-incommunicate',errortext=txt,channeldict=self.channeldict)
                    if remove_ta:
                        try:
                            ta_from.delete()
                            ta_to.delete()
                        except:
                            pass
                else:
                    ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                    ta_from.update(statust=DONE)
                    if self.channeldict['remove']:
                        os.remove(fromfilename)
                finally:
                    remove_ta = False
                    if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                        break
        else:   #all files have been set ready by external communicationscript using 'connect'.
            frompath = botslib.join(self.channeldict['path'], self.channeldict['filename'])
            filelist = sorted(filename for filename in glob.iglob(frompath) if os.path.isfile(filename))
            remove_ta = False
            for fromfilename in filelist:
                try:
                    ta_from = botslib.NewTransaction(filename = fromfilename,
                                                    status = EXTERNIN,
                                                    fromchannel = self.channeldict['idchannel'],
                                                    idroute = self.idroute)
                    ta_to = ta_from.copyta(status = FILEIN)
                    remove_ta = True
                    fromfile = open(fromfilename, 'rb')
                    tofilename = unicode(ta_to.idta)
                    tofile = botslib.opendata_bin(tofilename, 'wb')
                    content = fromfile.read()
                    filesize = len(content)
                    tofile.write(content)
                    fromfile.close()
                    tofile.close()
                except:
                    txt = botslib.txtexc()
                    botslib.ErrorProcess(functionname='communicationscript-incommunicate',errortext=txt,channeldict=self.channeldict)
                    if remove_ta:
                        try:
                            ta_from.delete()
                            ta_to.delete()
                        except:
                            pass
                else:
                    ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                    ta_from.update(statust=DONE)
                    if self.channeldict['remove']:
                        os.remove(fromfilename)
                finally:
                    remove_ta = False
                    if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                        break


    @botslib.log_session
    def outcommunicate(self):
        #check if output dir exists, else create it.
        outputdir = botslib.join(self.channeldict['path'])
        botslib.dirshouldbethere(outputdir)
        #get right filename_mask & determine if fixed name (append) or files with unique names
        filename_mask = self.channeldict['filename'] if self.channeldict['filename'] else '*'
        if '{overwrite}' in filename_mask:
            filename_mask = filename_mask.replace('{overwrite}','')
            mode = 'wb'
        else:
            mode = 'ab'
        #select the db-ta's for this channel
        for row in botslib.query('''SELECT idta,filename,numberofresends
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                    AND status=%(status)s
                                    AND statust=%(statust)s
                                    AND tochannel=%(tochannel)s ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,
                                    'status':FILEOUT,'statust':OK}):
            try:    #for each db-ta:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to =   ta_from.copyta(status=EXTERNOUT)
                tofilename = self.filename_formatter(filename_mask,ta_from)
                #open tofile
                tofilename = botslib.join(outputdir,tofilename)
                tofile = open(tofilename, mode)
                #open fromfile
                fromfile = botslib.opendata_bin(row[str('filename')], 'rb')
                #copy
                shutil.copyfileobj(fromfile,tofile,1048576)
                fromfile.close()
                tofile.close()
                #one file is written; call external
                if botslib.tryrunscript(self.userscript,self.scriptname,'main',channeldict=self.channeldict,filename=tofilename,ta=ta_from):
                    if self.channeldict['remove']:
                        os.remove(tofilename)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename=tofilename,numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)

    def disconnect(self):
        botslib.tryrunscript(self.userscript,self.scriptname,'disconnect',channeldict=self.channeldict)
        if self.channeldict['remove'] and not hasattr(self.userscript,'main'):  #if bots should remove the files, and all files are passed at once, delete these files.
            outputdir = botslib.join(self.channeldict['path'], self.channeldict['filename'])
            for filename in glob.iglob(outputdir):
                if os.path.isfile(filename):
                    try:
                        os.remove(filename)
                    except:
                        pass

class trash(_comsession):
    @botslib.log_session
    def outcommunicate(self):
        ''' does output of files to 'nothing' (trash it).
        '''
        #select the db-ta's for this channel
        for row in botslib.query('''SELECT idta,filename,numberofresends
                                       FROM ta
                                      WHERE idta>%(rootidta)s
                                        AND status=%(status)s
                                        AND statust=%(statust)s
                                        AND tochannel=%(tochannel)s
                                        ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,
                                    'status':FILEOUT,'statust':OK}):
            try:    #for each db-ta:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to =   ta_from.copyta(status=EXTERNOUT)
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename='',numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)

class http(_comsession):
    scheme = 'http'     #scheme used for building url
    headers = None      #used if specified; eg {'content-type': 'application/json'}, # A dictionary with header params
    params = None      #used if specified; eg {'key1':'value1','key2':'value2'} -> http://server.com/path?key2=value2&key1=value1
    verify = False       #True, False or name of CA-file
    
    def connect(self):
        try:
            self.requests = botslib.botsbaseimport('requests')
        except ImportError:
            raise ImportError(_('Dependency failure: communicationtype "http(s)" requires python library "requests".'))
        if self.channeldict['username'] and self.channeldict['secret']:
            self.auth = (self.channeldict['username'], self.channeldict['secret'])
        else:
            self.auth = None
        self.cert = None
        self.url = botslib.Uri(scheme=self.scheme,hostname=self.channeldict['host'],port=self.channeldict['port'],path=self.channeldict['path'])

    @botslib.log_session
    def incommunicate(self):
        startdatetime = datetime.datetime.now()
        remove_ta = False
        while True:     #loop until no content is received or max communication time is expired
            try:
                #fetch via requests library
                outResponse = self.requests.get(self.url.uri(),
                                                auth=self.auth,
                                                cert=self.cert,
                                                params=self.params,
                                                headers=self.headers,
                                                verify=self.verify)
                if outResponse.status_code != self.requests.codes.ok: #communication not OK: exception
                    raise botslib.CommunicationError(_('%(scheme)s receive error, response code: "%(status_code)s".'),{'scheme':self.scheme,'status_code':outResponse.status_code})
                if not outResponse.content: #communication OK, but nothing received: break
                    break
                ta_from = botslib.NewTransaction(filename=self.url.uri(),
                                                    status=EXTERNIN,
                                                    fromchannel=self.channeldict['idchannel'],
                                                    idroute=self.idroute)
                ta_to =   ta_from.copyta(status=FILEIN)
                remove_ta = True
                tofilename = unicode(ta_to.idta)
                tofile = botslib.opendata_bin(tofilename, 'wb')
                tofile.write(outResponse.content)
                tofile.close()
                filesize = len(outResponse.content)
            except:
                txt = botslib.txtexc()
                botslib.ErrorProcess(functionname='http-incommunicate',errortext=txt,channeldict=self.channeldict)
                if remove_ta:
                    try:
                        ta_from.delete()
                        ta_to.delete()
                    except:
                        pass
                break
            else:
                ta_to.update(filename=tofilename,statust=OK,filesize=filesize)
                ta_from.update(statust=DONE)
            finally:
                remove_ta = False
                if (datetime.datetime.now()-startdatetime).seconds >= self.maxsecondsperchannel:
                    break
            

    @botslib.log_session
    def outcommunicate(self):
        '''not used now:
            if send as 'body':
                outResponse = requests.post(url, ..., data = filedata)
            elif send as 'multipart':
                outResponse = requests.post(url, ..., files={'file': filedata})
        '''
        for row in botslib.query('''SELECT idta,filename,numberofresends
                                    FROM ta
                                    WHERE idta>%(rootidta)s
                                      AND status=%(status)s
                                      AND statust=%(statust)s
                                      AND tochannel=%(tochannel)s
                                        ''',
                                    {'tochannel':self.channeldict['idchannel'],'rootidta':self.rootidta,
                                    'status':FILEOUT,'statust':OK}):
            try:
                ta_from = botslib.OldTransaction(row[str('idta')])
                ta_to = ta_from.copyta(status=EXTERNOUT)
                fromfile = botslib.opendata_bin(row[str('filename')], 'rb')
                content = fromfile.read()
                fromfile.close()
                #communicate via requests library
                outResponse = self.requests.post(self.url.uri(),
                                                auth=self.auth,
                                                cert=self.cert,
                                                params=self.params,
                                                headers=self.headers,
                                                data=content,
                                                verify=self.verify)
                if outResponse.status_code != self.requests.codes.ok:
                    raise botslib.CommunicationError(_('%(scheme)s send error, response code: "%(status_code)s".'),{'scheme':self.scheme,'status_code':outResponse.status_code})
            except:
                txt = botslib.txtexc()
                ta_to.update(statust=ERROR,errortext=txt,filename=self.url.uri(filename=row[str('filename')]),numberofresends=row[str('numberofresends')]+1)
            else:
                ta_to.update(statust=DONE,filename=self.url.uri(filename=row[str('filename')]),numberofresends=row[str('numberofresends')]+1)
            finally:
                ta_from.update(statust=DONE)

    def disconnect(self):
        pass


class https(http):
    ''' testing results:
        - http server has self-signed certificate; caCert=None, verify='/pathtocert/ca.pem': OK, certificate is verified.
        - http server has self-signed certificate; caCert points to same certificate, verify = None: OK, certificate is verified.
        - http server has self-signed certificate; verify = True: OK, but certificate is not verified.
    '''
    scheme = 'https'   #scheme used for building url
    verify = True     #verify host certificate: True, False or path to CA bundle eg '/pathtocert/ca.pem'
    caCert = None     #None or path to CA bundle eg '/pathtocert/ca.pem', Specify if https server has an unrecognized CA. Looks like verify needs to be None in order to work(??)
    
    def connect(self):
        #option to set environement variable for requests library; use if https server has an unrecognized CA
        super(https,self).connect()
        if self.caCert:
            os.environ['REQUESTS_CA_BUNDLE'] = self.caCert
        if self.channeldict['certfile'] and self.channeldict['keyfile']:
            self.cert = (self.channeldict['certfile'], self.channeldict['keyfile'])
        else:
            self.cert = None
