from bots.botsconfig import *

structure=    [
{ID:'HEA',MIN:1,MAX:1}
]
    
recorddefs = {
    'HEA':[
            ['BOTSID','C',3, 'A'],
            ['string', 'M', 100, 'AN'],
            ['boolean', 'M', 5, 'B'],
            ['int', 'M', 11, 'N'],
            ['long', 'M', 20, 'N'],
            ['float', 'M', 7, 'R'],
            ['double', 'M', 16, 'R'],
            ['null', 'C', 100, 'AN'],
            ['null2', 'C', 100, 'AN']
          ]
     }
