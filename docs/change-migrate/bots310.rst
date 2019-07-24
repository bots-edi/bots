Bots 3.1.0
==========

* Bots 3.1.0RC was released 2013-07-17.
* No database migration is needed.
* Some small changes in x12 grammar might be needed, see details below.

Migration notes (from 3.0.0)
----------------------------

    **Editype x12: in ISA definition 'ISA11' has to be conditional**

    * Bots 3.1.0 supports the repeating character (for ISA-versions >= 00403).
    * If you use this, ISA11 has to be conditional in definition; file ``usersys/grammars/x12/envelope.py``, was:
        ``['ISA11','M',(1,1),'AN'],``
    * becomes in 3.1.0:
        ``['ISA11','C',(1,1),'AN'],``
    * This change also works for older ISA-version. Advised is to use this.

    **Editype x12, edifact, tradacoms: different handling of syntax parameters**

    * Bots handles the syntax parameters differently. In bots 3.0 and earlier this was somewhat 'fuzzy'. This works now like:
        * default syntax parameters are overruled by envelope parameters,
        * are overruled by message parameters,
        * are overruled by frompartner parameters,
        * are overruled by topartner parameters.

    * Most common problem will be for x12: message grammars had by default in syntax parameters:
        ``'version' : '00403',``
    * Formerly this was not used; now it is used.
    * This might lead to sending another version of ISA-envelope, this is probably not what you want!
    * Solution: delete (or uncomment) the ``version`` syntax parameter for message grammar.

    .. note::
        The ISA-version you send now is probably in ``usersys/grammars/x12/x12.py``

    **Editype fixed and idoc: 'startrecordID' and 'endrecordID' not longer used**

    * Bots calculates this automatically now.
    * Bots also checks for all used records if this is used the same over all records.
    * This might lead to errors.
    * **Solution**: BOTSID should have correct length in all records and be at correct position.

    **Envelope scripts**

    * was:
        ``self._openoutenvelope(self.ta_info['editype'],self.ta_info['envelope'])``
    * becomes in 3.1.0:
        ``self._openoutenvelope()``

    **Route scripting**

    Function transform.translate is changed:parameters startstatus,endstatus,idroute,rootidta have to be explicitly indicated (no more defaults).

Changes   
-------
   
    **Interface (GUI)**

    #. Improved and simplified many screens. Eg only filename is displayed (takes less space), a pop-up show full path name
        #. incoming
        #. outgoing
        #. detail
        #. document; split up to incoming and outgoing screens;
        #. confirm
    #. Show in configuration screen if there are routescripts, communicationscripts, mappingscripts, grammars. Routescripts etc can be viewed.
    #. Partners and partnergroups are split up (via menu and screens).
    #. Added a cancel button in configuration editing.
    #. Added a choice list for routes in Configuration-Confirm.
    #. Display edifact/x12: display per segment for better readability.
    #. Show correct number of messages for resends.
    #. Email error report is extended with information about errors.
    #. Improved view/edit counters screen.
    #. In errors the correct name of eg grammars is shown. This was confusing (using sometimes '.' instead of '\' etc). 

   **Highlights**

    #. Extra debug option: check all get/getloop if OK with grammars.
    #. Support for repeating elements is added (x12/edifact).
    #. Simplified logic of syntax reading: default syntax is overridden by envelope syntax is overridden by message sytax is overridden by partner-syntax.
    #. Added: fixed records can now be 'nobotsid': one record type, split to messages via field.
    #. Generating 997's can be done/manipulated via user script .

    **Smaller changes**

    #. Skip empty json elements in incoming files.
    #. StartrecordID and endrecordID are not needed anymore for in grammars for fixed message/idoc, bots calculates this now.
    #. Small improvements and bug fixes in XML reading/writing.
    #. QUERIES now also support callables.
    #. Xml2botsgrammar: sort fields in recorddefs, use empty elements in grammar.
    #. If 'alt' transaltion is not found, use default translation.
    #. More consistent handling of exceptions and logging (coding only).
    #. Fixed problems starting bots-engine from webserver in less common situations.
    #. Get correct incoming filename for re-receive.
    #. Removed code for old database connector and code-conversion via file.
    #. Automaticretry: first run only initialization (to avoid sending moch older files).
    #. Explicitly set for outgoing file: no automatic retry.
    #. Plugins: for different environments, path and testpath in channels are also relocated .
    #. Plugins: handling of unicode-characters is now correct.
    #. Add mapping function: getdecimal(). Returns a python decimal; if not found or non-valid input: returns decimal 0.
    #. For csv and fixed with 'noBOTSID': nextmessageblock can check for multiple fields, eg: ``nextmessageblock = ([{'BOTSID':'lin','field1':None},{'BOTSID':'lin','field2':None}])``
    #. When deleting configuration items via 'bulk delete': make a backup plugin first.

    **Bug fixes**

    #. There was a missing import in ``xml2botsgrammar``
    #. Logging of mapping debug did not work in 3.0
    #. Correct handling of resends/rereceives for already resend/received files
    #. Fixed bug in automaticretrycommunication
    #. Confirmation can now be asked via channel-rule.
    #. if multiple commands in run: reports etc are based on timestamp. This messed up the relation between runs and eg incoming files. 
