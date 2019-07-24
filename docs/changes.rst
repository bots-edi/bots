Changelog
=========


3.3.1 (unreleased)
------------------

- Restore jobqueueserver. It was broken in 3.3.0 because of unfinished
  python2/3-support. Fixes https://github.com/bots-edi/bots/issues/21.
  [WouterVH]

- Remove ``bots_importlib``. Python2.6 is no longer supported.
  Cfr. https://github.com/bots-edi/bots/issues/23
  [WouterVH]

- Remove ``bots_ordereddict``. Python2.6 is no longer supported.
  Cfr. https://github.com/bots-edi/bots/issues/22
  [WouterVH]

- Add new dependency on ``future`` to help with python3-compatibility.
  For more information, please see https://pypi.python.org/pypi/future/.
  [WouterVH]

- Add rst-version of GPL3-license.
  Thanks to https://github.com/shibukawa/rest-licenses/
  [WouterVH]

- Add dependencies in ``setup.py``.
  [WouterVH]

- Update ``MANIFEST.in``.
  [WouterVH]

- Add explicit ``UTF-8``-file-encoding to each python-file.
  Cfr. https://www.python.org/dev/peps/pep-0263/
  [WouterVH]

- Add ``etc/requirements.txt``
  [WouterVH]

- Add ``.landscape.yml`` to configure code-quality checks at
  https://landscape.io/github/bots-edi/bots
  [WouterVH]

- Add ``setup.cfg`` with config-settings for several tools.
  Also set ``bdist_wheel`` to ``universal``.
  [WouterVH]

- Move bots-code to ``src``-sub-directory. Why? Please see
  https://blog.ionelmc.ro/2014/05/25/python-packaging/
  [WouterVH]

- Move unittests to ``tests``-subdirectory.
  [WouterVH]

- Move scripts to ``scripts``-subdirectory.
  [WouterVH]


3.3.0 (2016-11-23)
------------------

- Add ``License.rst``
  [WouterVH - 22-11-2016]

- Update Readme, and .gitignore
  [JCapriotti - 19-11-2016]

- add setup.py using setuptools
  [WouterVH - 09-08-2016]

- add .gitignore-file
  [WouterVH - 09-08-2016]

- Revert ``Added gitignore and sphinx docs``
  [eppye - 08-03-2016]

- Revert ``Added gitignore and sphinx docs``
  [eppye - 08-03-2016]

- Merge pull request #367 from abhishek-ram/sphinx-docs
  Added gitignore and sphinx docs
  [eppye - 07-03-2016]

- Added gitignore and sphinx docs
  [ Abhishek Ram - 31-10-2015]

- last chagnes?
  [eppye - 15-08-2015]

- small change in text for 'ftp account'
  [eppye - 04-08-2015]

- Issue 362: add: more preprocessing
  [eppye - 21-05-2015]

- type in internal function name: save_int instead of safe_int
  [eppye - 21-05-2015]

- Issue 253: migrate to python 3.*
  python3 uses another pickle protocol by default.
  [eppye - 20-05-2015]

- change in comments
  [eppye - 20-05-2015]

- added some unittests.
  [eppye - 20-05-2015]

- small change i order to get unittests right: transform.getcodeset gets a list from ccodes.
  postgreSQL returns this in 'reversed' order.
  not an error, but use same orders as MySQL and SQLite
  [eppye - 20-05-2015]

- Issue 254: for persist: timestamp on update
  [eppye - 20-05-2015]

- Issue 359:  Add option for daily engine.log
  [eppye - 20-05-2015]

- Issue 341: Optionally add ``run cleanup`` to run menu. Allow cleanup run from commandline in acceptance testing.
  (missed some code at first try)
  [eppye - 20-05-2015]

- Issue 338: Error when incoming email with subject > 35 chars and db is not SQLite
  [eppye - 20-05-2015]

- Issue 347: bots_communication_failure counters: domein too long for db field
  [eppye - 20-05-2015]

- Issue 358: cleanup.py should not log ``vacuum database`` for non-sqlite installations
  [eppye - 20-05-2015]

- Issue 363: add: function to split up text (or lists)
  [eppye - 20-05-2015]

- change in comments
  [eppye - 20-05-2015]

- Issue 360: mapping is the centre of bots,
  set email-addresses from mapping
  [eppye - 19-05-2015]

- Issue 355: add: easier access to all envelope fields in mapping
  changed this again: envelope fields are in inn.envelope: a list of dicts: [mpath,mpath,etc]
  [eppye - 19-05-2015]

- Issue 360: mapping is the centre of bots
  - outcommented mysterious assignged to topartners in transform.py/_translate_one_file ; it does not do anything.
  - changes in comments
  [eppye - 16-05-2015]

- change in comments
  [eppye - 16-05-2015]

- Issue 328: pass frommail and tomail to mapping
  during testing found: tomail was not passed if there was no check on the toaddress.
  changed this, tomail is now always passed.
  [eppye - 15-05-2015]

- Issue 356: set all envelope fields from mapping
  - more data is passed for merging - so more data will get passed from maping script
  - more comments
  - fixed soem inconsistenties in enveloping
  [eppye - 13-05-2015]

- small code change for use in acceptance tests: get a frozen value for datetime objects.
  (needed this in some mappig scripts).
  [eppye - 12-05-2015]

- change in comments
  [eppye - 12-05-2015]

- Issue 355: add: easier access to all envelope fields in mapping envelope fields are in:
  inn.envelope (a dict), not in ta_info anymore.
  [eppye - 11-05-2015]

- small code change for use in acceptance tests: get a frozen value for datetime objects.
  (needed this in some mappig scripts).
  [eppye - 25-04-2015]

- Issue 355: add: easier access to all envelope fields in mapping
  [eppye - 23-04-2015]

