Migrate Django versions
=======================

Migrate Django to version 1.3 or greater:

* `Remove <https://docs.djangoproject.com/en/1.3/topics/install/#remove-any-old-versions-of-django>`_ the 1.1 version of Django
* `Download <https://www.djangoproject.com/download/>`_ new version.
    * Mind: bots 2.2.0 does not support Django 1.4.*.
    * Django version 1.3.1 is tested and recommended.
* `Install <https://docs.djangoproject.com/en/1.3/topics/install/#install-the-django-code>`_ the new version
* :doc:`Restart <../get-bots-running>` the bots webserver
* Be sure to use the correct bots upgrade plugin to match the version of Django you have installed.
* Bots includes copies of some Django files in it's directory structure. You may need to refresh these from your current Django version if you notice any admin interface "bugs". (eg. selection checkboxes not working correctly).
    * Copy from: ``<python dir>\Lib\site-packages\django\contrib\admin\media``
    * Copy to: ``<python dir>\Lib\site-packages\bots\media``
    * Include sub-directories: css, img, js
