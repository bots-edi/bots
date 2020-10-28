# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json as simplejson
import sys
import time

if sys.version_info[0] > 2:
    basestring = unicode = str
try:
    import cdecimal as decimal
except ImportError:
    import decimal

NODECIMAL = decimal.Decimal(1)
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from collections import OrderedDict
from django.utils.translation import ugettext as _

#bots-modules
from . import botslib
from . import botsglobal
from . import message
from . import grammar
from . import node
from .botsconfig import *

#avro
from fastavro import writer as avrowriter
from fastavro.schema import load_schema
from uuid import UUID

def outmessage_init(**ta_info):
    ''' dispatch function class Outmessage or subclass
        ta_info: needed is editype, messagetype, filename, charset, merge
    '''
    try:
        classtocall = globals()[ta_info['editype']]
    except KeyError:
        raise botslib.OutMessageError(_('Unknown editype for outgoing message: %(editype)s'), ta_info)
    return classtocall(ta_info)


class Outmessage(message.Message):
    ''' abstract class; represents a outgoing edi message.
        subclassing is necessary for the editype (csv, edi, x12, etc)
        A tree of nodes is build form the mpaths received from put()or putloop(). tree starts at self.root.
        Put() recieves mpaths from mappingscript
        The next algorithm is used to 'map' a mpath into the tree:
            For each part of a mpath: search node in 'current' level of tree
                If part already as a node:
                    recursively search node-children
                If part not as a node:
                    append new node to tree;
                    recursively append next parts to tree
        After the mappingscript is finished, the resulting tree is converted to self.lex_records.
        These lex_records are written to file.
    '''

    def __init__(self, ta_info):
        super(Outmessage, self).__init__(ta_info)
        # message tree; build via put()-interface in mappingscript. Initialise with empty dict
        self.root = node.Node(record={})

    def messagegrammarread(self, typeofgrammarfile):
        ''' read grammar for a message/envelope.
            (try to) read the topartner dependent grammar syntax.
        '''
        super(Outmessage, self).messagegrammarread(typeofgrammarfile)
        #read partner-syntax. Use this to always overrule values in self.ta_info
        if self.ta_info.get('frompartner'):
            try:
                partnersyntax = grammar.grammarread(self.ta_info['editype'], self.ta_info[
                                                    'frompartner'], typeofgrammarfile='partners')
                self.ta_info.update(partnersyntax.syntax)  # partner syntax overrules!
            except botslib.BotsImportError:
                pass  # No partner specific syntax found (is not an error).
        if self.ta_info.get('topartner'):
            try:
                partnersyntax = grammar.grammarread(self.ta_info['editype'], self.ta_info[
                                                    'topartner'], typeofgrammarfile='partners')
                self.ta_info.update(partnersyntax.syntax)  # partner syntax overrules!
            except botslib.BotsImportError:
                pass  # No partner specific syntax found (is not an error).

    def writeall(self):
        ''' writeall is called for writing all 'real' outmessage objects; but not for envelopes.
            writeall is call from transform.translate()
        '''
        self.messagegrammarread(typeofgrammarfile='grammars')
        self.checkmessage(self.root, self.defmessage)
        self.checkforerrorlist()
        self.nrmessagewritten = 0
        if self.root.record:  # root record contains information; write whole tree in one time
            self.multiplewrite = False
            self._initwrite()
            self._write(self.root)
            self.nrmessagewritten = 1
            self.ta_info['nrmessages'] = self.nrmessagewritten
            self._closewrite()
        elif not self.root.children:
            raise botslib.OutMessageError(_('No outgoing message'))  # then there is nothing to write...
        else:
            self.multiplewrite = True
            self._initwrite()
            for childnode in self.root.children:
                self._write(childnode)
                self.nrmessagewritten += 1
            #'write back' the number of messages. Tricky thing here is that sometimes such a structure is indeed one message: eg csv without BOTS iD.
            #in general: when only one type of record in recorddefs (mind: for xml this is not useful) no not writeback the count as nrofmessages
            #for now: always write back unless csv of fixed.
            if not isinstance(self, (csv, fixed)):
                self.ta_info['nrmessages'] = self.nrmessagewritten
            self._closewrite()

    def _initwrite(self):
        botsglobal.logger.debug('Start writing to file "%(filename)s".', self.ta_info)
        self._outstream = botslib.opendata(self.ta_info['filename'], 'wb', charset=self.ta_info[
                                           'charset'], errors=self.ta_info['checkcharsetout'])

    def _closewrite(self):
        botsglobal.logger.debug('End writing to file "%(filename)s".', self.ta_info)
        self._outstream.close()

    def _write(self, node_instance):
        ''' the write method for most classes.
            tree is serialised to lex_records; lex_records are written to file.
            Classses that write using other libraries (xml, json, template, db) use specific write methods.
        '''
        self.tree2records(node_instance)
        value = self.record2string(self.lex_records)
        wrap_length = int(self.ta_info.get('wrap_length', 0))
        if wrap_length:
            try:
                for i in range(0, len(value), wrap_length):  # split in fixed lengths
                    self._outstream.write(value[i:i + wrap_length] + '\r\n')
            except UnicodeError as msg:
                content = botslib.get_relevant_text_for_UnicodeError(msg)
                raise botslib.OutMessageError(_('[F50]: Characters not in character-set "%(char)s": %(content)s'),
                                              {'char': self.ta_info['charset'], 'content': content})
        else:
            try:
                self._outstream.write(value)
            except UnicodeError as msg:
                content = botslib.get_relevant_text_for_UnicodeError(msg)
                raise botslib.OutMessageError(_('[F50]: Characters not in character-set "%(char)s": %(content)s'),
                                              {'char': self.ta_info['charset'], 'content': content})

    def tree2records(self, node_instance):
        self.lex_records = []  # tree of nodes is flattened to these lex_records
        self._tree2recordscore(node_instance, self.defmessage.structure[0])

    def _tree2recordscore(self, node_instance, structure):
        ''' Write tree of nodes to flat lex_records.
            The nodes are already sorted
        '''
        self._tree2recordfields(node_instance.record, structure)  # write node->lex_record
        for childnode in node_instance.children:
            botsid_childnode = childnode.record['BOTSID'].strip()  # speed up: use local var
            botsidnr_childnode = childnode.record['BOTSIDnr']  # speed up: use local var
            for structure_record in structure[LEVEL]:  # for structure_record of this level in grammar
                # check if is is the right node
                if botsid_childnode == structure_record[ID] and botsidnr_childnode == structure_record[BOTSIDNR]:
                    self._tree2recordscore(childnode, structure_record)  # use rest of index in deeper level
                    break  # childnode was found and used; break to go to next child node

    def _tree2recordfields(self, noderecord, structure_record):
        ''' from noderecord->lex_record; use structure_record as guide.
            complex because is is used for: editypes that have compression rules (edifact), var editypes without compression, fixed protocols
        '''
        lex_record = []  # the record build; list (=record) of dicts (=fields).
        recordbuffer = []
        for field_definition in structure_record[FIELDS]:  # loop all fields in grammar-definition
            if field_definition[ISFIELD]:  # if field (no composite)
                if field_definition[MAXREPEAT] == 1:  # if non-repeating
                    field_has_data = False
                    if field_definition[ID] in noderecord and noderecord[field_definition[ID]]:
                        #field exists in outgoing message and has data
                        field_has_data = True
                        recordbuffer.append({VALUE: noderecord[field_definition[ID]],
                                             SFIELD: 0, FORMATFROMGRAMMAR: field_definition[FORMAT]})
                    elif self.ta_info['stripfield_sep']:
                        #no data and field not needed: write new empty field to recordbuffer;
                        recordbuffer.append({VALUE: '', SFIELD: 0, FORMATFROMGRAMMAR: field_definition[FORMAT]})
                    else:
                        # no data but field is needed: initialise empty field. For eg fixed and
                        # csv: all fields have to be present
                        field_has_data = True
                        value = self._initfield(field_definition)
                        recordbuffer.append({VALUE: value, SFIELD: 0, FORMATFROMGRAMMAR: field_definition[FORMAT]})
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                else:  # repeating field
                    field_has_data = False
                    if field_definition[ID] in noderecord:  # field exists in outgoing message
                        type_of_field = 0  # first field in repeat is marked as a field (not as repeat).
                        fieldbuffer = []  # buffer for this repeating field.
                        for field in noderecord[field_definition[ID]]:
                            if field:
                                field_has_data = True
                                fieldbuffer.append({VALUE: field, SFIELD: type_of_field,
                                                    FORMATFROMGRAMMAR: field_definition[FORMAT]})
                                recordbuffer += fieldbuffer
                                fieldbuffer = []
                            else:
                                fieldbuffer.append({VALUE: '', SFIELD: type_of_field,
                                                    FORMATFROMGRAMMAR: field_definition[FORMAT]})
                            type_of_field = 2  # mark rest of repeats as repeat.
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                    else:
                        recordbuffer.append({VALUE: '', SFIELD: 0, FORMATFROMGRAMMAR: field_definition[FORMAT]})
            else:  # if composite
                if field_definition[MAXREPEAT] == 1:  # if non-repeating
                    field_has_data = False
                    type_of_field = 0  # first subfield in composite is marked as a field (not a subfield).
                    fieldbuffer = []  # buffer for this composite.
                    for grammarsubfield in field_definition[SUBFIELDS]:  # loop subfields
                        # field exists in outgoing message and has data
                        if grammarsubfield[ID] in noderecord and noderecord[grammarsubfield[ID]]:
                            field_has_data = True
                            fieldbuffer.append({VALUE: noderecord[grammarsubfield[ID]],
                                                SFIELD: type_of_field})  # append field
                            recordbuffer += fieldbuffer
                            fieldbuffer = []
                        else:
                            fieldbuffer.append({VALUE: '', SFIELD: type_of_field})  # append new empty to buffer;
                        type_of_field = 1
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                    else:
                        #composite has no data: write empty field
                        recordbuffer.append({VALUE: '', SFIELD: 0})
                else:  # repeating composite
                    #receive list, including empty members
                    field_has_data = False
                    if field_definition[ID] in noderecord:  # field exists in outgoing message
                        type_of_field = 0  # first subfield in composite is marked as a field (not a subfield).
                        fieldbuffer = []  # buffer for this composite.
                        for comp_dict in noderecord[field_definition[ID]]:
                            composite_has_data = False  # comp_dict can be empty
                            compositebuffer = []  # buffer for this composite.
                            if comp_dict:
                                for grammarsubfield in field_definition[SUBFIELDS]:  # loop subfields
                                    # field exists in outgoing message and has data
                                    if grammarsubfield[ID] in comp_dict and comp_dict[grammarsubfield[ID]]:
                                        composite_has_data = True
                                        compositebuffer.append(
                                            {VALUE: comp_dict[grammarsubfield[ID]], SFIELD: type_of_field, FORMATFROMGRAMMAR: grammarsubfield[FORMAT]})
                                        fieldbuffer += compositebuffer
                                        compositebuffer = []
                                    else:
                                        compositebuffer.append({VALUE: '', SFIELD: type_of_field,
                                                                FORMATFROMGRAMMAR: grammarsubfield[FORMAT]})
                                    type_of_field = 1
                            if composite_has_data:
                                field_has_data = True
                                recordbuffer += fieldbuffer
                                fieldbuffer = []
                            else:
                                fieldbuffer.append({VALUE: '', SFIELD: type_of_field})
                            type_of_field = 2
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                    else:
                        #no data: write placeholder to recordbuffer;
                        recordbuffer.append({VALUE: '', SFIELD: 0})

        self.lex_records.append(lex_record)

    def _formatfield(self, value, field_definition, structure_record, node_instance):
        ''' Input: value (as a string) and field definition.
            Some parameters of self.syntax are used, eg decimaal
            Format is checked and converted (if needed).
            return the formatted value
        '''
        if field_definition[BFORMAT] == 'A':
            if isinstance(self, fixed):  # check length fields in variable records
                if field_definition[FORMAT] == 'AR':  # if field format is alfanumeric right aligned
                    value = value.rjust(field_definition[MINLENGTH])
                else:
                    # add spaces (left, because A-field is right aligned)
                    value = value.ljust(field_definition[MINLENGTH])
            if len(value) > field_definition[LENGTH]:
                self.add2errorlist(_('[F20]: Record "%(record)s" field "%(field)s" too big (max %(max)s): "%(content)s".\n') %
                                   {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value, 'max': field_definition[LENGTH]})
            if len(value) < field_definition[MINLENGTH]:
                self.add2errorlist(_('[F21]: Record "%(record)s" field "%(field)s" too small (min %(min)s): "%(content)s".\n') %
                                   {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value, 'min': field_definition[MINLENGTH]})
        elif field_definition[BFORMAT] in 'DT':
            lenght = len(value)
            if field_definition[BFORMAT] == 'D':
                try:
                    if lenght == 6:
                        time.strptime(value, '%y%m%d')
                    elif lenght == 8:
                        time.strptime(value, '%Y%m%d')
                    else:
                        raise ValueError('To be catched')
                except ValueError:
                    self.add2errorlist(_('[F22]: Record "%(record)s" date field "%(field)s" not a valid date: "%(content)s".\n') %
                                       {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value})
                if lenght > field_definition[LENGTH]:
                    self.add2errorlist(_('[F31]: Record "%(record)s" date field "%(field)s" too big (max %(max)s): "%(content)s".\n') %
                                       {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value, 'max': field_definition[LENGTH]})
                if lenght < field_definition[MINLENGTH]:
                    self.add2errorlist(_('[F32]: Record "%(record)s" date field "%(field)s" too small (min %(min)s): "%(content)s".\n') %
                                       {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value, 'min': field_definition[MINLENGTH]})
            else:  # if field_definition[BFORMAT] == 'T':
                try:
                    if lenght == 4:
                        time.strptime(value, '%H%M')
                    elif lenght == 6:
                        time.strptime(value, '%H%M%S')
                    else:
                        raise ValueError('To be catched')
                except ValueError:
                    self.add2errorlist(_('[F23]: Record "%(record)s" time field "%(field)s" not a valid time: "%(content)s".\n') %
                                       {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value})
                if lenght > field_definition[LENGTH]:
                    self.add2errorlist(_('[F33]: Record "%(record)s" time field "%(field)s" too big (max %(max)s): "%(content)s".\n') %
                                       {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value, 'max': field_definition[LENGTH]})
                if lenght < field_definition[MINLENGTH]:
                    self.add2errorlist(_('[F34]: Record "%(record)s" time field "%(field)s" too small (min %(min)s): "%(content)s".\n') %
                                       {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value, 'min': field_definition[MINLENGTH]})
        elif field_definition[BFORMAT] == 'ENUM':
            if(value not in field_definition[FORMAT]['ENUM']):
                self.add2errorlist(_('[F35]%(linpos)s: Record "%(record)s" enum field "%(field)s" not a valid enum: "%(content)s".\n') %
                                       {'linpos': node_instance.linpos(), 'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value})
        else:  # numerics
            #~ if value[0] == '-':
                #~ minussign = '-'
                #~ absvalue = value[1:]
            #~ else:
                #~ minussign = ''
                #~ absvalue = value
            #~ digits,decimalsign,decimals = absvalue.partition('.')
            #~ if not digits:
                #~ digits = '0'
                #~ if not decimals:# and decimalsign:
                    #~ self.add2errorlist(_('[F24]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n')%
                                        #~ {'field':field_definition[ID],'content':value,'record':self.mpathformat(structure_record[MPATH])})

            # for some formats (if self.ta_info['lengthnumericbare']=True; eg edifact)
            # length is calculated without decimal sing and/or minus sign.
            lengthcorrection = 0
            if field_definition[BFORMAT] == 'R':  # floating point: use all decimals received
                if self.ta_info['lengthnumericbare']:
                    if value[0] == '-':
                        lengthcorrection += 1
                    if '.' in value:
                        lengthcorrection += 1
                try:
                    value = unicode(decimal.Decimal(value))
                except:
                    self.add2errorlist(_('[F25]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n') %
                                       {'field': field_definition[ID], 'content': value, 'record': self.mpathformat(structure_record[MPATH])})
                if field_definition[FORMAT] == 'RL':  # if field format is numeric left aligned
                    value = value.ljust(field_definition[MINLENGTH] + lengthcorrection)
                elif field_definition[FORMAT] == 'RR':  # if field format is numeric right aligned
                    value = value.rjust(field_definition[MINLENGTH] + lengthcorrection)
                else:
                    value = value.zfill(field_definition[MINLENGTH] + lengthcorrection)
                value = value.replace('.', self.ta_info['decimaal'], 1)  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == 'N':  # fixed decimals; round
                if self.ta_info['lengthnumericbare']:
                    if value[0] == '-':
                        lengthcorrection += 1
                    if field_definition[DECIMALS]:
                        lengthcorrection += 1
                try:
                    dec_value = decimal.Decimal(value)
                    value = unicode(dec_value.quantize(decimal.Decimal('10e-%d' % field_definition[DECIMALS])))
                except:
                    self.add2errorlist(_('[F26]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n') %
                                       {'field': field_definition[ID], 'content': value, 'record': self.mpathformat(structure_record[MPATH])})
                if field_definition[FORMAT] == 'NL':  # if field format is numeric left aligned
                    value = value.ljust(field_definition[MINLENGTH] + lengthcorrection)
                elif field_definition[FORMAT] == 'NR':  # if field format is numeric right aligned
                    value = value.rjust(field_definition[MINLENGTH] + lengthcorrection)
                else:
                    value = value.zfill(field_definition[MINLENGTH] + lengthcorrection)
                value = value.replace('.', self.ta_info['decimaal'], 1)  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == 'I':  # implicit decimals
                if self.ta_info['lengthnumericbare']:
                    if value[0] == '-':
                        lengthcorrection += 1
                try:
                    dec_value = decimal.Decimal(value).shift(field_definition[DECIMALS])
                    value = unicode(dec_value.quantize(NODECIMAL))
                except:
                    self.add2errorlist(_('[F27]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n') %
                                       {'field': field_definition[ID], 'content': value, 'record': self.mpathformat(structure_record[MPATH])})
                value = value.zfill(field_definition[MINLENGTH] + lengthcorrection)

            if len(value) - lengthcorrection > field_definition[LENGTH]:
                self.add2errorlist(_('[F28]: Record "%(record)s" field "%(field)s" too big: "%(content)s".\n') %
                                   {'record': self.mpathformat(structure_record[MPATH]), 'field': field_definition[ID], 'content': value})
        return value

    def _initfield(self, field_definition):
        ''' for some editypes like fixed fields without date have specific initalisation.
            this is controlled by the 'stripfield_sep' parameter in grammar.
        '''
        if field_definition[BFORMAT] in 'ADT':
            value = ''
        else:  # numerics
            value = '0'
            if field_definition[BFORMAT] == 'R':  # floating point: use all decimals received
                value = value.zfill(field_definition[MINLENGTH])
            elif field_definition[BFORMAT] == 'N':  # fixed decimals; round
                value = unicode(decimal.Decimal(value).quantize(decimal.Decimal('10e-%d' % field_definition[DECIMALS])))
                value = value.zfill(field_definition[MINLENGTH])
                value = value.replace('.', self.ta_info['decimaal'], 1)  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == 'I':  # implicit decimals
                value = value.zfill(field_definition[MINLENGTH])
        return value

    def record2string(self, lex_records):
        ''' write lex_records to a file.
            using the right editype (edifact, x12, etc) and charset.
            write (all fields of) each record using the right separators, escape etc
        '''
        sfield_sep = self.ta_info['sfield_sep']
        if self.ta_info['record_tag_sep']:
            record_tag_sep = self.ta_info['record_tag_sep']
        else:
            record_tag_sep = self.ta_info['field_sep']
        field_sep = self.ta_info['field_sep']
        quote_char = self.ta_info['quote_char']
        escape = self.ta_info['escape']
        record_sep = self.ta_info['record_sep'] + self.ta_info['add_crlfafterrecord_sep']
        forcequote = self.ta_info['forcequote']
        escapechars = self._getescapechars()
        noBOTSID = self.ta_info.get('noBOTSID', False)
        rep_sep = self.ta_info['reserve']

        lijst = []
        for lex_record in lex_records:
            if noBOTSID:  # for csv/fixed: do not write BOTSID so remove it
                del lex_record[0]
            fieldcount = 0
            mode_quote = False
            value = ''  # to collect the formatted record-string.
            for field in lex_record:  # loop all fields in lex_record
                if not field[SFIELD]:  # is a field:
                    if fieldcount == 0:  # do nothing because first field in lex_record is not preceded by a separator
                        fieldcount = 1
                    elif fieldcount == 1:
                        value += record_tag_sep
                        fieldcount = 2
                    else:
                        value += field_sep
                elif field[SFIELD] == 1:  # is a subfield:
                    value += sfield_sep
                else:  # repeat
                    value += rep_sep
                if quote_char:  # quote char only used for csv
                    start_to__quote = False
                    if forcequote == 2:
                        if field[FORMATFROMGRAMMAR] in ['AN', 'A', 'AR']:
                            start_to__quote = True
                    elif forcequote:  # always quote; this catches values 1, '1', '0'
                        start_to__quote = True
                    else:
                        if field_sep in field[VALUE] or quote_char in field[VALUE] or record_sep in field[VALUE]:
                            start_to__quote = True
                    if start_to__quote:
                        value += quote_char
                        mode_quote = True
                # use escape (edifact, tradacom). For x12 is warned if content contains separator
                for char in field[VALUE]:
                    if char in escapechars:
                        if isinstance(self, x12):
                            if self.ta_info['replacechar']:
                                char = self.ta_info['replacechar']
                            else:
                                raise botslib.OutMessageError(_('[F51]: Character "%(char)s" is used as separator in this x12 file, so it can not be used in content. Field: "%(content)s".'),
                                                              {'char': char, 'content': field[VALUE]})
                        else:
                            value += escape
                    elif mode_quote and char == quote_char:
                        value += quote_char
                    value += char
                if mode_quote:
                    value += quote_char
                    mode_quote = False
            value += record_sep
            lijst.append(value)
        return ''.join(lijst)

    def _getescapechars(self):
        return ''


class fixed(Outmessage):

    def _initfield(self, field_definition):
        if field_definition[BFORMAT] == 'A':
            if field_definition[FORMAT] == 'AR':  # if field format is alfanumeric right aligned
                value = ''.rjust(field_definition[MINLENGTH])
            else:
                value = ''.ljust(field_definition[MINLENGTH])  # add spaces (left, because A-field is right aligned)
        elif field_definition[BFORMAT] == 'D':
            value = ''.ljust(field_definition[MINLENGTH])  # add spaces
        elif field_definition[BFORMAT] == 'T':
            value = ''.ljust(field_definition[MINLENGTH])  # add spaces
        else:  # numerics
            if field_definition[BFORMAT] == 'R':  # floating point: use all decimals received
                if field_definition[FORMAT] == 'RL':  # if field format is numeric right aligned
                    value = '0'.ljust(field_definition[MINLENGTH])
                elif field_definition[FORMAT] == 'RR':  # if field format is numeric right aligned
                    value = '0'.rjust(field_definition[MINLENGTH])
                else:
                    value = '0'.zfill(field_definition[MINLENGTH])
            elif field_definition[BFORMAT] == 'N':  # fixed decimals; round
                value = unicode(decimal.Decimal('0').quantize(decimal.Decimal(10) ** -field_definition[DECIMALS]))
                if field_definition[FORMAT] == 'NL':  # if field format is numeric right aligned
                    value = value.ljust(field_definition[MINLENGTH])
                elif field_definition[FORMAT] == 'NR':  # if field format is numeric right aligned
                    value = value.rjust(field_definition[MINLENGTH])
                else:
                    value = value.zfill(field_definition[MINLENGTH])
                value = value.replace('.', self.ta_info['decimaal'], 1)  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == 'I':  # implicit decimals
                dec_value = decimal.Decimal('0') * 10**field_definition[DECIMALS]
                value = unicode(dec_value.quantize(NODECIMAL))
                value = value.zfill(field_definition[MINLENGTH])
        return value


class idoc(fixed):

    def __init__(self, ta_info):
        super(idoc, self).__init__(ta_info)
        self.recordnumber = 0  # segment counter. For sequential recordnumbering in records.

    def _canonicaltree(self, node_instance, structure):
        self.headerrecordnumber = self.recordnumber
        super(idoc, self)._canonicaltree(node_instance, structure)

    def _canonicalfields(self, node_instance, record_definition):
        if self.ta_info['automaticcount']:
            node_instance.record.update({'MANDT': self.ta_info['MANDT'], 'DOCNUM': self.ta_info['DOCNUM'], 'SEGNUM': unicode(
                self.recordnumber), 'PSGNUM': unicode(self.headerrecordnumber), 'HLEVEL': unicode(len(record_definition[MPATH]))})
        else:
            node_instance.record.update({'MANDT': self.ta_info['MANDT'], 'DOCNUM': self.ta_info['DOCNUM']})
        super(idoc, self)._canonicalfields(node_instance, record_definition)
        self.recordnumber += 1  # tricky. EDI_DC is not counted, so I count after writing.


class var(Outmessage):
    pass


class csv(var):

    def _getescapechars(self):
        return self.ta_info['escape']


class edifact(var):

    def _getescapechars(self):
        terug = self.ta_info['record_sep'] + self.ta_info['field_sep'] + \
            self.ta_info['sfield_sep'] + self.ta_info['escape']
        if self.ta_info['version'] >= '4':
            terug += self.ta_info['reserve']
        return terug


class tradacoms(var):

    def _getescapechars(self):
        terug = self.ta_info['record_sep'] + self.ta_info['field_sep'] + \
            self.ta_info['sfield_sep'] + self.ta_info['escape'] + self.ta_info['record_tag_sep']
        return terug

    def writeall(self):
        ''' writeall is called for writing all 'real' outmessage objects; but not for enveloping.
            writeall is call from transform.translate()
        '''
        self.nrmessagewritten = 0
        if not self.root.children:
            raise botslib.OutMessageError(_('No outgoing message'))  # then there is nothing to write...
        messagetype = self.ta_info['messagetype']
        for tradacomsmessage in self.root.getloop({'BOTSID': 'STX'}, {'BOTSID': 'MHD'}):
            self.ta_info['messagetype'] = tradacomsmessage.get(
                {'BOTSID': 'MHD', 'TYPE.01': None}) + tradacomsmessage.get({'BOTSID': 'MHD', 'TYPE.02': None})
            self.messagegrammarread(typeofgrammarfile='grammars')
            if not self.nrmessagewritten:
                self._initwrite()
            self.checkmessage(tradacomsmessage, self.defmessage)
            self.checkforerrorlist()
            self._write(tradacomsmessage)
            self.nrmessagewritten += 1
        self.ta_info['messagetype'] = messagetype
        self._closewrite()
        self.ta_info['nrmessages'] = self.nrmessagewritten


class x12(var):

    def _getescapechars(self):
        terug = self.ta_info['record_sep'] + self.ta_info['field_sep'] + self.ta_info['sfield_sep']
        if self.ta_info['version'] >= '00403':
            terug += self.ta_info['reserve']
        return terug


class xml(Outmessage):
    ''' Some problems with right xml prolog, standalone, DOCTYPE, processing instructons: Different ET versions give different results.
        Things work OK for python 2.7
        celementtree in 2.7 is version 1.0.6, but different implementation in 2.6??
        For python <2.7: do not generate standalone, DOCTYPE, processing instructions for encoding !=utf-8,ascii OR if elementtree package is installed (version 1.3.0 or bigger)
    '''

    def _write(self, node_instance):
        ''' write normal XML messages (no envelope)'''
        xmltree = ET.ElementTree(self._node2xml(node_instance))
        root = xmltree.getroot()
        self._xmlcorewrite(xmltree, root)

    def envelopewrite(self, node_instance):
        ''' write envelope for XML messages'''
        self._initwrite()
        self.checkmessage(node_instance, self.defmessage)
        self.checkforerrorlist()
        xmltree = ET.ElementTree(self._node2xml(node_instance))
        root = xmltree.getroot()
        ETI.include(root)
        self._xmlcorewrite(xmltree, root)
        self._closewrite()

    def _xmlcorewrite(self, xmltree, root):
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            python26 = True
        else:
            python26 = False
        if not python26 and self.ta_info['namespace_prefixes']:   # Register any namespace prefixes specified in syntax
            for eachns in self.ta_info['namespace_prefixes']:
                ET.register_namespace(eachns[0], eachns[1])
        #xml prolog: always use.*********************************
        #standalone, DOCTYPE, processing instructions: only possible in python >= 2.7 or if encoding is utf-8/ascii
        if not python26 or self.ta_info['charset'] in ['us-ascii', 'utf-8'] or ET.VERSION >= '1.3.0':
            if self.ta_info['indented']:
                indentstring = b'\n'
            else:
                indentstring = b''
            if self.ta_info['standalone']:
                standalonestring = 'standalone="%s" ' % (self.ta_info['standalone'])
            else:
                standalonestring = ''
            processing_instruction = ET.ProcessingInstruction('xml', 'version="%s" encoding="%s" %s' % (
                self.ta_info['version'], self.ta_info['charset'], standalonestring))
            # do not use encoding here. gives double xml prolog; possibly because
            # ET.ElementTree.write i used again by write()
            self._outstream.write(ET.tostring(processing_instruction) + indentstring)
            #doctype /DTD **************************************
            if self.ta_info['DOCTYPE']:
                #~ self._outstream.write(b'<!DOCTYPE %s>'%(self.ta_info['DOCTYPE']) + indentstring)
                self._outstream.write(b'<!DOCTYPE ' + self.ta_info['DOCTYPE'].encode('ascii') + b'>' + indentstring)
            #processing instructions (other than prolog) ************
            if self.ta_info['processing_instructions']:
                for eachpi in self.ta_info['processing_instructions']:
                    processing_instruction = ET.ProcessingInstruction(eachpi[0], eachpi[1])
                    # do not use encoding here. gives double xml prolog; possibly because
                    # ET.ElementTree.write i used again by write()
                    self._outstream.write(ET.tostring(processing_instruction) + indentstring)
        #indent the xml elements
        if self.ta_info['indented']:
            botslib.indent_xml(root)
        #write tree to file; this is different for different python/elementtree versions
        if python26 and ET.VERSION < '1.3.0':
            xmltree.write(self._outstream, encoding=self.ta_info['charset'])
        else:
            xmltree.write(self._outstream, encoding=self.ta_info['charset'], xml_declaration=False)

    def _node2xml(self, node_instance):
        ''' recursive method.
        '''
        newnode = self._node2xmlfields(node_instance.record)
        for childnode in node_instance.children:
            newnode.append(self._node2xml(childnode))
        return newnode

    def _node2xmlfields(self, noderecord):
        ''' write record as xml-record-entity plus xml-field-entities within the xml-record-entity.
            output is sorted according to grammar, attributes alfabetically.
        '''
        recordtag = noderecord.pop('BOTSID')
        del noderecord['BOTSIDnr']
        BOTSCONTENT = noderecord.pop('BOTSCONTENT', None)
        #collect all values used as attributes from noderecord***************************
        attributemarker = self.ta_info['attributemarker']
        attributedict = {}  # is a dict of dicts
        for key, value in noderecord.items():
            if attributemarker in key:
                field, attribute = key.split(attributemarker, 1)
                if not field in attributedict:
                    attributedict[field] = {}
                attributedict[field][attribute] = value
                #~ del noderecord[key]
        #generate xml-record-entity***************************
        xmlrecord = ET.Element(recordtag, attributedict.get(recordtag, {}))
        #***add BOTSCONTENT as the content of the xml-record-entity
        xmlrecord.text = BOTSCONTENT
        #generate the xml-field-entities within the xml-record-entity***************************
        # loop over remaining fields in 'record': write these as subelements
        for field_def in self.defmessage.recorddefs[recordtag]:
            if attributemarker in field_def[ID]:  # skip fields that are marked as xml attributes
                continue
            content = noderecord.get(field_def[ID], None)
            attributes = attributedict.get(field_def[ID], {})
            if content is not None or attributes:
                ET.SubElement(xmlrecord, field_def[ID], attributes).text = content  # add xml element to xml record
        return xmlrecord

    def _initwrite(self):
        botsglobal.logger.debug('Start writing to file "%(filename)s".', self.ta_info)
        self._outstream = botslib.opendata_bin(self.ta_info['filename'], 'wb')


class xmlnocheck(xml):

    def _node2xmlfields(self, noderecord):
        ''' write record as xml-record-entity plus xml-field-entities within the xml-record-entity.
            output is sorted alfabetically, attributes alfabetically.
        '''
        recordtag = noderecord.pop('BOTSID')
        del noderecord['BOTSIDnr']
        BOTSCONTENT = noderecord.pop('BOTSCONTENT', None)
        #***collect from noderecord all entities and attributes***************************
        attributemarker = self.ta_info['attributemarker']
        attributedict = {}  # is a dict of dicts
        for key, value in noderecord.items():
            if attributemarker in key:
                field, attribute = key.split(attributemarker, 1)
                if not field in attributedict:
                    attributedict[field] = {}
                attributedict[field][attribute] = value
            else:
                if not key in attributedict:
                    attributedict[key] = {}
        #***generate the xml-record-entity***************************
        xmlrecord = ET.Element(recordtag, attributedict.pop(recordtag, {}))  # pop from attributedict->do not use later
        #***add BOTSCONTENT as the content of the xml-record-entity
        xmlrecord.text = BOTSCONTENT
        #***generate the xml-field-entities within the xml-record-entity***************************
        for key in sorted(attributedict.keys()):  # sorted: predictable output
            ET.SubElement(xmlrecord, key, attributedict[key]).text = noderecord.get(key)
        return xmlrecord


class json(Outmessage):

    def _initwrite(self):
        super(json, self)._initwrite()
        if self.multiplewrite:
            self._outstream.write('[')

    def _write(self, node_instance):
        ''' convert node tree to appropriate python object.
            python objects are written to json by simplejson.
        '''
        if self.nrmessagewritten:
            self._outstream.write(',')
        jsonobject = {node_instance.record['BOTSID']: self._node2json(node_instance)}
        if self.ta_info['indented']:
            indent = 2
        else:
            indent = None
        simplejson.dump(jsonobject, self._outstream, skipkeys=False,
                        ensure_ascii=False, check_circular=False, indent=indent)

    def _closewrite(self):
        if self.multiplewrite:
            self._outstream.write(']')
        super(json, self)._closewrite()

    def _node2json(self, node_instance):
        ''' recursive method.
        '''
        #newjsonobject is the json object assembled in the function.
        newjsonobject = node_instance.record.copy()  # init newjsonobject with record fields from node
        for childnode in node_instance.children:  # fill newjsonobject with the lex_records from childnodes.
            key = childnode.record['BOTSID']
            if key in newjsonobject:
                newjsonobject[key].append(self._node2json(childnode))
            else:
                newjsonobject[key] = [self._node2json(childnode)]
        del newjsonobject['BOTSID']
        try:
            del newjsonobject['BOTSIDnr']
        except:
            pass
        return newjsonobject

    def _node2jsonold(self, node_instance):
        ''' recursive method.
        '''
        newdict = node_instance.record.copy()
        if node_instance.children:  # if this node has records in it.
            sortedchildren = {}  # empty dict
            for childnode in node_instance.children:
                botsid = childnode.record['BOTSID']
                if botsid in sortedchildren:
                    sortedchildren[botsid].append(self._node2json(childnode))
                else:
                    sortedchildren[botsid] = [self._node2json(childnode)]
            for key, value in sortedchildren.items():
                if len(value) == 1:
                    newdict[key] = value[0]
                else:
                    newdict[key] = value
        del newdict['BOTSID']
        return newdict

    def _canonicalfields(self, node_instance, record_definition):
        ''' subclassed method; sorts using OrderedDict
            For all fields: check M/C, format.
            Fields are sorted according to grammar.
            Fields are never added.
        '''
        noderecord = node_instance.record
        new_noderecord = OrderedDict()
        for field_definition in record_definition[FIELDS]:  # loop over fields in grammar
            value = noderecord.get(field_definition[ID])
            if not value:
                if field_definition[MANDATORY]:
                    self.add2errorlist(_(u'[F02]%(linpos)s: Record "%(mpath)s" field "%(field)s" is mandatory.\n') %
                                       {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID]})
                if value is None:  # None-values are not used
                    continue
            new_noderecord[field_definition[ID]] = self._formatfield(
                value, field_definition, record_definition, node_instance)
        node_instance.record = new_noderecord


class jsonnocheck(json):

    def _node2json(self, node_instance):
        ''' recursive method.
        '''
        #newjsonobject is the json object assembled in the function.
        # init newjsonobject with record fields from node; sorted
        newjsonobject = OrderedDict(sorted(node_instance.record.items()))
        for childnode in node_instance.children:  # fill newjsonobject with the lex_records from childnodes.
            key = childnode.record['BOTSID']
            if key in newjsonobject:
                newjsonobject[key].append(self._node2json(childnode))
            else:
                newjsonobject[key] = [self._node2json(childnode)]
        del newjsonobject['BOTSID']
        del newjsonobject['BOTSIDnr']
        return newjsonobject

class avro(json):

    def _write(self, node_instance):
        ''' convert node tree to appropriate python object.
            python objects are written to avro by fastavro.
        '''
        avroobject = {node_instance.record['BOTSID']: self._node2avro(node_instance)}
        if (self.ta_info['noHeader']):
            avroobject = avroobject[node_instance.record['BOTSID']]
        _, schemapath = botslib.botsimport('grammars', self.ta_info['editype'], self.ta_info['messagetype'])
        schema = load_schema(schemapath + '.avsc')
        avrowriter(self._outstream, schema, [avroobject])
        

    def _node2avro(self, node_instance):
        ''' recursive method.
        '''
        #newavroobject is the avro object assembled in the function.
        newavroobject = dict(node_instance.record.copy())  # init newavroobject with record fields from node
        recordtag = newavroobject['BOTSID']
        for field_definition in self.defmessage.recorddefs[recordtag]:  # loop over fields in grammar
            value = newavroobject.get(field_definition[ID])
            if value is None:  # None-values are not used
                continue
            else: 
                newavroobject[field_definition[ID]] = self._convertField(value, field_definition)
        for childnode in node_instance.children:  # fill newjsonobject with the lex_records from childnodes.
            key = childnode.record['BOTSID']
            union_record_name = childnode.record.get('AVRO_RECORD_NAME')
            avro_array = childnode.record.get('AVRO_ARRAY')
            avro_map = childnode.record.get('AVRO_MAP')
            if key in newavroobject and avro_array:
                newavroobject[key].append(childnode.record.get('input'))
            elif key in newavroobject and avro_map:
                newavroobject[key][childnode.record.get('key')] = childnode.record.get('value')
            elif key in newavroobject:
                newavroobject[key].append(self._node2avro(childnode))
            elif union_record_name:
                newavroobject[key] = (union_record_name, self._node2avro(childnode.children[0]))
            elif avro_array:
                newavroobject[key] = [childnode.record.get('input')]
            elif avro_map:
                newavroobject[key] = {childnode.record.get('key'): childnode.record.get('value')} 
            else:
                # Heuristic to determine whether to put a childnode in an array or not
                if (childnode.structure[MIN] == 1 and childnode.structure[MAX] == 1):
                    newavroobject[key] = self._node2avro(childnode)
                else:
                    newavroobject[key] = [self._node2avro(childnode)]
        newavroobject.pop('BOTSID', None)
        newavroobject.pop('BOTSIDnr', None)
        newavroobject.pop('AVRO_RECORD_NAME', None)
        newavroobject.pop('AVRO_ARRAY', None)
        return newavroobject
    
    def _convertField(self, value, field_definition):
        if field_definition[BFORMAT] == 'N' and field_definition[DECIMALS] == 0:
            return int(value) 
        if field_definition[BFORMAT] == 'R':
            return float(value)
        if field_definition[BFORMAT] == 'UUID':
            return UUID(value)
        if field_definition[FORMAT] == 'B':
            return value == 'True'
        else: return value


class templatehtml(Outmessage):
    ''' uses Genshi library for templating. Genshi is very similar to Kid, and is the fork/follow-up of Kid.
        Kid is not being developed further; in time Kid will not be in repositories etc.
        Templates for Genshi are like Kid templates. Changes:
        - other namespace: xmlns:py="http://genshi.edgewall.org/" instead of xmlns:py="http://purl.org/kid/ns#"
        - enveloping is different: <xi:include href="${message}" /> instead of <div py:replace="document(message)"/>
        2 modes:
        1. use self.data, a class that can contain any python object (older way of working)
        2. use structure, recordedefs, write node tree. This is more like normal way of working; output is checked etc.
            the procided template can handle msot things, change only css of envelope.
    '''
    class TemplateData(object):
        pass

    def __init__(self, ta_info):
        try:
            self.template = botslib.botsbaseimport('genshi.template')
        except ImportError:
            raise ImportError(_('Dependency failure: editype "templatehtml" requires python library "genshi".'))
        super(templatehtml, self).__init__(ta_info)
        self.data = templatehtml.TemplateData()  # self.data can be used by mappingscript as container for content

    def _write(self, node_instance):
        templatefile = botslib.abspath(self.__class__.__name__, self.ta_info['template'])
        try:
            botsglobal.logger.debug('Start writing to file "%(filename)s".', self.ta_info)
            loader = self.template.TemplateLoader(auto_reload=False)
            tmpl = loader.load(templatefile)
        except:
            txt = botslib.txtexc()
            raise botslib.OutMessageError(_('While templating "%(editype)s.%(messagetype)s", error:\n%(txt)s'),
                                          {'editype': self.ta_info['editype'], 'messagetype': self.ta_info['messagetype'], 'txt': txt})
        try:
            filehandler = botslib.opendata_bin(self.ta_info['filename'], 'wb')
            if self.ta_info['has_structure']:  # new way of working
                if self.ta_info['print_as_row']:
                    node_instance.collectlines(self.ta_info['print_as_row'])
                stream = tmpl.generate(node=node_instance)
            else:
                stream = tmpl.generate(data=self.data)
            stream.render(method='xhtml', encoding=self.ta_info['charset'], out=filehandler)
        except:
            txt = botslib.txtexc()
            raise botslib.OutMessageError(_('While templating "%(editype)s.%(messagetype)s", error:\n%(txt)s'),
                                          {'editype': self.ta_info['editype'], 'messagetype': self.ta_info['messagetype'], 'txt': txt})
        finally:
            filehandler.close()
            botsglobal.logger.debug(_('End writing to file "%(filename)s".'), self.ta_info)

    def writeall(self):
        if not self.root.record:
            self.root.record = {'BOTSID': 'dummy'}  # dummy, is not used but needed for writeall of base class
        super(templatehtml, self).writeall()


class db(Outmessage):
    ''' For database connector: writing to database.
        Mapping script delevers an object (class, dict) in out.root.
        Object is pickled and saved.
        Communication script picks up the pickle,
    '''

    def __init__(self, ta_info):
        super(db, self).__init__(ta_info)
        self.root = None  # make root None; root is not a Node-object anyway; None can easy be tested when writing.

    def writeall(self):
        if self.root is None:
            raise botslib.OutMessageError(_('No outgoing message'))  # then there is nothing to write...
        botsglobal.logger.debug('Start writing to file "%(filename)s".', self.ta_info)
        botslib.writedata_pickled(self.ta_info['filename'], self.root)
        botsglobal.logger.debug('End writing to file "%(filename)s".', self.ta_info)
        self.ta_info['envelope'] = 'db'
        self.ta_info['merge'] = False


class raw(Outmessage):
    ''' Mapping script delivers a raw bytestream in out.root.
        Bytestream is saved.
    '''

    def __init__(self, ta_info):
        super(raw, self).__init__(ta_info)
        self.root = None  # make root None; root is not a Node-object anyway; None can easy be tested when writing.

    def writeall(self):
        if self.root is None:
            raise botslib.OutMessageError(_('No outgoing message'))  # then there is nothing to write...
        botsglobal.logger.debug('Start writing to file "%(filename)s".', self.ta_info)
        self._outstream = botslib.opendata_bin(self.ta_info['filename'], 'wb')
        self._outstream.write(self.root)
        self._outstream.close()
        botsglobal.logger.debug('End writing to file "%(filename)s".', self.ta_info)
        self.ta_info['envelope'] = 'raw'
        self.ta_info['merge'] = False
