from bots.botsconfig import *
from bots.usersys.grammars.edifact.envelope import recorddefs,structure,nextmessage,nextmessage2

syntax = { 
        'envelope'   :  'edifact',	#for outgoing edifact-messages: this is the envelope to use in merge()
        'charset'   :  'UNOA',	#for outgoing edifact-messages: this is the envelope to use in merge()
        'version'    :  '3',    #for outgong: value to use in UNB
        }
