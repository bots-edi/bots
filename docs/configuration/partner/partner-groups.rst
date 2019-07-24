Partner Groups
==============

EDI partners can be assigned to groups. This might come in handy:

* Partner dependent translations (in ``bots-monitor->Configuration->Translations``). Select a group here, and translation is done for all members of the group.
* Partner based filtering for routes/outchannel (in ``bots-monitor->Configuration->Routes``): the outchannel is used for all members of the group.
* In selections you can use partner-groups.

.. note::
    partner-groups do not work for confirmations.

**How to**

#. Create a group in ``bots-monitor->Configuration->Partners & groups``. Indicate it is a group using tick-box **Isgroup**.
#. For the partners in a group, assign them to this group using **Is in groups**.

**Plugin**

Plugin 'demo_partnerdependent' at the `bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_ demonstrates partner-groups.
