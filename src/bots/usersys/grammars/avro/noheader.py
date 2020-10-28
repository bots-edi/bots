from bots.botsconfig import *

syntax = {
  'noHeader': True
}

structure=    [
  { ID:'HEA', MIN:1, MAX:1 }
]
    
recorddefs = {
  'HEA':[
          ['BOTSID','C',3,'A'],
          ['name', 'M', 256, 'AN'],          
          ['favorite_number', 'C', 256, 'AN'],         
          ['favorite_color', 'C', 256, 'AN'] 
        ]
}
