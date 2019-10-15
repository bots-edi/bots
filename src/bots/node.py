# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import sys
if sys.version_info[0] > 2:
    basestring = unicode = str
try:
    import cdecimal as decimal
except ImportError:
    import decimal
from django.utils.translation import ugettext as _
#bots-modules
from . import botslib
from . import botsglobal
from .botsconfig import *


class Node(object):
    ''' Node class for building trees in inmessage and outmessage
    '''
    #slots: python optimalisation to preserve memory. Disadv.: no dynamic attr in this class
    #in tests: for normal translations less memory and faster; no effect fo one-on-one translations.
    __slots__ = ('record', 'children', '_queries', 'linpos_info', 'structure')

    def __init__(self, record=None, linpos_info=None):
        if record and 'BOTSIDnr' not in record:
            record['BOTSIDnr'] = '1'
        self.record = record  # record is a dict with fields
        self.children = []
        self.linpos_info = linpos_info
        self._queries = None
        self.structure = None

    def linpos(self):
        if self.linpos_info:
            return ' line %(lin)s pos %(pos)s' % {'lin': self.linpos_info[0], 'pos': self.linpos_info[1]}
        else:
            return ''

    def append(self, childnode):
        '''append child to node'''
        self.children.append(childnode)

    #********************************************************
    #*** queries ********************************************
    #********************************************************
    def _getquerie(self):
        ''' getter for queries: get queries of a node '''
        if self._queries:
            return self._queries
        else:
            return {}

    def _updatequerie(self, updatequeries):
        ''' setter for queries: set/update queries of a node with dict queries.
        '''
        if updatequeries:
            if self._queries is None:
                self._queries = updatequeries.copy()
            else:
                botslib.updateunlessset(self._queries, updatequeries)

    queries = property(_getquerie, _updatequerie)

    def processqueries(self, queries, maxlevel):
        ''' copies values for queries 'down the tree' untill right level.
            So when edi file is split up in messages,
            querie-info from higher levels is copied to message.'''
        self.queries = queries
        if self.record and not maxlevel:
            return
        for childnode in self.children:
            childnode.processqueries(self.queries, maxlevel - 1)

    def displayqueries(self, level=0):
        '''for debugging
            usage: in mappingscript:     inn.root.displayqueries()
        '''
        if level == 0:
            print('displaying queries for nodes in tree')
        print('    ' * level, 'node:', end='')
        if self.record:
            print(self.record['BOTSID'], end='')
        else:
            print('None', end='')
        print('', end='')
        print(self.queries)
        for childnode in self.children:
            childnode.displayqueries(level + 1)

    #********************************************************
    #*** handling of QUERIES and SUBTRANSLATION *************
    #********************************************************
    def enhancedget(self, mpaths):
        ''' to get QUERIES, SUBTRANSLATION or nextmessageblock.
            mpaths can be
            - dict:     do one get(mpaths); can not be a mpath quering one level deeper->in that case use a tuple: ({'BOTSID':'ISA'},{'BOTSID':'GS','GS02':None})
            - tuple:    do one get(mpaths); can be multiple dicts in mpaths
            - list:     for each list member do a get(); append the results
            - function: user exit that returns a value (or None, if not found)
            - string:   return that string
        '''
        if isinstance(mpaths, dict):
            return self.get(mpaths)
        elif isinstance(mpaths, tuple):
            return self.get(*mpaths)
        elif isinstance(mpaths, list):
            lijst = [self.enhancedget(mpath) for mpath in mpaths]  # go recursive
            return ''.join(str(part).strip() for part in lijst if part is not None)
        elif callable(mpaths):
            return mpaths(thisnode=self)
        elif isinstance(mpaths, basestring):
            return mpaths
        else:
            raise botslib.MappingFormatError(
                _('Errors in mpath for QUERIES, SUBTRANSLATION or nextmessageblock; you used %(mpath)s.'), {'mpath': mpaths})

    def get_queries_from_edi(self, record_definition):
        ''' extract information from edifile using QUERIES in grammar.structure; information will be placed in ta_info and in db-ta
        '''
        tmpdict = {}
        for key, value in record_definition[QUERIES].items():
            found = self.enhancedget(value)  # search in last added node
            if found is not None:
                found = found.strip()  # needed to get correct ISA-fields
                if found:
                    tmpdict[key] = found
        self.queries = tmpdict

    #********************************************************
    #*** manipulate node.tree: get, put, change, delete etc *
    #********************************************************
    def getrecord(self, *mpaths):
        ''' get whole node record
        '''
        self._mpath_sanity_check(mpaths)
        for part in mpaths:
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        terug = self._getrecordcore(mpaths)
        botsglobal.logmap.debug('"%(terug)s" for getrecord%(mpaths)s', {
                                'terug': unicode(terug), 'mpaths': unicode(mpaths)})
        return terug

    def _getrecordcore(self, mpaths):
        for key, value in mpaths[0].items():  # check all key, value for first part of where;
            if key not in self.record or value != self.record[key]:
                return None  # no match:
        else:  # all key,value are matched.
            if len(mpaths) == 1:  # mpath is exhausted; so we are there!!! #replace values with values in 'change'; delete if None
                return self.record
            else:  # go recursive
                for childnode in self.children:
                    terug = childnode._getrecordcore(mpaths[1:])
                    if terug:
                        return terug
                else:  # no child has given a valid return
                    return None

    def change(self, where, change):
        ''' where: node to find.
            change is applied to found node
            uses first matching node for 'where'.
        '''
        self._mpath_sanity_check(where)
        for part in where:
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        #sanity check 'change' parameter
        if not isinstance(change, dict):
            raise botslib.MappingFormatError(_('Parameter "change" must be dict: change(where=%(where)s,change=%(change)s)'),
                                             {'where': where, 'change': change})
        change.pop('BOTSID', 'nep')  # remove 'BOTSID' from change. BOTSID can not be changed
        change.pop('BOTSIDnr', 'nep')  # remove 'BOTSIDnr' from change. BOTSIDnr can not be changed
        for key, value in change.items():
            if not isinstance(key, basestring):
                raise botslib.MappingFormatError(_('Keys in "change" must be strings: change(where=%(where)s,change=%(change)s)'),
                                                 {'where': where, 'change': change})
            if value is None:  # if None, item is deleted
                pass
            elif isinstance(value, list):  # for now, just pass lists
                pass
            else:
                change[key] = unicode(value).strip()  # leading and trailing spaces are stripped from the values
        terug = self._changecore(where, change)
        botsglobal.logmap.debug('"%(terug)s" for change(where=%(where)s,change=%(change)s)', {
                                'terug': terug, 'where': unicode(where), 'change': unicode(change)})
        return terug

    def _changecore(self, where, change):
        for key, value in where[0].items():  # check all key, value for first part of where;
            if key not in self.record or value != self.record[key]:
                return False  # no match:
        else:  # all key,value are matched.
            if len(where) == 1:  # mpath is exhausted; so we are there!!! #replace values with values in 'change'; delete if None
                for key, value in change.items():
                    if value is None:
                        self.record.pop(key, 'nep')
                    else:
                        self.record[key] = value
                return True
            else:  # go recursive
                for childnode in self.children:
                    if childnode._changecore(where[1:], change):
                        return True
                else:  # no child has given a valid return
                    return False

    def delete(self, *mpaths):
        ''' delete the last record of mpath if found (first: find/identify record, than delete).'''
        self._mpath_sanity_check(mpaths)
        if len(mpaths) == 1:
            raise botslib.MappingFormatError(
                _('Only one dict: not allowed. Use different solution: delete(%(mpath)s)'), {'mpath': mpaths})
        for part in mpaths:
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        terug = bool(self._deletecore(mpaths))
        botsglobal.logmap.debug('"%(terug)s" for delete%(mpaths)s', {'terug': terug, 'mpaths': unicode(mpaths)})
        return terug  # return False if not removed, return True if removed

    def _deletecore(self, mpaths):
        for key, value in mpaths[0].items():  # check all items in first part of mpaths
            if key not in self.record or value != self.record[key]:
                return 0
        else:  # all items are matched
            if len(mpaths) == 1:  # mpath is exhausted; so we are there!!!
                return 2  # indicates node should be removed
            else:
                for i, childnode in enumerate(self.children):
                    terug = childnode._deletecore(mpaths[1:])  # search recursive for rest of mpaths
                    if terug == 2:  # indicates node should be removed
                        del self.children[i]  # remove node
                        return 1  # this indicates: deleted successfull, do not remove anymore (no removal of parents)
                    if terug:
                        return terug
                else:  # no child has given a valid return
                    return 0

    def get(self, *mpaths):
        ''' get value of a field in a record from a edi-message
            mpath is xpath-alike query to identify the record/field
            function returns 1 value; return None if nothing found.
            if more than one value can be found: first one is returned
            starts searching in current node, then deeper
        '''
        if Node.checklevel:
            self._mpath_sanity_check(mpaths[:-1])
            #sanity check of last part of mpaths: None only allowed in last section of Mpath; check last part
            if not isinstance(mpaths[-1], dict):
                raise botslib.MappingFormatError(_('Must be dicts in tuple: get(%(mpath)s)'), {'mpath': mpaths})
            if 'BOTSID' not in mpaths[-1]:
                raise botslib.MappingFormatError(_('Last section without "BOTSID": get(%(mpath)s)'), {'mpath': mpaths})
            count = 0
            for key, value in mpaths[-1].items():
                if not isinstance(key, basestring):
                    raise botslib.MappingFormatError(
                        _('Keys must be strings in last section: get(%(mpath)s)'), {'mpath': mpaths})
                if value is None:
                    count += 1
                elif not isinstance(value, basestring):
                    raise botslib.MappingFormatError(
                        _('Values must be strings (or none) in last section: get(%(mpath)s)'), {'mpath': mpaths})
            if count > 1:
                raise botslib.MappingFormatError(_('Max one "None" in last section: get(%(mpath)s)'), {'mpath': mpaths})
        for part in mpaths:
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        if Node.checklevel == 2:
            self._mpath_grammar_check(mpaths)
        terug = self._getcore(mpaths)
        botsglobal.logmap.debug('"%(terug)s" for get%(mpaths)s', {'terug': terug, 'mpaths': unicode(mpaths)})
        return terug

    def _getcore(self, mpaths):
        if len(mpaths) != 1:  # node is not end-node
            for key, value in mpaths[0].items():  # check all items in mpath;
                if key not in self.record or value != self.record[key]:  # does not match/is not right node
                    return None
            else:  # all items in mpath are matched and OK; recursuve search
                for childnode in self.children:
                    terug = childnode._getcore(mpaths[1:])  # recursive search for rest of mpaths
                    if terug is not None:
                        return terug
                else:  # nothing found in children
                    return None
        else:  # node is end-node
            # default return value: if there is no 'None' in the mpath, but everything
            # is matched, 1 is returned (like True)
            terug = 1
            for key, value in mpaths[0].items():  # check all items in mpath;
                if key not in self.record:  # does not match/is not right node
                    return None
                elif value is None:  # item has None-value; remember this value because this might be the right node
                    terug = self.record[key][:]  # copy to avoid memory problems
                elif value != self.record[key]:  # compare values
                    return None  # does not match/is not right node
            else:  # all keys/values in this mpathr are matched and OK.
                return terug  # either the remembered value is returned or 1 (as a boolean, indicated 'found)

    def getcount(self):
        '''count the number of nodes/records under the node/in whole tree'''
        count = 0
        if self.record:
            count += 1  # count itself
        for childnode in self.children:
            count += childnode.getcount()
        return count

    def getcountoccurrences(self, *mpaths):
        ''' count number of occurences of mpath. Eg count nr of LIN's'''
        return len(list(self.getloop(*mpaths)))

    def getcountsum(self, *mpaths):
        ''' return the sum for all values found in mpath. Eg total number of ordered quantities.'''
        mpath_for_found_node = mpaths[-1].copy()
        for key, value in list(mpaths[-1].items()):
            if value is None:
                del mpaths[-1][key]
        count = decimal.Decimal(0)
        for i in self.getloop(*mpaths):
            count += i.getdecimal(mpath_for_found_node)
        return unicode(count)

    def getloop(self, *mpaths):
        ''' generator. Returns one by one the nodes as indicated in mpath
        '''
        if Node.checklevel:
            self._mpath_sanity_check(mpaths)
        for part in mpaths:
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        if Node.checklevel == 2:
            self._mpath_grammar_check(mpaths)
        for terug in self._getloopcore(mpaths):
            botsglobal.logmap.debug('getloop %(mpaths)s returns "%(record)s".',
                                    {'mpaths': mpaths, 'record': terug.record})
            yield terug

    def _getloopcore(self, mpaths):
        ''' recursive part of getloop()
        '''
        for key, value in mpaths[0].items():
            if key not in self.record or value != self.record[key]:
                return
        else:  # all items are checked and OK.
            if len(mpaths) == 1:
                yield self  # found!
            else:
                for childnode in self.children:
                    for terug in childnode._getloopcore(mpaths[1:]):  # search recursive for rest of mpaths
                        yield terug

    def getloop_including_mpath(self, *mpaths):
        ''' generator. Returns one by one the nodes as indicated in mpath
            like getloop(), but returns a list: [mpath,mpath,etc,,node] ->node is same as returned by getloop()
        '''
        if Node.checklevel:
            self._mpath_sanity_check(mpaths)
        for part in mpaths:
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        if Node.checklevel == 2:
            self._mpath_grammar_check(mpaths)
        for terug in self._getloopcore_including_mpath(mpaths):
            botsglobal.logmap.debug('getloop %(mpaths)s returns "%(terug)s".', {'mpaths': mpaths, 'terug': terug})
            yield terug

    def _getloopcore_including_mpath(self, mpaths):
        ''' recursive part of getloop()
        '''
        for key, value in mpaths[0].items():
            if key not in self.record or value != self.record[key]:
                return
        else:  # all items are checked and OK.
            if len(mpaths) == 1:
                yield [self]  # found!
            else:
                for childnode in self.children:
                    # search recursive for rest of mpaths
                    for terug in childnode._getloopcore_including_mpath(mpaths[1:]):
                        yield [self.record] + terug if terug is not None else None

    #~ def get_for_sort(self,*mpaths):
        #~ ''' like get, but either returns a value or '' (empty string). If get() delivers None, return as ''.
            #~ used by sort()
        #~ '''
        #~ terug = self.get(*mpaths)
        #~ if not terug:
            #~ return ''
        #~ return terug

    def getnozero(self, *mpaths):
        ''' like get, but either return a numerical value (as string) or None. If value to return is equal to zero, None is returned.
            useful eg for fixed records, where num fields are initialised with zeroes.
        '''
        terug = self.get(*mpaths)
        try:
            value = float(terug)
        except (TypeError, ValueError):
            return None
        if value == 0:
            return None
        return terug

    def getdecimal(self, *mpaths):
        ''' like get, but return a decimal value. If value to return is None or not numeric, zero is returned.
            warning: this function might 'mask' errors, because when input is not-valid, it aalwyas return a decimal 0.
            useful eg for when math calculations are needed in mapping.
        '''
        terug = self.get(*mpaths)
        # if minus-sign at the end, put it in front. This is useful for idocs,
        # where fields are never defined as numeric.
        if terug and terug[-1] == '-':
            terug = terug[-1] + terug[:-1]
        try:
            return decimal.Decimal(terug)
        except (TypeError, ValueError):
            return decimal.Decimal('0')

    def put(self, *mpaths, **kwargs):
        #sanity check of mpaths
        if not mpaths or not isinstance(mpaths, tuple):
            raise botslib.MappingFormatError(_('Must be dicts in tuple: put(%(mpath)s)'), {'mpath': mpaths})
        for part in mpaths:
            if not isinstance(part, dict):
                raise botslib.MappingFormatError(_('Must be dicts in tuple: put(%(mpath)s)'), {'mpath': mpaths})
            if 'BOTSID' not in part:
                raise botslib.MappingFormatError(_('Section without "BOTSID": put(%(mpath)s)'), {'mpath': mpaths})
            for key, value in part.items():
                if value is None:
                    botsglobal.logmap.debug('"None" in put %(mpaths)s.', {'mpaths': unicode(mpaths)})
                    return False
                if not isinstance(key, basestring):
                    raise botslib.MappingFormatError(_('Keys must be strings: put(%(mpath)s)'), {'mpath': mpaths})
                if isinstance(value, list):
                    #empty is not useful, drop it (like None)
                    if not value:
                        botsglobal.logmap.debug('Empty list in put %(mpaths)s.', {'mpaths': unicode(mpaths)})
                        return False
                else:
                    if kwargs.get('strip', True):
                        part[key] = unicode(value).strip()  # leading and trailing spaces are stripped from the values
                    else:
                        part[key] = unicode(value)  # used for fixed ISA header of x12
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'

        if self._sameoccurence(mpaths[0]):
            self._putcore(mpaths[1:])
        else:
            raise botslib.MappingRootError(_('Error in root put "%(mpath)s".'), {'mpath': mpaths[0]})
        botsglobal.logmap.debug('"True" for put %(mpaths)s', {'mpaths': unicode(mpaths)})
        return True

    def _putcore(self, mpaths):
        if not mpaths:  # newmpath is exhausted, stop searching.
            return
        for childnode in self.children:
            # checking of BOTSID is also done in sameoccurance!->performance!
            if childnode.record['BOTSID'] == mpaths[0]['BOTSID'] and childnode._sameoccurence(mpaths[0]):
                childnode._putcore(mpaths[1:])
                return
        else:  # is not present in children, so append mpath as a new node
            self.append(Node(mpaths[0]))
            self.children[-1]._putcore(mpaths[1:])

    def putloop(self, *mpaths):
        #sanity check of mpaths
        if not mpaths or not isinstance(mpaths, tuple):
            raise botslib.MappingFormatError(_('Must be dicts in tuple: putloop(%(mpath)s)'), {'mpath': mpaths})
        for part in mpaths:
            if not isinstance(part, dict):
                raise botslib.MappingFormatError(_('Must be dicts in tuple: putloop(%(mpath)s)'), {'mpath': mpaths})
            if 'BOTSID' not in part:
                raise botslib.MappingFormatError(_('Section without "BOTSID": putloop(%(mpath)s)'), {'mpath': mpaths})
            for key, value in part.items():
                if not isinstance(key, basestring):
                    raise botslib.MappingFormatError(_('Keys must be strings: putloop(%(mpath)s)'), {'mpath': mpaths})
                if value is None:
                    return False
                part[key] = unicode(value).strip()
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        if self._sameoccurence(mpaths[0]):
            if len(mpaths) == 1:
                return self
            return self._putloopcore(mpaths[1:])
        else:
            raise botslib.MappingRootError(_('Error in root putloop "%(mpath)s".'), {'mpath': mpaths[0]})

    def _putloopcore(self, mpaths):
        if len(mpaths) == 1:  # end of mpath reached; always make new child-node
            self.append(Node(mpaths[0]))
            return self.children[-1]
        for childnode in self.children:  # if first part of mpaths exists already in children go recursive
            # checking of BOTSID is also done in sameoccurance!->performance!
            if childnode.record['BOTSID'] == mpaths[0]['BOTSID'] and childnode._sameoccurence(mpaths[0]):
                return childnode._putloopcore(mpaths[1:])
        else:  # is not present in children, so append a child, and go recursive
            self.append(Node(mpaths[0]))
            return self.children[-1]._putloopcore(mpaths[1:])

    def _sameoccurence(self, mpath):
        ''' checks if all items that appear in both node and mpath have the same value. If so, all new items in mpath are added to node
        '''
        for key, value in self.record.items():
            if key in mpath and mpath[key] != value:
                return False
        else:  # all equal keys have same values, thus both are 'equal'.
            self.record.update(mpath)  # add items to self.record that are new
            return True

    def sort(self, *mpaths):
        ''' sort nodes. eg in mappingscript:
            1a. inn.sort({'BOTSID':'UNH'},{'BOTSID':'LIN','C212.7140':None})    -> sorts the LIN segments by article number.
            1b. inn.sort(sortfrom=({'BOTSID':'UNH'},),compare=({'BOTSID':'LIN','C212.7140':None},))    -> sorts the LIN segments by article number.
            2a. inn.sort({'BOTSID':'envelope'},{'BOTSID':'message'},{'BOTSID':'lines'},{'BOTSID':'line','gtin':None}) -> sorts lines by GTIN
            2b. inn.sort({'BOTSID':'envelope'},{'BOTSID':'message'},{'BOTSID':'lines'},{'BOTSID':'line','gtin':None}) -> sorts lines by GTIN
            3a. inn.sort({'BOTSID':'UNH'},{'BOTSID':'LIN'},{'BOTSID':'QTY','C186.6063':'12','C186.6060':None})    -> sorts the LIN segments according to quantityby article number.
            3b. inn.sort({'BOTSID':'UNH'},{'BOTSID':'LIN'},{'BOTSID':'QTY','C186.6063':'12','C186.6060':None})    -> sorts the LIN segments according to quantityby article number.
            version <= 3.2 only had mpaths as parameters; extended this in order to be upward compatible. mpath was split in sort_from_node and comparekey
            Case 3 can not be done with old parameter.
            new parameters (in **kwargs)
            - sort_from_node
            - comparekey
            - reverse - as reverse in python's sort
            - sort_if_none: if comparekey not there; should these be sorted as last or first. None is lowest, none is highest
            - sort_decimal: numerical sort
        '''
        if Node.checklevel:
            self._mpath_sanity_check(mpaths[:-1])
            #sanity check of last part of mpaths: None only allowed in last section of Mpath; check last part
            if not isinstance(mpaths[-1], dict):
                raise botslib.MappingFormatError(_('Must be dicts in tuple: get(%(mpath)s)'), {'mpath': mpaths})
            if 'BOTSID' not in mpaths[-1]:
                raise botslib.MappingFormatError(_('Last section without "BOTSID": get(%(mpath)s)'), {'mpath': mpaths})
            count = 0
            for key, value in mpaths[-1].items():
                if not isinstance(key, basestring):
                    raise botslib.MappingFormatError(
                        _('Keys must be strings in last section: get(%(mpath)s)'), {'mpath': mpaths})
                if value is None:
                    count += 1
                elif not isinstance(value, basestring):
                    raise botslib.MappingFormatError(
                        _('Values must be strings (or none) in last section: get(%(mpath)s)'), {'mpath': mpaths})
            if count > 1:
                raise botslib.MappingFormatError(_('Max one "None" in last section: get(%(mpath)s)'), {'mpath': mpaths})
        for part in mpaths:
            if 'BOTSIDnr' not in part:
                part['BOTSIDnr'] = '1'
        if Node.checklevel == 2:
            self._mpath_grammar_check(mpaths)
        remember = Node.checklevel
        Node.checklevel = 0
        comparekey = mpaths[-1:]
        sort_from_node = mpaths[:-1]
        try:
            for n in self.getloop(*sort_from_node):
                n.children.sort(key=lambda s: s.get(*comparekey))
        finally:
            Node.checklevel = remember

        #~ comparekey = mpaths[1:]
        #~ #does not work with checklevel == 2, so temporary set checklevel to 0
        #~ remember = Node.checklevel
        #~ Node.checklevel = 0
        #~ try:
            #~ self.children.sort(key=lambda s: s.get_for_sort(*comparekey))
        #~ finally:
            #~ Node.checklevel = remember
    #********************************************************
    #*** utility functions **********************************
    #********************************************************
    @staticmethod
    def _mpath_sanity_check(mpaths):
        ''' sanity check of mpaths. '''
        if not isinstance(mpaths, tuple):
            raise botslib.MappingFormatError(_('Parameter mpath must be tuple: %(mpaths)s'), {'mpaths': mpaths})
        for part in mpaths:
            if not isinstance(part, dict):
                raise botslib.MappingFormatError(
                    _('Parameter mpath must be dicts in a tuple: %(mpaths)s'), {'mpaths': mpaths})
            if 'BOTSID' not in part:
                raise botslib.MappingFormatError(_('"BOTSID" is required in mpath: %(mpaths)s'), {'mpaths': mpaths})
            for key, value in part.items():
                if not isinstance(key, basestring):
                    raise botslib.MappingFormatError(_('Keys must be strings in mpath: %(mpaths)s'), {'mpaths': mpaths})
                if not isinstance(value, basestring):
                    raise botslib.MappingFormatError(
                        _('Values must be strings in mpath: getrecord(%(mpaths)s)'), {'mpaths': mpaths})

    def _mpath_grammar_check(self, mpaths):
        ''' check of mpaths with grammar. '''
        def _mpath_ok_with_grammar(structure, mpaths):
            ''' inner function, recursive.
                every part of mpaths should be in structure, at right level, have right fields.
            '''
            mpath = mpaths[0]
            for record_definition in structure:
                if record_definition[ID] == mpath['BOTSID'] and record_definition[BOTSIDNR] == mpath['BOTSIDnr']:
                    for key in mpath:
                        if key == 'BOTSIDnr':  # BOTSIDnr is not in grammar, so do not check
                            continue
                        for field_definition in record_definition[FIELDS]:
                            if field_definition[ISFIELD]:
                                if key == field_definition[ID]:
                                    break  # check next key
                            else:
                                if key == field_definition[ID]:  # first check compostie-key itself, for repeating composites
                                    break  # check next key
                                for grammarsubfield in field_definition[SUBFIELDS]:  # loop subfields
                                    if key == grammarsubfield[ID]:
                                        break  # check next key
                                else:
                                    continue  # checking field_defintions
                                break  # check next key
                        else:  # Not found in record!
                            return False
                    #all fields in mpath are correct; go to next level of mpath..
                    if mpaths[1:]:
                        if not LEVEL in record_definition:
                            return False
                        return _mpath_ok_with_grammar(record_definition[LEVEL], mpaths[1:])
                    else:
                        return True  # no more levels, all fields found
            else:
                return False
        if not self.structure:
            return
        if not _mpath_ok_with_grammar([self.structure], mpaths):
            raise botslib.MappingFormatError(
                _('Parameter mpath is not valid according to grammar: %(mpaths)s'), {'mpaths': mpaths})

    def display(self, level=0):
        '''for debugging
            usage eg in mappingscript:     inn.root.display()
        '''
        if level == 0:
            print('displaying all nodes in node tree:')
        print('    ' * level, self.record)
        for childnode in self.children:
            childnode.display(level + 1)

    def stripnode(self):
        ''' removes spaces from all fields in tree.
            used in alt translations where a dict is returned by mappingscript indicating the out-tree should be used as inn.
            the out-tree has been formatted already, this is not OK for fixed formats (idoc!)
        '''
        if self.record is not None:
            for key, value in self.record.items():
                self.record[key] = value.strip()
        for child in self.children:
            child.stripnode()

    def collectlines(self, print_as_row):
        ''' for new edifax routine: collect same nodes in Node.children in a list; for table-row printing.
        '''
        new = []  # new list
        for childnode in self.children:
            if childnode.structure[MPATH] in print_as_row:
                if not new:  # if new is still empty
                    new.append([childnode])
                elif isinstance(new[-1], list) and new[-1][0].record['BOTSID'] == childnode.record['BOTSID']:
                    new[-1].append(childnode)  # append in tabel-row-list
                else:  # other recordID, also print as table-row
                    new.append([childnode])
            else:  # just append, no change
                new.append(childnode)
                childnode.collectlines(print_as_row)  # go recursive
        self.children = new

    def copynode(self):
        ''' make a 'safe' copy of node; return the new node
        '''
        if self.record is None:
            new_node = Node(record=None)
        else:
            new_node = Node(record=dict(self.record))
        for childnode in self.children:
            new_node.append(childnode.copynode())
        return new_node
