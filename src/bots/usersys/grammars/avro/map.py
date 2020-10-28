from bots.botsconfig import *

structure= [
  { 
    ID:'HEA',
    MIN:1,
    MAX:1,
    LEVEL: [
      { ID: 'map', MIN:1, MAX:9999 }
    ]
  }
]
    
recorddefs = {
  'HEA':[
    ['BOTSID','M', 3, 'A'],
    ['BOGUS', 'C', 3, 'A']
  ],
  'map': [
    ['BOTSID', 'M', 5, 'A'],
    ['AVRO_MAP', 'C', 5, 'A'],
    ['key', 'M', 256, 'AN'],
    ['value', 'M', 256, 'AN']
  ]
}
