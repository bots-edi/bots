from bots.botsconfig import *

structure= [
  { 
    ID:'HEA',
    MIN:1,
    MAX:1,
    LEVEL: [
      {
        ID: 'union', 
        MIN:1, 
        MAX:1,
        LEVEL: [
          {
            ID: 'com.acme.avro.A', 
            MIN:0, 
            MAX:1
          },
          {
            ID: 'com.acme.avro.B', 
            MIN:0, 
            MAX:1
          }
        ]
      }
    ]
  }
]
    
recorddefs = {
  'HEA':[
    ['BOTSID','M', 3, 'A'],
    ['BOGUS', 'C', 3, 'A']
  ],
  'union': [
    ['BOTSID', 'M', 5, 'A'],
    ['AVRO_RECORD_NAME', 'C', 15, 'A']
  ],
  'com.acme.avro.A': [
    ['BOTSID', 'M', 15, 'A'],
    ['id', 'M', 99, 'A']
  ],
  'com.acme.avro.B': [
    ['BOTSID', 'M', 15, 'A'],
    ['id', 'M', 99, 'A']
  ]
}
