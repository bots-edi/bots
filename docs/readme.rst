Bots-Edi
========

.. image:: https://badges.gitter.im/Join Chat.svg
   :alt: Join the chat at https://gitter.im/bots-edi/Lobby
   :target: https://gitter.im/bots-edi/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://readthedocs.org/projects/bots/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://bots-edi.github.io/bots/

.. image:: https://landscape.io/github/bots-edi/bots/master/landscape.svg?style=flat
   :target: https://landscape.io/github/bots-edi/bots/master
   :alt: Code Health

.. image:: https://img.shields.io/pypi/v/bots.svg
   :target: https://pypi.python.org/pypi/bots
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/bots.svg
   :target: https://pypi.python.org/pypi/bots
   :alt: Development Status

.. image:: https://img.shields.io/pypi/pyversions/bots.svg
   :target: https://pypi.python.org/pypi/bots
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/l/bots.svg
   :target: https://raw.githubusercontent.com/bots-edi/bots/master/license.rst
   :alt: License






Bots is complete software for EDI (Electronic Data Interchange)
Bots-Edi is a free, open-source EDI translator. It has the following features:

::

    - Supports all major EDI data formats: EDIFACT, x12, Tradacoms, XML.
    - Runs on Windows, Linux, OSX and Unix.
    - Bots is very stable.
    - Bots handles high volumes of EDI transactions.
    - Bots is very flexible and can be configurated for your specific EDI needs.

This is a fork of Bots, which was created by `Henk-Jan
Ebbers`_. This fork was
created in an effort to build a more collaborative community around this
project.

Quick Start
-----------

.. code-block:: bash

    $ git clone https://github.com/git-albertomarin/bots
    $ cd bots
    $ python3 -m venv .venv; source .venv/bin/activate
    $ pip install .
    $ python postinstallation.py --install
    $ bots-webserver.py


Getting Started
---------------

The documentation_ is a great place to get
started.

License
-------

Bots is licenced under GNU GENERAL PUBLIC LICENSE Version 3; for full
text: http://www.gnu.org/copyleft/gpl.html

.. _Henk-Jan Ebbers: http://bots.sourceforge.net/en/index.shtml
.. _documentation: https://bots-edi.github.io/bots
