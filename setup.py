# -*- coding: utf-8 -*-

"""A setuptools based setup module.

For more information, please see
- https://pypi.python.org/pypi/setuptools
- https://pythonhosted.org/setuptools
- https://python-packaging-user-guide.readthedocs.io/en/latest/distributing/
- https://packaging.python.org/en/latest/distributing.html
- https://github.com/pypa/sampleproject

"""
from __future__ import absolute_import, division, print_function

import io
import os
import platform
import setuptools


def read(*names, **kwargs):
    r"""Return the contents of a file.

    Default encoding is UTF-8, unless specified otherwise.

    Args:
        - names (list, required): list of strings, parts of the path.
          the path might be relative to the current file.

    Keyword Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
      String containing the content of the file.

    Examples:
        >>> read('docs/readme.rst')
            u'Overview\n--------\n...'

        >>> read('docs', 'readme.rst')
            u'Overview\n--------\n...'

    """
    fn = os.path.join(os.path.dirname(__file__), *names)
    with io.open(fn, encoding=kwargs.get('encoding', 'utf8')) as fd:
        return fd.read()


version = '3.3.1.dev0'


long_description = (
    read('docs', 'readme.rst') +
    '\n\n' +
    read('docs', 'changes.rst')
    #'\n\n' +
    #read('docs', 'contributors.rst')
    )

install_requires = [
    'Cherrypy>3.1.0',
    'click',
    'Django>=1.4.0',
    'future',
    'setuptools',
    'six',
    ]

extras_require = {
    'docs': [
        'sphinx',
        'sphinx_rtd_theme',
        ],
    'tools': [
        'ecdsa',     # dep of paramiko
        'Genshi',    # for using templates/mapping to HTML)
        'paramiko',  # SFTP
        'pdfminer',  # parse pdf-files
        'pycrypto',  # SFTP
        'xlrd',      # parse excel-files
        ],
    }

# Add OS-specific dependencies
operating_system = platform.system()
if operating_system == 'Linux':
    install_requires.append('pyinotify')
elif operating_system == 'Windows':
    install_requires.append('pywin32')

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Topic :: Office/Business',
    'Topic :: Office/Business :: Financial',
    'Topic :: Other/Nonlisted Topic',
    'Topic :: Communications',
    'Environment :: Console',
    'Environment :: Web Environment',
    ]

setuptools.setup(
    name='bots',
    version=version,
    author='hjebbers',
    author_email='hjebbers@gmail.com',
    url='https://github.com/bots-edi/bots',
    description='Bots open source edi translator',
    long_description=long_description,
    platforms='OS Independent (Written in an interpreted language)',
    license='GNU General Public License (GPL)',
    keywords='edi edifact x12 tradacoms xml fixedfile csv',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    install_requires=install_requires,
    extras_require=extras_require,

    scripts=[
        'scripts/bots-webserver.py',
        'scripts/bots-engine.py',
        'scripts/bots-grammarcheck.py',
        'scripts/bots-xml2botsgrammar.py',
        'scripts/bots-updatedb.py',
        'scripts/bots-dirmonitor.py',
        'scripts/bots-jobqueueserver.py',
        'scripts/bots-plugoutindex.py',
        'scripts/bots-job2queue.py',
        ],

    entry_points={
        'console_scripts': [
            'bots-dirmonitor = bots.dirmonitor:start',
            'bots-engine = bots.engine:start',
            'bots-engine2 = bots.engine:start',
            'bots-grammarcheck = bots.grammarcheck:start',
            'bots-grammarcheckall = bots.grammarcheck:startall',
            'bots-job2queue = bots.job2queue:start',
            'bots-jobqueueserver = bots.jobqueueserver:start',
            'bots-plugoutindex = bots.plugoutindex:start',
            'bots-updatedb = bots.updatedb:start',
            'bots-webserver = bots.webserver:start',
            'bots-xml2botsgrammar = bots.xml2botsgrammar:start',
            ]
        },
    )
