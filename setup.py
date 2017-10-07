#!/usr/bin/env python

from setuptools import setup

setup(
    name="pymultiwallet",
    version="0.1.0",
    packages = [
    ],
    author="Dev Random",
    entry_points = { 'console_scripts':
            [
                'mw = mw:main',
            ]
        },
    author_email="info@gitian.org",
    url="https://github.com/devrandom/pymultiwallet",
    license="http://opensource.org/licenses/MIT",
    description="BIP-44 multi-coin wallet tool",
    test_suite='tests',
    install_requires=[
        'pycoin',
        'mnemonic'
        ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],)
