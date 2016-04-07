# -*- coding: utf-8 -*-
"""
Test Library Functions
"""
import sys, traceback
import datetime, time
from plexapi import server
from plexapi.client import PlexClient
from plexapi.exceptions import NotFound
from plexapi.myplex import MyPlexAccount

COLORS = {'blue':'\033[94m', 'green':'\033[92m', 'red':'\033[91m', 'yellow':'\033[93m', 'end':'\033[0m'}


registered = []
def register(tags=''):
    def wrap2(func):
        registered.append({'name':func.__name__, 'tags':tags.split(','), 'func':func})
        def wrap1(*args, **kwargs):  # noqa
            func(*args, **kwargs)
        return wrap1
    return wrap2


def log(indent, message, color=None):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if color:
        return sys.stdout.write('%s: %s%s%s%s\n' % (dt, ' '*indent, COLORS[color], message, COLORS['end']))
    return sys.stdout.write('%s: %s%s\n' % (dt, ' '*indent, message))


def fetch_server(args):
    if args.resource and args.username and args.password:
        log(0, 'Signing in as MyPlex account %s..' % args.username)
        account = MyPlexAccount.signin(args.username, args.password)
        log(0, 'Connecting to Plex server %s..' % args.resource)
        return account.resource(args.resource).connect(), account
    elif args.baseurl and args.token:
        log(0, 'Connecting to Plex server %s..' % args.baseurl)
        return server.PlexServer(args.baseurl, args.token), None
    return server.PlexServer(), None


def safe_client(name, baseurl, server):
    try:
        return server.client(name)
    except NotFound as err:
        log(2, 'Warning: %s' % err)
        return PlexClient(baseurl, server=server)


def iter_tests(query):
    tags = query[5:].split(',') if query and query.startswith('tags:') else ''
    for test in registered:
        if not query:
            yield test
        elif tags:
            matching_tags = [t for t in tags if t in test['tags']]
            if matching_tags: yield test
        elif query == test['name']:
            yield test


def run_tests(module, args):
    plex, account = fetch_server(args)
    tests = {'passed':0, 'failed':0}
    for test in iter_tests(args.query):
        starttime = time.time()
        log(0, '%s (%s)' % (test['name'], ','.join(test['tags'])))
        try:
            test['func'](plex, account)
            runtime = time.time() - starttime
            log(2, 'PASS! (runtime: %.3fs)' % runtime, 'blue')
            tests['passed'] += 1
        except Exception as err:
            errstr = str(err)
            errstr += '\n%s' % traceback.format_exc() if args.verbose else ''
            log(2, 'FAIL!: %s' % errstr, 'red')
            tests['failed'] += 1
        log(0, '')
    log(0, 'Tests Run:    %s' % sum(tests.values()))
    log(0, 'Tests Passed: %s' % tests['passed'])
    if tests['failed']:
        log(0, 'Tests Failed: %s' % tests['failed'], 'red')
    if not tests['failed']:
        log(0, '')
        log(0, 'EVERYTHING OK!! :)')
    raise SystemExit(tests['failed'])
