# -*- coding: utf-8 -*-
# flake8:noqa
"""
Python 2/3 compatability
Always try Py3 first
"""

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
