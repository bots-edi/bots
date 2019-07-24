Deployment
==========

This part of the wiki is about using bots in production.
There are extra points to consider when deploying bots in a 24x7 production environment:

#. Consider the best way of :doc:`running bots-engine <run-botsengine>`.
#. When errors in edi-files occur, receive a :doc:`notification by email <email-notifications>`.
#. :doc:`Use multiple environments <multiple-environments>`; having different environments for at least test and production is standard IT practice.
#. Consider if edi files need :doc:`extra archiving <archiving>`
#. Out of the box bots does not run as a :doc:`service/daemon <run-as-service>`. In a production enviroment this is what you'll probably want.

.. rubric::
    Index

.. toctree::
    :maxdepth: 2

    run-botsengine
    production-errors
    email-notifications
    archiving
    run-as-service
    multiple-environments
