Syntax Parameters
=================

* Syntax contains parameters that are used in reading or writing edi-files.
* The complete list of syntax parameters including default values is in bots/grammars.py (in the classes of the editypes).
* Syntax is a python dict (dictionary).

Example of syntax parameters:

.. code-block:: python

    syntax = { 
            'charset'                  : 'uft-8', #character set is utf-8
            'checkfixedrecordtooshort' : True,    #check if fixed record is to short
            'indented'                 : True,    #xml: produced indented output
            'decimaal'                 : ',',     #decimal sign is ', '
            }

Usage and Overriding
--------------------

Syntax parameters can be set at different places; these settings override (somewhat luke CSS).
The order in which overriding is done:

* default values are in ``bots/grammars.py`` (per editype). **Do not change these values!**
* envelope grammar (eg for x12: ``bots/usersys/grammars/x12/x12.py``, for edifact: ``bots/usersys/grammars/edifact/edifact.py``)
* message grammar
* frompartner grammar (eg in ``bots/usersys/partners/x12/partnerID.py``)
* topartner grammar (eg in ``bots/usersys/partners/x12/partnerID.py``)

.. rubric::
    Example 1: edifact charset

* default value is UNOA
* value in envelope (``edifact.py``) is UNOA
* for invoices: a description is used so the message grammar for invoices has charset UNOC
* retailer ABC insists on receiving invoices as UNOA, so this is indicated in the topartner grammar.

.. rubric::
    Example 2: x12 element separator

* in grammar.py: ``'field_sep':'*'`` (bots default value)
* in x12.py: ``'field_sep':'|'`` (default value company uses when sending x12)
* retailer ABC insists: ``'field_sep':'\x07'`` (that is ``\a``, or BEL)

List of most useful Syntax Parameters
-------------------------------------

.. csv-table:: 
    :header: "Parameter", "Direction", "Description"

    "add_crlfafterrecord_sep","Out","put **extra** character after a record/segment separator. Value: string, typically ``\n`` or ``\r\n``. I use this for x12/edifact while testing: output is better to read. Most partenrs can handles these file, but they are slightly bigger. See also parameter ``indent``."
    "acceptspaceinnumfield","In","Do not raise error when numeric field contains only spaces but assume value is 0"
    "allow_lastrecordnotclosedproperly","In","(csv) allows last record not to have record separator"
    "charset","In","charset to use; (edifact, xml) is overridden by charset-declaration in content."
    "","Out","charset to use in output. Bots is quite strict in this."
    "checkcharsetin","In","what to do for chars not in charset. Possible values 'strict' (gives error) or 'ignore' (skip the characters not in the charset) or 'botsreplace' (replace with char as set in bots.ini; default is space)"
    "checkcharsetout","Out","what to do for chars not in charset. Possible values 'strict' (gives error), 'ignore' (skip the characters not in the charset) or 'botsreplace' (replace with char as set in bots.ini; default is space)"
    "checkfixedrecordtoolong","In","(fixed): warn if record too long. Possible values: True/False, default: True"
    "checkfixedrecordtooshort","In","fixed): warn if record too short. Possible values: True/False, default: False"
    "checkunknownentities","In/Out","(xml,JSON) skip unknown attributes/elements (instead of raising an error)"
    "contenttype","Out","content-type of translated file; used as mime-envelope of email"
    "decimaal","In/Out","decimal point; default is '.'. For edifact: read from UNA-string if present."
    "endrecordID","In","(fixed) end position of record ID; value: number, default 3. See startrecordID"
    "envelope","Out","envelope to use; if nothing specified: no envelope - files are just copied/appended. For csv output, use the value 'csvheader' to include a header line with field names."
    "envelope-template","Out","(template/html) the template for the envelope."
    "escape","In/Out","escape character used. Default: edifact: '?'."
    "field_sep","In/Out","field separator. Default: edifact: '+'; csv: ':' x12: '')"
    "forcequote","Out","(csv) Possible values: 1 (quote only if necessary); 1 (always quote), 2 (quote only alfanum). Default is 1"
    "forceUNA","Out","(edifact) Always use UNA-segment in header, even if not needed. Possible values: True, False. Default: False."
    "indented","Out","(xml, json) Indent message for human readability. Nice while testing. Indented messages are syntactically OK, but are much bigger. Possible values: True, False. Default: False. See also add_crlfafterrecord_sep"
    "merge","Out","if merge is True: merge translated messages to one file (for same sender, receiver, messagetype, channel, etc). Related: envelope. Possible values: True, False."
    "namespace_prefixes","Out","(xml) to over-ride default namespace prefixes (ns0, ns1 etc) for outgoing xml. is a list, consisting of tuples, each tuple consists of prefix and uri. Example: ``'namespace_prefixes':[('orders','http://www.company.com/EDIOrders'),]``"
    "noBOTSID","In/Out","(csv) use if records contain no real record ID."
    "output","Out","(template) values: 'xhtml-strict'"
    "pass_all","In","(csv, fixed) if only one recordtype and no nextmessageblock; False: pass record for record to mapping; True: Pass all records to mapping."
    "quote_char","In/Out","(csv) char used as quote symbol"
    "record_sep","In/Out","char used as record separator. Defaults: edifact: ''' (single quote); fixed: '\n'; x12: '~'"
    "record_tag_sep","Out","(tradacoms) separator used after segment tag. Defaults: '='"
    "replacechar","Out","(x12) if a separator value is found in the data, replace with this character. Default: '' (raise error when separator value in data)."
    "skip_char","In","char(s) to skip, not interpreted when reading file. Typically '\n' in edifact."
    "skip_firstline","In","(csv) skip first line (often contains field names). Possible values: True/False/Integer number of lines to skip, default: False. True skips 1 line."
    "startrecordID","In","(fixed) start position of record ID; value: number, default 0. See endrecordID"
    "template","Out","(template) Template to use for HTML-output."
    "triad","In","triad (thousands) symbol used (e.g. '1,000,048.35'). If specified, this symbol is skipped when parsing numbers. By default numbers are expected to come without thousands separators."
    "version","Out","(edifact,x12) version of standard generate. Value: string, typically: '3' in edifact or '004010' for x12."
    "wrap_length","Out","Wraps the output to a new line when it exceeds this length. value: number, default 0. Typically used in conjunction with 'add_crlfafterrecord_sep':'' (blank). Note: does not affect envelope of message."
