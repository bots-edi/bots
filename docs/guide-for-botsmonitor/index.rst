Guide For Bots-Monitor
======================

.. note::
    The :doc:`tutorial<../quick-start-guide/index>` contains some detailed information and screen-shots of bots-monitor!

**Menu in bots-monitor**

#. **Home: start page and general information.**
#. Last run: view results of the last run:
    * incoming: view incoming files and results
    * document: view status of business document. An edi file can contain multiple documents (eg orders). In this view are the results of the separate business documents. See :doc:`setting document views <../configuration/document-view>`
    * outgoing: view outgoing files and results
    * process errors: view process errors; mostly these will be communication errors.
#. All runs: view results of all runs:
    * reports: view of all runs and results
    * incoming: view incoming files and results
    * document: view status of business document. An edi file can contain multiple documents (eg orders). In this view are the results of the separate business documents. See :doc:`setting document views <../configuration/document-view>`
    * outgoing: view outgoing files and results
    * process errors: view process errors; mostly these will be communication errors.
    * confirmations: view the results of confirmations you wanted and confirmation you gave. See :doc:`setup confirmations <../configuration/acknowledgements>`
#. Select: use criteria like date/time to view results you want to see like eg editype edifact or x12.
    * Note: select screens can also be used using 'select' button in other views.
#. **Configuration: configuration of the edi setup.**
#. **System tasks (administrators only): read plugins, create plugins, maintain users, etc.**
#. Run: manually start a run of bots-engine:
    * Run (only new): receive, translate, and send new edi messages.
    * Run userindicated rerecieves: receive previously received edi-files again from archive. User has to mark edi-files as 're-receive' via incoming view.
    * Run userindicated resends: resend previously send edi-files again. User has to mark edi-files as 're-send' via outgoing view.

**User interface tips**

* View screens often have a star at the beginning of each line; moving over the star will show possible actions.
* In view screens, you can see the contents of an edi file if you click on the file name.
* When viewing the contents of an edi file, you can go backwards and forwards to see the processing steps of the file.
* Might be handy to use tabbed browsing.
* Bots uses user rights (viewers, administrators and superuser). See :doc:`setting user rights <../advanced-deployment/user-rights>`



**More**

.. toctree::
   :maxdepth: 2

   how-to-rereceive
