Channel Scripting
=================
When the standard communication of bots does not fit your needs, use communicationscripts.
Instruction to make a channel script:

* There must be channel in bots-monitor (or make a new one)
* Make a communicationscript with the **same name** as the channelID
* Place the communicationscript in ``bots/usersys/communicationscripts/channelid.py``

**Use cases**

* Communication method not provided by bots
* Existing communication needs customization
* Call external program to write edi message to your ERP system.
* Additional requirements: Eg. use partner name or order number in output file name.
* Control archive file naming

**Types of communication scripts**

#. Small user exits: at certain places in normal communication a user script is called. Examples of `small user exits <#small-user-exits>`_
#. Subclass: take-over of (parts of) communication script: user script subclasses existing communication type.
#. Communication type ``communicationscript``. Bots tries to do the bots-handling of files, you provide the communication details. Examples of `communication type 'communicationscript' <communication-type-communicationscript>`_

Small User Exits
----------------

Some examples of small user exists are below:

**Example to Filter email attachments**: 
Some edi-partners send signatures etc in their email. Script does a simple check if incoming attachment starts with 'UNB'. (Note: Bots treats any text in the email body as another "attachment")

.. code-block:: python

    def accept_incoming_attachment(channeldict,ta,charset,content,contenttype,*args,**kwargs):
        if 'UNB' in content[0:50]:
            return True   #attachments is OK
        else:
            return False  #skip this attachment

**Example to Set email subject**: 
Some edi-partners send signatures etc in their email. By default bots uses a number for emails. Sometimes you want a more meaningfull subject.

.. code-block:: python

    def subject(channeldict,ta,subjectstring,content,*args,**kwargs):
        ta.synall()        #needed to get access to attributes of object ta (eg ta.frompartner)
        return 'EDI messages from ' + ta.frompartner + '_' + subjectstring

**Exapmle to Name archive file same as input file**: 
Not needed for bots 3.x where you can **do this via setting in bots.ini**

.. code-block:: python

    import os
    import bots.botslib as botslib

    def archivename(channeldict,idta,filename,*args,**kwargs):
         taparent=botslib.OldTransaction(idta=idta)
         ta_list = botslib.trace_origin(ta=taparent,where={'status':EXTERNIN})
         archivename = os.path.basename(ta_list[0].filename)
         return archivename 

**Example to Set the archive path**: 
Path root is set in channel. Add sub-dir per date, then sub-dir per channel under it.

.. code-block:: python

    import time
    import bots.botslib as botslib

    def archivepath(channeldict,*args,**kwargs):
        archivepath = botslib.join(channeldict['archivepath'],time.strftime('%Y%m%d'),channeldict['idchannel'])
        return archivepath

**Example to Partners in the output file name**: 
Not needed for bots 3.x where you can **do this via file name in GUI**.

.. code-block:: python

    def filename(channeldict,filename,ta,*args,**kwargs):
        ta.synall()        #needed to get access to attributes of object ta (eg ta.frompartner)
        return ta.frompartner + '_' + ta.topartner + '_' + filename

**Example to Name the output file from botskey**:
``botskey`` can be set in grammar or mapping, eg. from customer's order number. If no botskey is found, the default file naming method will be used. 
Syntax must contain 'merge':False. Not needed for bots 3.x where you can **do this via file name in GUI**.

.. code-block:: python

    def filename(channeldict,filename,ta,*args,**kwargs):
        ta.synall()
        if ta.botskey:
            return filename + ta.botskey
        else:
            return filename

**Example to Name the output file same as input file**: 
Syntax must contain **merge**:False. Not needed for bots 3.x where you can **do this via file name in GUI**.

.. code-block:: python

    import os
    import bots.botslib as botslib

    def filename(channeldict,filename,ta,*args,**kwargs):
        ta_list = botslib.trace_origin(ta=ta,where={'status':EXTERNIN})
        filename_in = os.path.basename(ta_list[0].filename) # just filename, remove path
        return filename + filename_in

Subclassing
-----------

It is possible to overwrite bots communication methods completely.
This is done using python subclassing.
Again, as with all communication scripting there should be a file in ``usersys/communicationscripts`` with the same name as the channel (and extension ``.py``)

**Example 1**: 
In this case communication-type of the channel is 'file'. Bots will check the communication-script file if there is a class called 'file' and use that.
The class 'file' subclasses the standard 'file' method of bots.

