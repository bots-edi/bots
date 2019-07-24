# -*- coding: utf-8 -*-

import os
import sys
from distutils.core import setup


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == "":
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != "":
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk("bots"):
    # Ignore dirnames that start with '.'
    # ~ for i, dirname in enumerate(dirnames):
    # ~ if dirname.startswith('.'): del dirnames[i]
    if "__init__.py" in filenames:
        packages.append(".".join(fullsplit(dirpath)))
        data_files.append(
            [
                dirpath,
                [os.path.join(dirpath, f) for f in filenames if not f.endswith(".pyc")],
            ]
        )
    elif filenames:
        data_files.append(
            [
                dirpath,
                [os.path.join(dirpath, f) for f in filenames if not f.endswith(".pyc")],
            ]
        )

# ~ # Small hack for working with bdist_wininst.
# ~ # See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
# ~ if len(sys.argv) > 1 and 'bdist_wininst' in sys.argv[1:]:
if len(sys.argv) > 1 and "bdist_wininst" in sys.argv[1:]:
    for file_info in data_files:
        file_info[0] = "\\PURELIB\\%s" % file_info[0]


setup(
    name="bots",
    version="3.2.0",
    author="hjebbers",
    author_email="hjebbers@gmail.com",
    url="http://bots.sourceforge.net/",
    description="Bots open source edi translator",
    long_description="Bots is complete software for edi (Electronic Data Interchange): translate and communicate. All major edi data formats are supported: edifact, x12, tradacoms, xml",
    platforms="OS Independent (Written in an interpreted language)",
    license="GNU General Public License (GPL)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial",
        "Topic :: Other/Nonlisted Topic",
        "Topic :: Communications",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    scripts=[
        "bots-webserver.py",
        "bots-engine.py",
        "bots-grammarcheck.py",
        "bots-xml2botsgrammar.py",
        "bots-updatedb.py",
        "bots-dirmonitor.py",
        "bots-jobqueueserver.py",
        "bots-plugoutindex.py",
        "bots-job2queue.py",
        "postinstallation.py",
    ],
    packages=packages,
    data_files=data_files,
)
