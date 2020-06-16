# -*- coding: utf-8 -*-



import sys
if sys.version_info[0] > 2:
    str = str = str
from django.utils.translation import ugettext as _
#bots-modules
from . import botslib
from . import node
from . import botsglobal
from . import grammar
from .botsconfig import *


class Message(object):
    ''' abstract class; represents a edi message.
        is subclassed as outmessage or inmessage object.
    '''

    def __init__(self, ta_info):
        self.ta_info = ta_info  # here ta_info is only filled with parameters from db-ta
        self.errorlist = []  # collect non-fatal errors in the edi file; used in reporting errors.
        self.errorfatal = True  # store fatal errors: errors that stop the processing of the file
        self.messagetypetxt = ''  # used in reporting errors.
        self.messagecount = 0  # count messages in edi file; used in reporting errors.

    def add2errorlist(self, errortxt):
        ''' Handle non-fatal parse errors.
        '''
        #~ raise botslib.MessageError('For unit format test')     #UNITTEST_CORRECTION
        if len(self.errorlist) < botsglobal.ini.getint('settings', 'max_number_errors', 10):
            self.errorlist.append(self.messagetypetxt + errortxt)
        elif len(self.errorlist) == botsglobal.ini.getint('settings', 'max_number_errors', 10):
            self.errorlist.append((_('Found at least %(max_number_errors)s errors.') %
                                   {'max_number_errors': len(self.errorlist)}))
        else:
            #more than max_number_errors: stop adding new errors to list.
            pass

    def checkforerrorlist(self):
        ''' examine the message-object for errors;
        '''
        if self.errorfatal:  # for fatal errors: (try to) get information like partners for edi file
            self.try_to_retrieve_info()
        if self.errorlist:
            raise botslib.MessageError(''.join(self.errorlist))

    def try_to_retrieve_info(self):
        ''' when edi-file is not correct, (try to) get info about eg partnerID's in message
            method is specified in subclasses.
        '''
        pass

    def messagegrammarread(self, typeofgrammarfile):
        ''' read grammar for a message/envelope.
        '''
        #read grammar for message.
        self.defmessage = grammar.grammarread(self.ta_info['editype'], self.ta_info['messagetype'], typeofgrammarfile)
        #write values from grammar syntax to self.ta_info - unless these values are already set (eg by mappingscript)
        botslib.updateunlessset(self.ta_info, self.defmessage.syntax)

    @staticmethod
    def display(lex_records):
        ''' for debugging: display lexed records.'''
        for lex_record in lex_records:
            counter = 0
            for veld in lex_record:
                if counter == 0:
                    print('%s    (Record-id)' % (veld[VALUE]))
                else:
                    if veld[SFIELD] == 0:
                        print('    %s    (field)' % (veld[VALUE]))
                    elif veld[SFIELD] == 1:
                        print('        %s    (sub)' % (veld[VALUE]))
                    elif veld[SFIELD] == 2:
                        print('        %s    (rep)' % (veld[VALUE]))
                    else:
                        print('    %s    (???)' % (veld[VALUE]))
                counter += 1

    @staticmethod
    def mpathformat(mpath):
        ''' mpath is eg: ['UNH', 'NAD'], formatted is: 'UNH-NAD'.
        '''
        return '-'.join(mpath)

    def checkmessage(self, node_instance, defmessage, subtranslation=False):
        ''' The node tree is check, sorted, fields are formatted etc against grammar. (so far only minimal tests have been done during processing)
            For checking translation & subtranslation
            parameter 'subtranslation' only used for reporting
            some different cases:
            - empy root.record, root.children filled:
            - edifact, x12, tradacoms: each child is an envelope. Check each envelope. (use mailbag to have one UNB per node-tree here)
            - csv nobotsid: each child is a record. Check all records in one check
            - xml, json:
            root.record filled, root.children filled: outgoing messages.
        '''
        if not self.ta_info['has_structure']:
            return
        if node_instance.record:  # root record contains information; so one message
            self._checkonemessage(node_instance, defmessage, subtranslation)
        else:
            for childnode in node_instance.children:
                self._checkonemessage(childnode, defmessage, subtranslation)

    def _checkonemessage(self, node_instance, defmessage, subtranslation):
        structure = defmessage.structure
        if node_instance.record['BOTSID'] != structure[0][ID]:
            raise botslib.MessageRootError(_('[G50]: Grammar "%(grammar)s" starts with record "%(grammarroot)s"; but in edi-file found start-record "%(root)s".'),
                                           {'root': node_instance.record['BOTSID'], 'grammarroot': structure[0][ID], 'grammar': defmessage.grammarname})
        self._checkifrecordsingrammar(node_instance, structure[0], defmessage.grammarname)
        self._canonicaltree(node_instance, structure[0])
        # should the content of the message (the records read) be logged.
        if not subtranslation and botsglobal.ini.getboolean('settings', 'readrecorddebug', False):
            self._logmessagecontent(node_instance)

    def _checkifrecordsingrammar(self, node_instance, structure, grammarname):
        ''' check for every node if in grammar
            recursive
        '''
        deletelist = []  # list of records not in the grammar; these records are deleted at end of function
        self._checkiffieldsingrammar(node_instance, structure)  # check if fields are known in grammar
        # determine if SUBTRANSLATION starts; do not check (is already checked)
        if 'messagetype' in node_instance.queries:
            return
        if node_instance.children and LEVEL not in structure:  # if record has children, but these are not in the grammar
            if self.ta_info['checkunknownentities']:
                self.add2errorlist(_('[S01]%(linpos)s: Record "%(record)s" in message has children, but these are not in grammar "%(grammar)s". Found record "%(xx)s".\n') %
                                   {'linpos': node_instance.linpos(), 'record': node_instance.record['BOTSID'], 'grammar': grammarname, 'xx': node_instance.children[0].record['BOTSID']})
            node_instance.children = []
            return
        for childnode in node_instance.children:  # for every record/childnode:
            for record_definition in structure[LEVEL]:  # search in grammar-records
                if childnode.record['BOTSID'] == record_definition[ID]:
                    #found record in grammar
                    #check recursive:
                    self._checkifrecordsingrammar(childnode, record_definition, grammarname)
                    break  # record/childnode is in gramar; go to check next record/childnode
            else:  # record/childnode in not in grammar
                if self.ta_info['checkunknownentities']:
                    self.add2errorlist(_('[S02]%(linpos)s: Unknown record "%(record)s" in message.\n') %
                                       {'linpos': node_instance.linpos(), 'record': childnode.record['BOTSID']})
                deletelist.append(childnode)
        for child in deletelist:
            node_instance.children.remove(child)

    def _checkiffieldsingrammar(self, node_instance, record_definition):
        ''' checks for every field in record if field exists in record_definition (from grammar).
            for inmessage of type (var,fixed,??) this is not needed
        '''
        for field in list(node_instance.record.keys()):  # check every field in the record
            if field == 'BOTSIDnr':  # BOTSIDnr is not in grammar, so skip check
                continue
            for field_definition in record_definition[FIELDS]:
                if field_definition[ISFIELD]:  # if field (no composite)
                    if field == field_definition[ID]:
                        break  # OK!
                else:  # if composite
                    if field_definition[MAXREPEAT] == 1:  # non-repeating composite
                        for grammarsubfield in field_definition[SUBFIELDS]:  # loop subfields
                            if field == grammarsubfield[ID]:
                                break  # break out of grammarsubfield-for-loop ->goto break out of field_definition-for-loop
                        else:
                            continue  # nothing found; continue with next gammarfield
                        break  # break out of field_definition-for-loop
                    else:  # repeating composite
                        if field == field_definition[ID]:
                            #OK. Contents is a list of dicts;
                            #TODO: check for each dict if sub-fields exist in grammar.
                            break
            else:  # field not found in grammar
                if self.ta_info['checkunknownentities']:
                    self.add2errorlist(_('[F01]%(linpos)s: Record: "%(mpath)s" has unknown field "%(field)s".\n') %
                                       {'linpos': node_instance.linpos(), 'field': field, 'mpath': self.mpathformat(record_definition[MPATH])})
                del node_instance.record[field]

    def _canonicaltree(self, node_instance, structure):
        ''' For nodes: check min and max occurence; sort the records conform grammar
        '''
        sortednodelist = []
        self._canonicalfields(node_instance, structure)  # handle fields of this record
        if node_instance.structure is None:
            node_instance.structure = structure
        if LEVEL in structure:
            for record_definition in structure[LEVEL]:  # for every record_definition (in grammar) of this level
                count = 0  # count number of occurences of record
                for childnode in node_instance.children:  # for every node in mpathtree; SPEED: delete nodes from list when found
                    # if it is not the right NODE":
                    if childnode.record['BOTSID'] != record_definition[ID] or childnode.record['BOTSIDnr'] != record_definition[BOTSIDNR]:
                        continue
                    count += 1
                    self._canonicaltree(childnode, record_definition)  # use rest of index in deeper level
                    sortednodelist.append(childnode)
                if record_definition[MIN] > count:
                    self.add2errorlist(_('[S03]%(linpos)s: Record "%(mpath)s" occurs %(count)d times, min is %(mincount)d.\n') %
                                       {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'count': count, 'mincount': record_definition[MIN]})
                if record_definition[MAX] < count:
                    self.add2errorlist(_('[S04]%(linpos)s: Record "%(mpath)s" occurs %(count)d times, max is %(maxcount)d.\n') %
                                       {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'count': count, 'maxcount': record_definition[MAX]})
            node_instance.children = sortednodelist

    def _canonicalfields(self, node_instance, record_definition):
        ''' For all fields: check M/C, format.
            Fields are not sorted (a dict can not be sorted).
            Fields are never added.
        '''
        noderecord = node_instance.record
        for field_definition in record_definition[FIELDS]:  # loop over fields in grammar
            if field_definition[ISFIELD]:  # if field (no composite)
                if field_definition[MAXREPEAT] == 1:  # if non-repeating
                    value = noderecord.get(field_definition[ID])
                    if not value:
                        if field_definition[MANDATORY]:
                            self.add2errorlist(_('[F02]%(linpos)s: Record "%(mpath)s" field "%(field)s" is mandatory.\n') %
                                               {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID]})
                        continue
                    noderecord[field_definition[ID]] = self._formatfield(
                        value, field_definition, record_definition, node_instance)
                else:  # repeating field;
                    #a list of values; values can be empty or None; at least one field should have value, else dropped
                    valuelist = noderecord.get(field_definition[ID])
                    if valuelist is None:  # empty lists are already catched in node.put()
                        if field_definition[MANDATORY]:
                            self.add2errorlist(_('[F41]%(linpos)s: Record "%(mpath)s" repeating field "%(field)s" is mandatory.\n') %
                                               {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID]})
                        continue
                    if not isinstance(valuelist, list):
                        raise botslib.MappingFormatError(
                            _('Repeating field: must be a list: put(%(mpath)s)'), {'mpath': valuelist})
                    if len(valuelist) > field_definition[MAXREPEAT]:
                        self.add2errorlist(_('[F42]%(linpos)s: Record "%(mpath)s" repeating field "%(field)s" occurs %(occurs)s times, max is %(max)s.\n') %
                                           {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID],
                                            'occurs': len(valuelist), 'max': field_definition[MAXREPEAT]})
                    newlist = []
                    repeating_field_has_data = False
                    for value in valuelist:
                        if value is None:
                            value = ''
                        else:
                            value = str(value).strip()
                            if value:
                                repeating_field_has_data = True
                        newlist.append(self._formatfield(value, field_definition, record_definition, node_instance))
                    if not repeating_field_has_data:
                        if field_definition[MANDATORY]:
                            self.add2errorlist(_('[F43]%(linpos)s: Record "%(mpath)s" repeating field "%(field)s" is mandatory.\n') %
                                               {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID]})
                        del noderecord[field_definition[ID]]
                        continue
                    noderecord[field_definition[ID]] = newlist
            else:  # composite
                if field_definition[MAXREPEAT] == 1:  # non-repeating compostie
                    #first check if there is any data att all in this composite
                    for grammarsubfield in field_definition[SUBFIELDS]:
                        if noderecord.get(grammarsubfield[ID]):
                            break  # composite has data.
                    else:  # composite has no data
                        if field_definition[MANDATORY]:
                            self.add2errorlist(_('[F03]%(linpos)s: Record "%(mpath)s" composite "%(field)s" is mandatory.\n') %
                                               {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID]})
                        continue  # there is no data in composite, so do nothing
                    #there is data in the composite!
                    for grammarsubfield in field_definition[SUBFIELDS]:  # loop subfields
                        value = noderecord.get(grammarsubfield[ID])
                        if not value:
                            if grammarsubfield[MANDATORY]:
                                self.add2errorlist(_('[F04]%(linpos)s: Record "%(mpath)s" subfield "%(field)s" is mandatory.\n') %
                                                   {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': grammarsubfield[ID]})
                            continue
                        noderecord[grammarsubfield[ID]] = self._formatfield(
                            value, grammarsubfield, record_definition, node_instance)
                else:  # if repeating composite: list of dicts
                    valuelist = noderecord.get(field_definition[ID])
                    #~ print('valuelist',valuelist)
                    if valuelist is None:  # empty lists are catched in node.put()
                        if field_definition[MANDATORY]:
                            self.add2errorlist(_('[F44]%(linpos)s: Record "%(mpath)s" repeating composite "%(field)s" is mandatory.\n') %
                                               {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID]})
                        continue
                    if not isinstance(valuelist, list):
                        raise botslib.MappingFormatError(
                            _('Repeating composite: must be a list: put(%(mpath)s)'), {'mpath': valuelist})
                    if len(valuelist) > field_definition[MAXREPEAT]:
                        self.add2errorlist(_('[F45]%(linpos)s: Record "%(mpath)s" repeating composite "%(field)s" occurs %(occurs)s times, max is %(max)s.\n') %
                                           {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID],
                                            'occurs': len(valuelist), 'max': field_definition[MAXREPEAT]})
                    #is a list of composites; each composite is a dict.
                    #loop over composites/dicts, create a new list
                    #- dict can be empty: {}. check if: composite contains data or is empty
                    #- if composite is not-empty, check M/C of elements in composite
                    #- keys should be basestring.
                    #- convert values to unicode
                    #- check if there is data for whole repeating composite
                    newlist = []
                    repeating_composite_has_data = False
                    for comp in valuelist:
                        if not isinstance(comp, dict):
                            raise botslib.MappingFormatError(
                                _('Repeating composite: each composite must be a dict: put(%(mpath)s)'), {'mpath': valuelist})
                        #check each dict, convert values to unicode
                        #also: check if dict has data at all
                        composite_has_data = False
                        for key, value in list(comp.items()):
                            if not isinstance(key, str):
                                raise botslib.MappingFormatError(
                                    _('Repeating composite: keys must be strings: put(%(mpath)s)'), {'mpath': valuelist})
                            if value is None:
                                comp[key] = ''
                            else:
                                # leading and trailing spaces are stripped from the values
                                comp[key] = str(value).strip()
                                if comp[key]:
                                    composite_has_data = True
                        if composite_has_data:
                            repeating_composite_has_data = True
                            for grammarsubfield in field_definition[SUBFIELDS]:  # loop subfields
                                value = comp.get(grammarsubfield[ID])
                                if not value:
                                    if grammarsubfield[MANDATORY]:
                                        self.add2errorlist(_('[F46]%(linpos)s: Record "%(mpath)s" subfield "%(field)s" in repeating composite is mandatory.\n') %
                                                           {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': grammarsubfield[ID]})
                                    continue
                                comp[grammarsubfield[ID]] = self._formatfield(
                                    value, grammarsubfield, record_definition, node_instance)
                        else:
                            comp = {}
                        newlist.append(comp)
                    if not repeating_composite_has_data:
                        if field_definition[MANDATORY]:
                            self.add2errorlist(_('[F47]%(linpos)s: Record "%(mpath)s" repeating composite "%(field)s" is mandatory.\n') %
                                               {'linpos': node_instance.linpos(), 'mpath': self.mpathformat(record_definition[MPATH]), 'field': field_definition[ID]})

                        del noderecord[field_definition[ID]]
                    else:
                        noderecord[field_definition[ID]] = newlist

    def _logmessagecontent(self, node_instance):
        botsglobal.logger.debug('Record "%(BOTSID)s":', node_instance.record)
        self._logfieldcontent(node_instance.record)  # handle fields of this record
        for child in node_instance.children:
            self._logmessagecontent(child)

    @staticmethod
    def _logfieldcontent(noderecord):
        for key, value in list(noderecord.items()):
            if key not in ['BOTSID', 'BOTSIDnr']:
                botsglobal.logger.debug('    "%(key)s" : "%(value)s"', {'key': key, 'value': value})

    #***************************************************************************
    #* methods below pass call to node.Node ************************************
    #***************************************************************************
    def getrecord(self, *mpaths):
        if self.root.record is None:
            raise botslib.MappingRootError(_('getrecord(%(mpath)s): "root" of incoming message is empty; either split messages or use inn.getloop'),
                                           {'mpath': mpaths})
        return self.root.getrecord(*mpaths)

    def change(self, where, change):
        ''' query tree (self.root) with where; if found replace with change; return True if change, return False if not changed.'''
        if self.root.record is None:
            raise botslib.MappingRootError(_('change(%(where)s,%(change)s): "root" of incoming message is empty; either split messages or use inn.getloop'),
                                           {'where': where, 'change': change})
        return self.root.change(where, change)

    def delete(self, *mpaths):
        ''' query tree (self.root) with mpath; delete if found. return True if deleted, return False if not deleted.'''
        if self.root.record is None:
            raise botslib.MappingRootError(_('delete(%(mpath)s): "root" of incoming message is empty; either split messages or use inn.getloop'),
                                           {'mpath': mpaths})
        return self.root.delete(*mpaths)

    def get(self, *mpaths):
        ''' query tree (self.root) with mpath; get value (string); get None if not found.'''
        if self.root.record is None:
            raise botslib.MappingRootError(_('get(%(mpath)s): "root" of incoming message is empty; either split messages or use inn.getloop'),
                                           {'mpath': mpaths})
        return self.root.get(*mpaths)

    def getnozero(self, *mpaths):
        ''' like get, returns None is value is zero (0) or not numeric.
            Is sometimes usefull in mapping.'''
        if self.root.record is None:
            raise botslib.MappingRootError(_('getnozero(%(mpath)s): "root" of incoming message is empty; either split messages or use inn.getloop'),
                                           {'mpath': mpaths})
        return self.root.getnozero(*mpaths)

    def getdecimal(self, *mpaths):
        ''' like get, returns None is value is zero (0) or not numeric.
            Is sometimes usefull in mapping.'''
        if self.root.record is None:
            raise botslib.MappingRootError(_('getdecimal(%(mpath)s): "root" of incoming message is empty; either split messages or use inn.getloop'),
                                           {'mpath': mpaths})
        return self.root.getdecimal(*mpaths)

    def getcount(self):
        ''' count number of nodes in self.root. Number of nodes is number of records.'''
        return self.root.getcount()

    def getcountoccurrences(self, *mpaths):
        ''' count number of nodes in self.root. Number of nodes is number of records.'''
        return len(list(self.getloop(*mpaths)))

    def getcountsum(self, *mpaths):
        ''' return the sum for all values found in mpath. Eg total number of ordered quantities.'''
        if self.root.record is None:
            raise botslib.MappingRootError(_('get(%(mpath)s): "root" of incoming message is empty; either split messages or use inn.getloop'),
                                           {'mpath': mpaths})
        return self.root.getcountsum(*mpaths)

    def getloop(self, *mpaths):
        ''' query tree with mpath; generates all the nodes. Is typically used as: for record in inn.get(mpath):
        '''
        if self.root.record:  # self.root is a real root
            for terug in self.root.getloop(*mpaths):  # search recursive for rest of mpaths
                yield terug
        else:  # self.root is dummy root
            for childnode in self.root.children:
                for terug in childnode.getloop(*mpaths):  # search recursive for rest of mpaths
                    yield terug

    def getloop_including_mpath(self, *mpaths):
        ''' as getloop, but returns a list: [mpath,mpath,etc,,node] ->node is same as returned by getloop()
        '''
        if self.root.record:  # self.root is a real root
            for terug in self.root.getloop_including_mpath(*mpaths):  # search recursive for rest of mpaths
                yield terug
        else:  # self.root is dummy root
            for childnode in self.root.children:
                for terug in childnode.getloop_including_mpath(*mpaths):  # search recursive for rest of mpaths
                    yield terug

    def put(self, *mpaths, **kwargs):
        if self.root.record is None and self.root.children:
            raise botslib.MappingRootError(_('put(%(mpath)s): "root" of outgoing message is empty; use out.putloop'),
                                           {'mpath': mpaths})
        return self.root.put(*mpaths, **kwargs)

    def putloop(self, *mpaths):
        if not self.root.record:  # no input yet, and start with a putloop(): dummy root
            if len(mpaths) == 1:
                self.root.append(node.Node(record=mpaths[0]))
                return self.root.children[-1]
            else:
                raise botslib.MappingRootError(_('putloop(%(mpath)s): mpath too long???'),
                                               {'mpath': mpaths})
        return self.root.putloop(*mpaths)

    def sort(self, *mpaths):
        if self.root.record is None:
            raise botslib.MappingRootError(_('get(%(mpath)s): "root" of message is empty; either split messages or use inn.getloop'),
                                           {'mpath': mpaths})
        self.root.sort(*mpaths)
