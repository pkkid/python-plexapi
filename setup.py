#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Install PlexAPI
"""
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from plexapi import const

# Get README.rst contents
readme = open('README.rst', 'r').read()

# Get requirments
requirements = []
with open('requirements.txt') as handle:
    for line in handle.readlines():
        if not line.startswith('#'):
            package = line.strip().split('=', 1)[0]
            requirements.append(package)

setup(
    name='PlexAPI',
    version=const.__version__,
    description='Python bindings for the Plex API.',
    author='Michael Shepanski',
    author_email='michael.shepanski@gmail.com',
    url='https://github.com/pkkid/python-plexapi',
    packages=['plexapi'],
    install_requires=requirements,
    python_requires='>=3.6',
    long_description=readme,
    keywords=['plex', 'api'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ]
)
