Standard Communications
=======================
Bots supports a set of communication protocols out of the box such that you only need to configure it in ``bots-monitor->Configuration->Channels`` to get it working.
The set of supported protocols are listed below:

.. csv-table:: Supported Communication Types
    :header: "Protocol", "Description"
    :widths: 10, 30

    "file", "Use this to push/pull files with the filesystem, also works with shared file systems."
    "smtp", "Use this to send an email to your trading partner with the EDI file."
    "smtps", "Same as smtp but additionally uses SSL for secure transmission"
    "smtpstarttls", "Same as smtp but additionally uses TLS for secure transmission"
    "pop3", "Use this to extract emails with EDI files from your email inbox."
    "pop3s", "Same as pop3 but additionally uses SSL for secure transmission"
    "pop3sapop", "Same as pop3 but additionally encrypts your password during authentication"
    "http", "Use the HTTP protocol to GET or PUT files with your trading partner."
    "https", "Same as http but additionally uses SSL for secure transmission."
    "imap4", "Use this to extract emails with EDI files from your email inbox."
    "imap4s", "Same as imap4 but additionally uses SSL for secure transmission"
    "ftp", "Use the FTP protocol to exchange files with your trading partner."
    "ftps (explicit)", "Same as ftp but additionally uses explicit SSL for secure transmission"
    "ftps (Implicit)", "Same as ftp but additionally uses implicit SSL for secure transmission"
    "sftp (ssh)", "Use the SFTP protocol for exchange files with your trading partner."
    "xmlrpc", "Use the XMLRPC protocol for exchange files with your trading partner."
    "trash/discard", "Use this to discard uneeded messages types from your trading partner."
    "communicationscript", "Use this for custom comms, as described :doc:`here <channel-scripting>`"
    "db", "Use this for database comms, as described :doc:`here <database>`"