.. code-block:: python

    import bots.communication as communication

    class file(communication.file):
        def connect(self,*args,**kwargs):
            #do the preparing work
            print 'in connect method'

**Example 2**: 
In this case communication-type of the channel is 'ftp'. The class 'ftp' subclasses the standard 'ftp' method of bots. The 'outcommunicate' method of the ftp class is taken over with this implementation.

.. code-block:: python

    import bots.communication as communication
    import bots.botslib as botslib
    from bots.botsconfig import *

    class ftp(communication.ftp):
        @botslib.log_session
        def outcommunicate(self,*args,**kwargs):
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
                    ta_from = botslib.OldTransaction(row['idta'])
                    ta_to = ta_from.copyta(status=EXTERNOUT)
                    tofilename = self.filename_formatter(filename_mask,ta_from)
                    if self.channeldict['ftpbinary']:
                        fromfile = botslib.opendata(row['filename'], 'rb')
                        self.session.storbinary(mode + tofilename, fromfile)
                    else:
                        fromfile = botslib.opendata(row['filename'], 'r')
                        self.session.storlines(mode + tofilename, fromfile)
                    fromfile.close()
                except:
                    txt = botslib.txtexc()
                    ta_to.update(statust=ERROR,errortext=txt,filename='ftp:/'+posixpath.join(self.dirpath,tofilename),numberofresends=row['numberofresends']+1)
                else:
                    ta_to.update(statust=DONE,filename='ftp:/'+posixpath.join(self.dirpath,tofilename),numberofresends=row['numberofresends']+1)
                finally:
                    ta_from.update(statust=DONE)

**Example 3**: 
In this case communication-type of the channel is 'ftp' or 'sftp'. The class 'ftp' subclasses the standard 'ftp' method of bots. The 'disconnect' method of the ftp class is taken over with this implementation. The bots channel should be configured to upload either to a 'tmp' sub-directory, or with a '.tmp' extension. This function renames the files once uploads are complete, this preventing the recipient from processing partial files.

.. code-block:: python

    '''
    For safety when uploading to ftp servers, it is a good idea to rename/move
    files once complete. This prevents the receiver processing partial files.
    When all files have been sent and before the session is disconnected, the
    files are renamed so the receiver can process them.

    Two methods are available:
     1. Append extension ".tmp" to the channel filename
        This method is simpler, but the receiver may still process the
        .tmp files if it does not look for specific extensions to process.
     2. Append subdirectory "/tmp" to the channel path
        This requires an extra directory created on the server, you may not
        be authorised to do this.

    Subclassing of ftp.disconnect. Import this to your communicationscript (ftp or sftp as required):
        from _ftp_rename import ftp
        from _ftp_rename import sftp

    Mike Griffin  4/09/2013

    '''

    import bots.communication as communication
    import bots.botslib as botslib
    import bots.botsglobal as botsglobal

    class ftp(communication.ftp):
        def disconnect(self,*args,**kwargs):

            # rename files to remove .tmp extensions
            if self.channeldict['filename'].endswith('.tmp'):
                for f in self.session.nlst():
                    if f.endswith('.tmp'):
                        try:
                            self.session.rename(f,f[:-4])
                        except:
                            pass

            # rename files from tmp subdirectory to parent directory
            if self.channeldict['path'].endswith('/tmp'):
                for f in self.session.nlst():
                    try:
                        self.session.rename(f,'../%s' %f)
                    except:
                        pass

            try:
                self.session.quit()
            except:
                self.session.close()
            botslib.settimeout(botsglobal.ini.getint('settings','globaltimeout',10))

    class sftp(communication.sftp):
        def disconnect(self,*args,**kwargs):

            # rename files to remove .tmp extensions
            if self.channeldict['filename'].endswith('.tmp'):
                for f in self.session.listdir('.'):
                    if f.endswith('.tmp'):
                        try:
                            self.session.rename(f,f[:-4])
                        except:
                            pass

            # rename files from tmp subdirectory to parent directory
            if self.channeldict['path'].endswith('/tmp'):
                for f in self.session.listdir('.'):
                    try:
                        self.session.rename(f,'../%s' %f)
                    except:
                        pass

            self.session.close()
            self.transport.close()

**Example 4**: 
In this case communication-type of the channel is 'ftp'. The class 'ftp' subclasses the standard 'ftp' method of bots. The 'disconnect' method of the ftp class is taken over with this implementation. This provides a way to submit a remote command to the ftp server, for example to run a program on that server. The bots channel is configured with the command in the 'parameters' field.

