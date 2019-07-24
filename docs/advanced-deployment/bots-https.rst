Bots-Monitor over HTTPS
=======================

* This feature is introduced in bots 2.1.0.
* This works with cherrypy > 3.2.0 in combination with python 2.6 or 2.7. In python 2.5 this works (using extra dependency pyOpenssl) but gives problems with reading plugins.

**Procedure**

#. You will need an SSL certificate. You can use self-signed certificates.
#. In ``bots/config/bots.ini`` uncomment options ssl_certificate and ssl_private_key (in section webserver), and set these to the right value, eg:

    .. code-block:: ini

        ssl_certificate = /mysafeplace/mycert.pem 
        ssl_private_key = /mysafeplace/mycert.pem
        #In this example certificate and private key are in the same pem-file.
#. Restart bots-webserver
#. Point your browser to the right https-address, eg: https://localhost:8080

.. note::

    * If you are using cherrypy and receive an error "ssl_error_rx_record_too_long" try the `2-line fix <https://bitbucket.org/cherrypy/cherrypy/issue/1293/ssl-broken-under-pypy-221>`_
    * You can create self-signed certificates `here <http://www.selfsignedcertificate.com/>`_
    * You can configure port=443 in bots.ini then just point your browser to https://localhost
