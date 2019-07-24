Handling errors in Production
=============================

Different errors:

#. Errors in edi files:
    * inbound: contact your edi-partner they should send valid messages. (yes, and sometimes you will just have to adapt the definitions of the standards).
    * outbound: check out why your ERP-system sends invalid messages. Adapt the export-module.
#. Communication errors
    * inbound: no problem, next run bots will try again to fetch the messages correctly. No action needed (but if it keeps happinging....).
    * outbound. You can handle this manually or automated:
        * manually:
            #. in the outgoing view, select edi-files with failed outbound communication and mark these as 'resend'
            #. do: 'Run user-indicated resends'
            #. check if communication was OK this time.
            #. Note: number of resends is indicated in the outgoing view.
        * automatic:
            #. schedule bots-engine with option ``--automaticretrycommunication``.
            #. all edi-files for which out-communication failed will be resend automatically.
            #. if communication fails (again) in the automatic retry this is indicated in the error notification. So probably it is best to react on this.
            #. Note: number of resends is indicated in the outgoing view.
            #. The first time you use ``automaticretrycommunication`` nothing is resend, but automaticretry is initialised: all failed communications from that moment on will be resend. This is to prevent having all older failed communications resend.
            #. Scheduling: often bots is scheduled to run eg every 10 minutes, and automaticretry once an hour. For this type of scheduling use the `jobqueue server <run-botsengine.html#job-queue-server-bots-3-0>`_.
