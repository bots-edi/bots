Mapping Scripts
===============

.. epigraph::
    Definition: Instructions to get data from incoming edi-message and put it in the outgoing edi-message

* Mapping scripts are python programs. 
* Mapping script are in: ``usersys/mappings/editype/mapping-script-name.py``.
* Within a mapping script function ``main()`` is called.
* Some important things to be noted about mapping scripts:
    * All data in the incoming/outgoing messages are strings.
    * Errors in a mapping script are caught by Bots and displayed in bots-monitor.
    * You can Raise an exception in your mapping script if you encounter an error situation.
    * (Bots>=3.0) if an error is raised in a script, other translations for message in same edi-file will continue.
    * (Bots>=3.0) when an error situation is met in script: you can send specific error-email to responsible people.

**Index**

.. toctree::
    :maxdepth: 2

    how-it-works
    get-from-msg
    put-in-msg
    mapping-functions
    code-conversion
    calculate-count
    persist
    eanupc-check
    change-delete