- Improve & bug fix for Issue 353: add: function to 'strip diacritics'
  - one function (instead of 2)
  - can handled other charsets (not only ascii and latin1/iso-8859-1)
  - one char -> one char or nothing - but not eg 2 chars; better because fields lenghts should not get 'suddenly' bigger in edi
  [eppye - 22-04-2015]

- Issue 357: Add: pass to mapping number of messages and sequence number in file/interchange
  [eppye - 22-04-2015]

- Issue 354: better handling of partners in x12 (edifact)
  pick up combination of ISA-ID/ISA-qual/GS-ID.
  improved coding of enhancedget.
  [eppye - 17-04-2015]

- Issue 353: add: function to 'strip diacritics'
  [eppye - 16-04-2015]

- Issue 349: In translations, grammars not required for db or raw types, so do not show error icon
  [eppye - 15-04-2015]

- Issue 253: migrate to python 3.*
  roll back: callable() is available in python >= 3.2
  [eppye - 11-04-2015]

- small code/errors improvement:
  - different warning for missing frompartner and topartner
  - checking in subroutine: same for x12, edifact etc.
  [eppye - 11-04-2015]

- Issue 352: new: very strict checking on whitespace 'between' records
  [eppye - 11-04-2015]

- Issue 351: add: sanity checks on separators (edifact/x12)
  [eppye - 10-04-2015]

- Issue 348: set/change headers via user scripting
  [eppye - 09-04-2015]

- max integer was not tested correctly.
  limit here is the database: int is 2^31 -1
  to change that, have to change database -> next database migration
  [eppye - 09-04-2015]

- Issue 337: Add bots_environment_text in page title
  [eppye - 07-04-2015]

- Issue 340: Admin views minor changes for better usability
  [eppye - 07-04-2015]

- Issue 341: Optionally add ``run cleanup`` to run menu. Allow cleanup run from commandline in acceptance testing.
  [eppye - 06-04-2015]

- Issue 346: added option: when arything goes wrong in translation, skip whole file /no output
  [eppye - 03-04-2015]

- change in comments
  [eppye - 03-04-2015]

- Issue 345: remove in communication.py option to userscript keyfile, certfile
  [eppye - 03-04-2015]

- Issue 342: Add logfile viewer in GUI
  [eppye - 03-04-2015]

- change in comments.
  [eppye - 03-04-2015]

- restructured code for fixed files with noBOTSID
  [eppye - 02-04-2015]

- Issue 344: bug when re-using structures (in grammar)
  Other things for grammars/grammarreading:
  - more consistent fucntion calls (no more defaults)
  - much more comments in grammar.py
  - code is better structured.
  - soem extra checks were not performed bacause of typo
  [eppye - 02-04-2015]

- Issue 253: migrate to python 3.*
  in unittests: same conversion 'trics' as in source code
  [eppye - 02-04-2015]

- Issue 253: migrate to python 3.*
  [eppye - 01-04-2015]

- get grammar/grammar reading clearer:
  - changes in comments
  - no more defaults in grammar read functions - that only obscures things.
  [eppye - 31-03-2015]

- small change in coding: read/write pickled files via botslib.
  [eppye - 30-03-2015]

- change in comments.
  [eppye - 30-03-2015]

- Issue 334: better errors for numeric fields with exponentials
  [eppye - 30-03-2015]

- Issue 333: bug: charsets of incoming emails
  [eppye - 30-03-2015]

- minor change/improvement in logic of file->email mime.
  [eppye - 30-03-2015]

- Issue 332:  in node.change: convert eg int to string (like in put())
  [eppye - 30-03-2015]

- Issue 331: changed 'out_as_inn' implementation (same functionality)
  also other changes; see change for  Issue 253:  migrate to python 3.*
  [eppye - 30-03-2015]

- Issue 330: removed 'persistfilter' in GUI
  [eppye - 30-03-2015]

- Issue 329: filtering incoming email: add 'multipart/related' to whitelist_multipart
  [eppye - 30-03-2015]

- Issue 328: pass frommail and tomail to mapping
  [eppye - 30-03-2015]

- Issue 327: add more parameters to user exits for 997/CONTRL
  [eppye - 30-03-2015]

- Issue 326: edifact/UNA segment: if repetition seperator is space, assume they make a mistake
  plus: typo: seperator -> separator
  [eppye - 29-03-2015]

- Issue 325: fix bug in grammar read logic
  [eppye - 28-03-2015]

- Issue 324: other way of indicating unique part in filename
  [eppye - 28-03-2015]

- Issue 318:  mimefile msgid may exceed 70 chars (too big for database)
  [eppye - 28-03-2015]

- Issue 323: rollback Issue 314
  [eppye - 26-03-2015]

- Issue 253: migrate to python 3.*
  [eppye - 26-03-2015]

- Issue 319: better xml-generating
  [eppye - 26-03-2015]

- Issue 320: better json generating - sorted!
  [eppye - 26-03-2015]

- Issue 321: improve outgoing formatting fields
  [eppye - 26-03-2015]

- bug in bots 3.2.0. not serious/no harm.
  [eppye - 10-09-2014]

- bug in 2.3.0. Not very serious.
  [eppye - 10-09-2014]

- 2 bugs in bots 3.2.0 (reported by ludovic)
  [eppye - 10-09-2014]

- changes in comments
  [eppye - 10-09-2014]

- update windows build batchfiles.
  [eppye - 04-09-2014]

- correct version
  [eppye - 03-09-2014]

- ready for release 3.2.0
  [eppye - 01-09-2014]


3.2.0 (2014-09-02)
------------------

- TODO


3.2.0rc2 (2014-05-27)
---------------------

- TODO


3.2.0rc (2013-05-27)
--------------------

- TODO
