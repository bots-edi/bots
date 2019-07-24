# -*- coding: utf-8 -*-

# constants/definitions for Bots
# to be used as:
# from botsconfig import *

# ***for statust in ta:
OPEN = 0  # Bots always closes transaction. OPEN is severe error
ERROR = 1  # error in transaction.
OK = (
    2
)  # successfull, result is 'save'. Should be picked up in same run. If automatic evaluation finds this: is 'stuck'.
DONE = 3  # successfull, and result is picked up by next step
RESEND = 4  # file has been resend.
NO_RETRY = 5  # file has been resend.

# ***for status in ta:
PROCESS = 1
DISCARD = 3

EXTERNIN = 200  # file is imported into bots
FILEIN = 220  # received edifile
PARSED = 310  # edifile is lexed and parsed
SPLITUP = 320  # messages in the edifile have been split up
TRANSLATED = 330  # result of translation
MERGED = 400  # envelope and/or merged.
FILEOUT = 500  # file is enveloped; ready for out
EXTERNOUT = 520  # file is exported

# ***grammar.structure: keys in grammarrecords (dicts)
ID = 0
MIN = 1
MAX = 2
COUNT = 3
LEVEL = 4
MPATH = 5
FIELDS = 6
QUERIES = 7
SUBTRANSLATION = 8
BOTSIDNR = 9
FIXED_RECORD_LENGTH = 10  # length of fixed record

# ***grammar.recorddefs: dict keys for fields of record eg: record[FIELDS][ID] == 'C124.0034'
# ID = 0 (is already defined)
MANDATORY = 1
LENGTH = 2
SUBFIELDS = 2  # for composites
FORMAT = 3  # format in grammar file
ISFIELD = 4
DECIMALS = 5
MINLENGTH = 6
BFORMAT = 7  # internal bots format; formats in grammar are converted to bformat
MAXREPEAT = 8

# ***lex_record in self.lex_records: is a dict
VALUE = 0
SFIELD = 1  # 1: is subfield, 0: field or first element composite
LIN = 2
POS = 3
FIXEDLINE = 4  # for fixed records; tmp storage of fixed record
FORMATFROMGRAMMAR = 5  # to store FORMAT field has in grammar
