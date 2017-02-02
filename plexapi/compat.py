# -*- coding: utf-8 -*-
# Python 2/3 compatability
# Always try Py3 first

try:
    string_type = basestring
except NameError:
    string_type = str

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree
    