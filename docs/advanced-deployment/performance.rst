Performance
===========

* Most edi files are just a few kilobyes. An edi file of 5Mb is very large (edifact, x12). If you encounter larger ones: please let me know.
* AFAIK there are no issues with performance. If you run into this: please inform me eg via mailing list.


**Get More Performance**

* (Bots >= 2.2.0) `Cdecimals (Extern library) <http://www.bytereef.org/mpdecimal/index.html>`_ speeds up bots. This library will be included in python 3.3, but can be installed in earlier python versions.
* (bots >= 3.1) Do not use ``get_checklevel=2`` in ``config/bots.ini``. This does extended checking of mpath's, use this during development only.
* (bots >= 3.0) Schedule bots-engine via the job queue server.
* For xml: check if the c-version of python's elementtree is installed and used.
* Enough memory is important for performance: disk-memory swapping is slow! Actual memory usage depends on size of edi-files.
* Check mappings for slow/inefficient algorithms.
* Bots works with `pypy <www.pypy.org>`_, see below on this page.
* Use SSD for faster reading/writing. In ``config/bots.ini`` the ``botssys-directory`` can be set, in ``config/settings.py`` the place of the SQLite-database.

**Strategy for bigger edi volumes**

* Best strategy is to `schedule <../deployment/run-botsengine.html#scheduling-bots-engine>`_ bots-engine more often.
* (bots >= 3.0) Schedule bots-engine via the `job queue server <../deployment/run-botsengine.html#job-queue-server-bots-3-0>`_.
* Routes can be `scheduled independently <../deployment/run-botsengine.html#scheduling-bots-engine>`_.
* Set-up good scheduling, keeping volumes in mind.
* EDI in the real world has often large peaks.
* Dome edi transactions are time critical (eg orders), others not so much (eg invoices)
* Check where the large volumes are (size and number of edi-transactions)
* Look at the sending pattern of your customers. Often edi is send in night jobs, so you might receive lot of volume early in the morning.
* Check where you send large volumes. Send this at a time that does not interfere with other flows.
* Incoming volumes can be limited per run. This way the time bots-engine runs is predictable. 
    * The max time a channel fetches incoming files is a parameter for each channel. 
    * This is dependent upon the communication type used; eg file system I/O is much faster than SFTP. 
    * Files "left behind" will be fetched on subsequent runs.
* (Bots >= 3.0) Limit for max file-size (set in bots.ini). If an incoming file is larger, bots will give error. This is to prevent **accidents**.

**Performance/throughput testing**

#. Tests are done using file system I/O (no testing of communication performance).
#. Tests done in one run of bots-engine.
#. Test system: Intel Q9400 2.66GHz; 4Gb memory; ubuntu 10.04(lucid); python 2.7; default SQLite database.
#. Please note that these tests are **artificial**: if you have such high volumes and big files look at good scheduling!
#. Tests are with edifact; x12 performance is the same.

.. csv-table::
    :header: Description,File Count,Total Size,Message Count,Time(bots2.0),Speed(bots2.0),Time(bots2.2),Speed(bots2.2),Time(bots3.2),Speed(bots3.2)

    01 edifact2fixed,32,305Mb,32,1:01:39,82 kb/s,0:50:57,100 kb/s,0:44:01,115 kb/s
    02 edifact2fixed,116,300Mb,116,1:14:18,68 kb/s,0:36:20,137 kb/s,0:37:25,133 kb/s
    03 edifact2fixed,94048,295Mb,141072,0:47:21,104 kb/s,0:39:54,125 kb/s,0:42:30,115 kb/s
    04 fixed2edifact,14244,300Mb,78342,1:04:11,78 kb/s,0:33:21,150 kb/s,0:32:40,153 kb/s
    05 xml2edifact,17424,300Mb,17424,0:41:24,121 kb/s,0:35:48,139 kb/s,0:35:20,141 kb/s
    06 edifact2xml(1to1),14609,300Mb,74919,1:23:03,60 kb/s,0:58:19,85 kb/s,0:44:38,112 kb/s

**Conclusions of performance measurements:**

#. Memory usage is stable (no leakage).
#. Memory usage is directly related to the size of the edi-files. In test 01 (edifact files of 9.5Mb) bots-engine uses 1.5Gb memory.
#. Tested with edifact files of 120Mb; memory usage is stable at 4.5Gb.
#. Performance is reasonably independent from the size of edi-files/messages.
#. An edifact file of 9.5Mb takes about 85sec to be processed.
#. For outgoing edi files: writing to one file or multiple file does not significantly affect performance.

**Testing with pypy**

`pypy <www.pypy.org>`_ s a python implementation that is faster by using a JIT (that is one of their achievements).
Results of the first tests with pypy (beta-versions of pypy 2.0):

* Bots works with pypy.
* Comparing some stress tests: much faster, 2-3 times faster.
* Did not run all test-sets. Probably I will do that with definitive version of pypy 2.0 and/or release of bots 3.1.
* Problem might be that not all libraries/dependencies work with pypy.
    * SQLite3 database connector: OK
    * MySQL database connector: version 1.2.5 does. Note that bots 3.1.0 gave am error with this version, a patch was easy.
    * paramiko (for SFTP/SSH): no, dependency pycrypto is not supported.

This looks like a very interesting development!