.. code-block:: python

    '''
    Before disconnecting, send a remote command
    Channel "parameters" holds the command to send

    Subclassing of ftp.disconnect. Import this to your communicationscript:
        from _ftp_remote_command import ftp

    Mike Griffin  13/09/2013
    '''

    import bots.communication as communication
    import bots.botsglobal as botsglobal

    class ftp(communication.ftp):
        def disconnect(self,*args,**kwargs):

            # send remote command to ftp server
            botsglobal.logger.info('Send remote command: %s',self.channeldict['parameters'])
            self.session.sendcmd('RCMD %s' %self.channeldict['parameters'])

            try:
                self.session.quit()
            except:
                self.session.close()
            botslib.settimeout(botsglobal.ini.getint('settings','globaltimeout',10))

Communication type ``communicationscript``
------------------------------------------

In this case, the channel must be configured with Type: ``communicationscript``.
In the communicationscript some functions will be called:

* connect (required)
* main (optional, 'main' should handle files one by one)
* disconnect (optional)

Different ways of working:

#. For incoming files (bots receives the files):
    * Connect puts all files in a directory, there is no 'main' function. bots can remove the files (if you use the ``remove`` switch of the channel). See example 1.
    * Connect only builds the connection, ``main`` is a generator that passes the messages one by one (using ``yield``). bots can remove the files (if you use the ``remove`` switch of the channel). See example 2. 
#. For outgoing files (bots sends the files):
    * No ``main`` function: the processing of all the files can be done in ``disconnect``. bots can remove the files (if you use the ``remove`` switch of the channel). See example 3.
    * If there is a ``main`` function: the ``main`` function is called by bots after writing each file. bots can remove the files (if you use the ``remove`` switch of the channel). See example 4.

**Example 1: incoming files via external program all at once** 

Calls an external program. Think eg of a specific communication module for a VAN. All files are received at once to a folder, then processed like a normal file channel.

.. code-block:: python

    import subprocess

    def connect(channeldict,*args,**kwargs):
        subprocess.call(['C:/Program files/my VAN/comms-module.exe','-receive'])

**Example 2: incoming files via external program one by one**

TODO: make a valid example using yield. main is a generator.

.. code-block:: python

    import subprocess

    def connect(channeldict,*args,**kwargs):
        ''' function does nothing but it is required.'''
        pass

    def main(channeldict,*args,**kwargs):

        yield ?

**Example 3: outgoing files via external program all at once**

Calls an external program. Think eg of a specific communication module for a VAN.
In this example the 'disconnect' script is called after all files are written to directory; in disconnect all files are passed to external communication-module.

.. code-block:: python

    import subprocess
    import os

    def connect(channeldict,*args,**kwargs):
        ''' function does nothing but it is required.'''
        pass

    def disconnect(channeldict,*args,**kwargs):
        subprocess.call(['C:/Program files/my VAN/comms-module.exe','-send',os.path.join(channeldict['path'],'\*.xml'])

**Example 4: outgoing files via external program one by one**

Calls an external program. Think eg of a specific communication module for a VAN.
In this example the 'main' script is called for each outgoing file.

.. code-block:: python

    import subprocess

    def connect(channeldict,*args,**kwargs):
        ''' function does nothing but it is required.'''
        pass

    def main(channeldict,filename,ta,*args,**kwargs):
        subprocess.call(['C:/Program files/my VAN/comms-module.exe','-send',filename])

**Example 5: outgoing files to a printer**

Send data (eg. ZPL code to print fancy labels) directly to a Windows configured printer. The printer can be defined in Windows either as "Generic/Text Only" or with the proper driver, because this script just sends raw data, bypassing the driver.

| Dependencies: Requires pywin32
| Reference: http://timgolden.me.uk/pywin32-docs/win32print.html


.. code-block:: python

    import os
    import win32print
    import bots.transform as transform

    def connect(channeldict,*args,**kwargs):
        ''' function does nothing but it is required.'''
        pass

    def main(channeldict,filename,ta,*args,**kwargs):

        # set printer values required
        ta.synall()
        printer = transform.partnerlookup(ta.topartner,'attr1')
        jobname = ta.botskey

        # read the output file
        with open(filename,'r') as content_file:
            content = content_file.read()

        # send data to the printer
        hPrinter = win32print.OpenPrinter(printer)
        hJob = win32print.StartDocPrinter(hPrinter,1,(jobname,None,'RAW'))
        win32print.WritePrinter(hPrinter,content)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)
