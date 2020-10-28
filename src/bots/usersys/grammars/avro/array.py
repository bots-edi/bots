from bots.botsconfig import *

structure= [
  { 
    ID:'HEA',
    MIN:1,
    MAX:1,
    LEVEL: [
      {ID: 'array', MIN: 0, MAX: 99999 }
    ]
  }
]
    
recorddefs = {
  'HEA':[
    ['BOTSID','M', 3, 'A'],
    ['BOGUS','C', 3, 'A']
  ],
  'array': [
    ['BOTSID','M', 5, 'A'],
    ['AVRO_ARRAY','M', 5, 'A'],
    ['input','C', 256, 'AN']
  ]
}
