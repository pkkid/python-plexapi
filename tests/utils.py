# -*- coding: utf-8 -*-
"""
Test Library Functions
"""
import datetime, sys
from plexapi.client import PlexClient
from plexapi.exceptions import NotFound

REGISTERED = []
COLORS = {'blue':'\033[94m', 'green':'\033[92m', 'red':'\033[91m', 'yellow':'\033[93m', 'end':'\033[0m'}


def register():
    def wrapper(func):
        name = '%s/%s' % (func.__module__, func.__name__)
        REGISTERED.append({'func':func, 'name':name})
        return lambda plex, account: func(plex, account)
    return wrapper


def itertests(query):
    for test in REGISTERED:
        if not query:
            yield test
        elif query in test['name']:
            yield test


def log(indent, message, color=None):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if color:
        return sys.stdout.write('%s: %s%s%s%s\n' % (dt, ' '*indent, COLORS[color], message, COLORS['end']))
    return sys.stdout.write('%s: %s%s\n' % (dt, ' '*indent, message))


def getclient(name, baseurl, server):
    try:
        return server.client(name)
    except NotFound as err:
        log(2, 'Warning: %s' % err)
        return PlexClient(baseurl, server=server)

