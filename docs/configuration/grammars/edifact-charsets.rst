EDIFACT Character-Sets 
======================

Edifact uses its own naming of character-sets such as UNOA, UNOB, etc..
And some character-sets are quite typical or old.

Bots has 2 ways of supporting these edifact character-sets:

#. via specific character-sets UNOA and UNOB in ``bots/usersys/charsets``
#. in bots.ini aliases are giving for edifact character-sets, eg: UNOC=latin1=iso8859-1

There are some problems with character-sets UNOA and UNOB:

* This is not always handle correct by some, eg they send UNOA with lower-case characters.
* In practice often <CR/LF> is send; officially these are not in UNOA or UNOB.

A default bots installation includes by default the UNOA and UNOB character set. These are not strict interpreted, but **tuned to reality**, so that they will not often lead to problems.

In the download **charsetvariations** on `sourceforge site <http://sourceforge.net/projects/bots/files/grammars/edifact%20grammars/>`_ are some variations on these character-sets (stricter, less strict). Read the comments in these files first.
