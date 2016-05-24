#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Install PlexAPI
"""
import re
from distutils.core import setup
from setuptools import find_packages

# Convert markdown readme to rst
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("Warn: pypandoc not found, not converting Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


# Fetch the current version
with open('plexapi/__init__.py') as handle:
    for line in handle.readlines():
        if line.startswith('VERSION'):
            VERSION = re.findall("'([0-9\.]+?)'", line)[0]

setup(
    name='PlexAPI',
    version=VERSION,
    description='Python bindings for the Plex API.',
    author='Michael Shepanski',
    author_email='mjs7231@gmail.com',
    url='https://github.com/mjs7231/plexapi',
    packages=find_packages(),
    install_requires=['requests'],
    long_description=read_md('README.md'),
    keywords=['plex', 'api'],
)
