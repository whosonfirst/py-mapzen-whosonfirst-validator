#!/usr/bin/env python

from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read(),

setup(
    name='mapzen.whosonfirst.validator',
    namespace_packages=['mapzen', 'mapzen.whosonfirst', 'mapzen.whosonfirst.validator'],
    version='0.10',
    description='Tools for validating Who\'s On First documents',
    author='Mapzen',
    url='https://github.com/whosonfirst/py-mapzen-whosonfirst-validator',
    install_requires=[
        'mapzen.whosonfirst.export>=0.69',
        'mapzen.whosonfirst.placetypes>=0.04',
        'mapzen.whosonfirst.sources>=0.02',
        'mapzen.whosonfirst.utils>=0.05',
        'geojson',
        ],
    dependency_links=[
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-export/tarball/master#egg=mapzen.whosonfirst.export-0.69',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-placetypes/tarball/master#egg=mapzen.whosonfirst.placetypes-0.04',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-sources/tarball/master#egg=mapzen.whosonfirst.sources-0.02',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-utils/tarball/master#egg=mapzen.whosonfirst.utils-0.06',
        ],
    packages=packages,
    scripts=[
        'scripts/wof-validator',
        ],
    download_url='https://github.com/mapzen/py-mapzen-whosonfirst-validator/releases/tag/v0.10',
    license='BSD')
