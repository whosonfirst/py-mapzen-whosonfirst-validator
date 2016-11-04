#!/usr/bin/env python

# Remove .egg-info directory if it exists, to avoid dependency problems with
# partially-installed packages (20160119/dphiffer)

import os, sys
from shutil import rmtree

cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
egg_info = cwd + "/mapzen.whosonfirst.validator.egg-info"
if os.path.exists(egg_info):
    rmtree(egg_info)

from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read()
version = open("VERSION").read()

setup(
    name='mapzen.whosonfirst.validator',
    namespace_packages=['mapzen', 'mapzen.whosonfirst'],
    version=version,
    description='Tools for validating Who\'s On First documents',
    author='Mapzen',
    url='https://github.com/whosonfirst/py-mapzen-whosonfirst-validator',
    install_requires=[
        'mapzen.whosonfirst.export>=0.71',
        'mapzen.whosonfirst.placetypes>=0.11',
        'mapzen.whosonfirst.sources>=0.03',
        'mapzen.whosonfirst.utils>=0.18',
        'geojson'
        ],
    dependency_links=[
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-export/tarball/master#egg=mapzen.whosonfirst.export-0.71',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-placetypes/tarball/master#egg=mapzen.whosonfirst.placetypes-0.11',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-sources/tarball/master#egg=mapzen.whosonfirst.sources-0.03',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-utils/tarball/master#egg=mapzen.whosonfirst.utils-0.18'
        ],
    packages=packages,
    scripts=[
        'scripts/wof-validator',
        ],
    download_url='https://github.com/whosonfirst/py-mapzen-whosonfirst-validator/releases/tag/' + version,
    license='BSD')
