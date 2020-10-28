from bots.botsconfig import *

structure= [
  { 
    ID:'HEA',
    MIN:1,
    MAX:1
  }
]
    
recorddefs = {
  'HEA':[
    ['BOTSID','M', 3, 'A'],
    ['enum', 'M', 256, {'ENUM': ['SPADES', 'HEARTS', 'DIAMONDS', 'CLUBS']}]
  ]
}
