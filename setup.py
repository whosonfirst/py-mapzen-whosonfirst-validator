#!/usr/bin/env python

from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read(),

setup(
    name='mapzen.whosonfirst.validator',
    namespace_packages=['mapzen', 'mapzen.whosonfirst', 'mapzen.whosonfirst.validator'],
    version='0.05',
    description='Tools for validating Who\'s On First documents',
    author='Mapzen',
    url='https://github.com/whosonfirst/py-mapzen-whosonfirst-validator',
    install_requires=[
        'mapzen.whosonfirst.utils>=0.05',
        'mapzen.whosonfirst.export>=0.59',
        'mapzen.whosonfirst.placetypes>=0.04',
        'geojson',
        ],
    dependency_links=[
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-utils/tarball/master#egg=mapzen.whosonfirst.utils',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-export/tarball/master#egg=mapzen.whosonfirst.export',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-placetypes/tarball/master#egg=mapzen.whosonfirst.placetypes',
        ],
    packages=packages,
    scripts=[
        'scripts/wof-validator',
        ],
    download_url='https://github.com/mapzen/py-mapzen-whosonfirst-validator/releases/tag/v0.05',
    license='BSD')
