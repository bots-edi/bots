from bots.botsconfig import *

nextmessage = ({'BOTSID':'UNB'},{'BOTSID':'UNH'})
nextmessage2 = ({'BOTSID':'UNB'},{'BOTSID':'UNG'},{'BOTSID':'UNH'})

#works both with/without grouping (UNG-UNE)
#an interchange either consists of message or groups
#by placing UNH-UNT before UNG-UNE no collision will occur
structure = [
    {ID:'UNB',MIN:0,MAX:99999,    
        QUERIES:{
            'frompartner':  {'BOTSID':'UNB','S002.0004':None},
            'topartner':    {'BOTSID':'UNB','S003.0010':None},
            'testindicator':{'BOTSID':'UNB','0035':None}
            },
        LEVEL:		
            [
            {ID:'UNH',MIN:0,MAX:99999,
                QUERIES:{
                    'reference':   {'BOTSID':'UNH','0062':None},
                    },
                SUBTRANSLATION:[
                    {'BOTSID':'UNH','S009.0065':None},
                    {'BOTSID':'UNH','S009.0052':None},
                    {'BOTSID':'UNH','S009.0054':None},
                    {'BOTSID':'UNH','S009.0051':None},
                    {'BOTSID':'UNH','S009.0057':None},
                    ]},
            #note; no UNT in this envelope structure. This is not needed
            #message definitions have a UNT record.
            {ID:'UNG',MIN:0,MAX:99999,
                LEVEL:		
                    [
                    {ID:'UNH',MIN:0,MAX:99999,
                        QUERIES:{
                            'reference':   {'BOTSID':'UNH','0062':None},
                            },
                        SUBTRANSLATION:[
                            {'BOTSID':'UNH','S009.0065':None},
                            {'BOTSID':'UNH','S009.0052':None},
                            {'BOTSID':'UNH','S009.0054':None},
                            {'BOTSID':'UNH','S009.0051':None},
                            {'BOTSID':'UNH','S009.0057':None},
                            ]},
                    {ID:'UNE',MIN:1,MAX:1}
                    ]
                },
            {ID:'UNZ',MIN:1,MAX:1}
            ]
        }
    ]

#updated for syntax version 4 20090623
recorddefs =    {
    'UNB':[
        ['BOTSID','M',3,'A'],
        ['S001', 'M',  
            [
            ['S001.0001', 'M', (4,4), 'A'],
            ['S001.0002', 'M', 1, 'N'],
            ['S001.0080', 'C', 6, 'AN'],
            ['S001.0133', 'C', 3, 'AN'],
            ]],
        ['S002', 'M',
            [
            ['S002.0004', 'M', 35, 'AN'],
            ['S002.0007', 'C', 4, 'AN'],
            ['S002.0008', 'C', 35, 'AN'],
            ['S002.0042', 'C', 35, 'AN'],
            ]],
        ['S003', 'M',
            [
            ['S003.0010', 'M', 35, 'AN'],
            ['S003.0007', 'C', 4, 'AN'],
            ['S003.0014', 'C', 35, 'AN'],
            ['S003.0046', 'C', 35, 'AN'],
            ]],
        ['S004', 'M',
            [
            ['S004.0017', 'M', (6,8), 'AN'],
            ['S004.0019', 'M', (4,4), 'AN'],
            ]],
        ['0020', 'M', 14, 'AN'],
        ['S005', 'C',
            [
            ['S005.0022', 'M', 14, 'AN'],
            ['S005.0025', 'C', 2, 'AN'],
            ]],
        ['0026', 'C', 14, 'AN'],
        ['0029', 'C', 1, 'A'],
        ['0031', 'C', 1, 'N'],
        ['0032', 'C', 35, 'AN'],
        ['0035', 'C', 1, 'N'],
        ],
    'UNG':[
        ['BOTSID','M',3,'A'],
        ['0038', 'M', 6, 'AN'],
        ['S006', 'M',
            [
            ['S006.0040', 'M', 35, 'AN'],
            ['S006.0007', 'C', 4, 'AN'],
            ]],
        ['S007', 'M',
            [
            ['S007.0044', 'M', 35, 'AN'],
            ['S007.0007', 'C', 4, 'AN'],
            ]],
        ['S004', 'M',
            [
            ['S004.0017', 'M', (6,8), 'AN'],
            ['S004.0019', 'M', (4,4), 'AN'],
            ]],
        ['0048', 'M', 14, 'AN'],
        ['0051', 'C', 3, 'AN'],
        ['S008', 'M',
            [
            ['S008.0052', 'M', 3, 'AN'],
            ['S008.0054', 'M', 3, 'AN'],
            ['S008.0057', 'C', 6, 'AN'],
            ]],
        ['0058', 'C', 14, 'AN'],
        ],
    'UNH':[
        ['BOTSID','M',3,'A'],
        ['0062', 'M', 14, 'AN'],
        ['S009', 'M',
            [
            ['S009.0065', 'M', 6, 'AN'],
            ['S009.0052', 'M', 3, 'AN'],
            ['S009.0054', 'M', 3, 'AN'],
            ['S009.0051', 'M', 2, 'AN'],
            ['S009.0057', 'C', 6, 'AN'],
            ['S009.0110', 'C', 6, 'AN'],
            ['S009.0113', 'C', 6, 'AN'],
            ]],
        ['0068', 'C', 35, 'AN'],
        ['S010', 'C',
            [
            ['S010.0070', 'M', 2, 'N'],
            ['S010.0073', 'C', 1, 'A'],
            ]],
        ['S016', 'C',
            [
            ['S016.0115', 'M', 14, 'A'],
            ['S016.0116', 'C', 3, 'A'],
            ['S016.0118', 'C', 3, 'A'],
            ['S016.0051', 'C', 3, 'A'],
            ]],
        ['S017', 'C',
            [
            ['S017.0121', 'M', 14, 'A'],
            ['S017.0122', 'C', 3, 'A'],
            ['S017.0124', 'C', 3, 'A'],
            ['S017.0051', 'C', 3, 'A'],
            ]],
        ['S018', 'C',
            [
            ['S018.0127', 'M', 14, 'A'],
            ['S018.0128', 'C', 3, 'A'],
            ['S018.0130', 'C', 3, 'A'],
            ['S018.0051', 'C', 3, 'A'],
            ]],
        ],
    'UNT':[
        ['BOTSID','M',3,'A'],
        ['0074', 'M', 6, 'N'],
        ['0062', 'M', 14, 'AN'],
        ],
    'UNE':[
        ['BOTSID','M',3,'A'],
        ['0060', 'M', 6, 'N'],
        ['0048', 'M', 14, 'AN'],
        ],
    'UNZ':[
        ['BOTSID','M',3,'A'],
        ['0036', 'M', 6, 'N'],
        ['0020', 'M', 14, 'AN'],
        ],
    }
