How to do configuration
=======================

**How do I make an edi configuration?**

#. Use :doc:`plugins <../plugins/index>`. This is a quick and easy way to install predefined configurations of bots.
    * Downloads: `bots sourceforge site <http://sourceforge.net/projects/bots/files/plugins/>`_
    * Description of plugins: :doc:`on this wiki page <../plugins/plugins-sourceforge>`
    * Plugins can be shared by users and communities. Send your plugin!
#. Use a plugin *close* to what you want, and adapt.
#. Do your own configuration:
    * Take a look at the :doc:`tutorial <../quick-start-guide/index>`.
    * Use bots-monitor for configuration of routes, channels, translations and partners.
    * There are grammars for all edifact and x12 messages `on the bots sourceforge site <http://sourceforge.net/projects/bots/files/grammars/>`_.
    * Grammars and mapping require knowledge of edi and edi-standards and some python knowledge. (python is a relatively easy programming, no deep knowledge of python is needed).
    * Use command line tool ``bots-xml2botsgrammar.py`` to generate a grammar from an xml file.
    * Check a grammar using the command line tool ``bots-grammar.py``.
#. A step by step description (next section) of making a configuration.
#. If you are doing your own configuration check out how to :doc:`debug <../debugging>`
#. Hire us (`EbbersConsult <http://www.ebbersconsult.com/>`_ - the makers of Bots) to help you with configuring bots: we are the edi experts.

DIY step by step
----------------

This is how I start with a new route and translation...

* Create some :doc:`channels <channel/index>` (eg. test_in and test_out).   
    * These are just "file" channels that read from botssys\infile\(some-dir) and write to botssys\outfile\(some-dir). 
    * You should have some sample input documents from your partner, put one or a few of these in the infile location. 
    * Make sure the test channel is NOT set to delete them.
* Get (or create) the incoming :doc:`grammar <grammars/index>`. 
    * If incoming is edifact or X12 then this part is already done for you, download the grammars from the bots website. 
    * For XML there is a conversion tool to make a start. 
    * For fixed/csv etc. you need to do it yourself, it is best to start with one of the plugin examples. 
    * Creating a fully working correct grammar can be the most difficult part of setting up bots, but is a once-off task. 
    * From then on that edi type can be used in any route.
* Configure a :doc:`route <route/index>` to get files from your inchannel and specify the editype and messagetype corresponding to your grammar. 
    * You can use the same editype for outgoing too for now. 
    * Don't worry about translation yet, just run bots engine, check errors, and keep adjusting your grammar and testing iteratively until the file is "received" ok. 
    * It will then be "stuck" because there's no translation. 
    * If you get syntax errors when using a downloaded grammar, most likely the input file actually contains errors! Contact your partner about this, or correct them by editing the file and continue testing.
* As you did for incoming, create your outgoing grammar and configure it in the route. If you are creating your own grammars try at first to keep them simple with no mandatory segments etc. This can be added later.
* Configure a :doc:`translation <translation/index>` and create a :doc:`mapping script <mapping-scripts/index>`. 
    * Start with mapping just the bare minimum mapping one or two fields (eg. order number) and again iteratively modify and test until you have some output.
    * if your output grammar is edifact or X12 for example, you'll need to at least map the mandatory segments to create a valid document.
* When testing a mapping, it's very useful to insert print statements to help with :doc:`debugging <../debugging>`. The output will be seen in the webserver console window if you run bots engine from the GUI menu.

* Once you can run the route with no errors and get "something" output you'll feel that sense of achievement and can then go on to add everything else you need into the mapping and grammar, piece by piece. 
* If you have many mappings to do, create a module of common functions you create, and import into every mapping. 
* Also check out the bots built in mapping functions provided. The code conversion tables are particularly useful.
* The channels are the final part once it's all working and tested, to read and write from the actual systems involved. Create the new channels and change the route to use them.

I would say the learning curve is a little steep at first, but once started you'll be glad you did.
