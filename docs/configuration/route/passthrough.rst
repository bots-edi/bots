PassThrough (no translation)
============================

Sometimes you want to pass an edi-file though bots without translation.
In this case bots is only used to manage/register the sending or receiving of edi-files.

**For bots>=3.0**

In route (``bots-monitor->Configuration->Routes``) use value **Pass-through** for **translate**.


**For bots<=2.2**

Use a routescript:

#. Configure route the normal way (bots-monitor->Configuration->Routes)
#. Make a routescript with the same name as the routeID
#. Place the routescript in bots/usersys/routescripts/routeid.py

Contents of routescript:

.. code-block:: python

    from bots.botsconfig import *
    import bots.transform as transform

    def postincommunication(routedict,*args,**kwargs): 
        # postincommunication() is run after fromchannel communication.
        # the status of incoming files is changed to outgoing. 
        # bots skips parsing and translation.
        transform.addinfo(change={'status':MERGED},where={'status':FILEIN,'idroute':routedict['idroute']})
