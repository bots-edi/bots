#!/bin/sh
cp setup_tar.py setup.py
python2.7 setup.py --quiet sdist
rm setup.py


