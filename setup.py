#!/usr/bin/env python

from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read(),

setup(
    name='mapzen.whosonfirst.validator',
    namespace_packages=['mapzen', 'mapzen.whosonfirst', 'mapzen.whosonfirst.validator'],
    version='0.01',
    description='Tools for validating Who\'s On First documents',
    author='Mapzen',
    url='https://github.com/mapzen/py-mapzen-whosonfirst-validator',
    install_requires=[
        'mapzen.whosonfirst.utils',
        'mapzen.whosonfirst.export',
        'mapzen.whosonfirst.placetypes',
        'geojson',
        ],
    dependency_links=[
        ],
    packages=packages,
    scripts=[
        # 'scripts/wof-validate',
        ],
    download_url='https://github.com/mapzen/py-mapzen-whosonfirst-validator/releases/tag/v0.01',
    license='BSD')
