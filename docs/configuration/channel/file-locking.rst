Safe File Writing/Locking
=========================

**The Problem**

* ERP writes an in-house file; bots starts to read this before the file is completely written.
* Bots writes file over FTP, but file is read before Bots finishes writing.

**The Solution**

#. Tmp-part file name: bots writes a filename, than renames the file.

   | Example 1. In channel: filename is ``myfilename_*.edi.tmp``, tmp-part is ``.tmp``
   | Bots writes: ``myfilename_12345.edi.tmp``
   | Bots renames: ``myfilename_12345.edi``

#. System lock: use system file locks for reading or writing edi files (windows, \*nix).
#. Lock-file: Directory locking: if lock-file exists in directory, directory is locked for reading/writing. Both reader and writer should check for this.

