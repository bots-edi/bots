Bots Documentation
==================

The documentation is written in reStructuredText format. Sphinx is used
to generate the HTML documentation site.

Building the Docs
-----------------

Requirements
~~~~~~~~~~~~

-  Python
-  Pip packages:

   -  sphinx
   -  sphinx\_rtd\_theme

Building
~~~~~~~~

1. Clone the repository ``git clone git@github.com:bots-edi/docs.git``
2. Run ``make html``

Publishing
~~~~~~~~~~

The documentation site uses GitHub Pages, specifically the
https://github.com/bots-edi/bots-edi.github.io repository.

1. Clone the repository
   ``git clone git@github.com:bots-edi/bots-edi.github.io.git``
2. Build the documentation (see above)
3. Copy the contents of the \_build/html folder to the
   ``bots-edi.github.io`` repository.
4. Commit

Credits
=======

This work was started by @abhishek-ram at
https://github.com/abhishek-ram/bots/tree/sphinx-docs/docs and @skilchen
at https://github.com/skilchen/bots/tree/master/docs
