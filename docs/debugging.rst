Debugging
=========

Standard method using the bots-monitor
--------------------------------------

* The reports-screen gives an overview of what happened in a run.
* If there are process errors in a run, first view the process errors!
* The incoming-screen gives information about the results of each incoming file
* For each incoming edi-file: view the detail-screen for information about the 
  processing steps for incoming/outgoing edi file (in incoming-screen move your 
  mouse to the star at the start of the line, a drop-down box will appear, choose ``details``.
* View the outgoing files, including communication errors for outgoing files.

Extended Debug options
----------------------

* In config/bots.ini there is the parameter **get_checklevel**. Set to to 2 for developing. 
  Then all gets/puts are checked with the grammar(s).
  For production use 1 (does sanity checks on get/puts) or 0  (which is fastest, but if errors gives probably 
  strange error-messages).

* If wished, use extended errors: parameter **debug** in :doc:`bots.ini<overview/configuration-files>` 
  gives information about the place in the code where the error occurred.

* logging. Logging can be found in botssys/logging. Parameters in :doc:`bots.ini<overview/configuration-files>` 
  can be set to get more debug information:

    * **log_file_level**: set to DEBUG to get extended information.
    * **readrecorddebug**: information about the records that are read and their content.
    * **mappingdebug**: information about the results of get()/put() in the mapping script. 

      .. note::
        In bots 3.0.0 this does not work (bug). Fix: in botsinit.py, line 188 should be: ``botsglobal.logmap = logging.getLogger('engine.map')``

* Extended log information for some communication protocols in :doc:`bots.ini<overview/configuration-files>` 
  ftpdebug, smtpdebug, pop3debug. This debug-information is on the console/command line.

* Within a mapping script (or other user script) use 'print', output can be viewed on the console/command line.

* Use root.display() to see message content in mapping script:  

    * incoming messages: at the start of the main function ``inn.root.display()``
    * outgoing messages: at the end of the main function: ``out.root.display()``

 root.display() is not the nicest output, but is definitely what you receive/have generated.

.. note::
    The errors bots gives for incoming edi-files are quite accurate ;-))

Tips for debugging
------------------

* If a run has process errors, first check the process errors!
* Be careful with character-set/encoding:  

    * Can your editor handle this? Be careful with editing files and saving these again, 
      you might run into issues with character-set/encodings!
    * Are you familiar with the character-set you use? Are you familiar with eg utf-8? 
      If not, please check this first.

* In reality, edifact and x12 messages contains errors. Especially when **found on internet**; 
  lot of ISA headers for X12 are not OK!
