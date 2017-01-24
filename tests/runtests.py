#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
You can run this test suite with the following command:
>> python tests.py -u <USERNAME> -p <PASSWORD> -s <SERVERNAME>
"""
import argparse, os, pkgutil, sys, time, traceback
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
from utils import log, itertests


def runtests(args):
    # Get username and password from environment
    username = args.username or os.environ.get('TEST_PLEX_USERNAME')
    password = args.password or os.environ.get('TEST_PLEX_PASSWORD')
    resource = args.resource or os.environ.get('TEST_PLEX_RESOURCE')

    # Register known tests
    for loader, name, ispkg in pkgutil.iter_modules([dirname(abspath(__file__))]):
        if name.startswith('test_'):
            log(0, 'Registering tests from %s.py' % name)
            loader.find_module(name).load_module(name)
    # Create Account and Plex objects
    log(0, 'Logging into MyPlex as %s' % username)
    account = MyPlexAccount.signin(username, password)
    log(0, 'Signed into MyPlex as %s (%s)' % (account.username, account.email))
    if resource:
        plex = account.resource(resource).connect()
        log(0, 'Connected to PlexServer resource %s' % plex.friendlyName)
    else:
        plex = PlexServer(args.baseurl, args.token)
        log(0, 'Connected to PlexServer %s' % plex.friendlyName)
    log(0, '')
    # Run all specified tests
    tests = {'passed':0, 'failed':0}
    for test in itertests(args.query):
        starttime = time.time()
        log(0, test['name'], 'green')
        try:
            test['func'](account, plex)
            runtime = time.time() - starttime
            log(2, 'PASS! (runtime: %.3fs)' % runtime, 'blue')
            tests['passed'] += 1
        except Exception as err:
            errstr = str(err)
            errstr += '\n%s' % traceback.format_exc() if args.verbose else ''
            log(2, 'FAIL: %s' % errstr, 'red')
            tests['failed'] += 1
        log(0, '')
    # Log a final report
    log(0, 'Tests Run:    %s' % sum(tests.values()))
    log(0, 'Tests Passed: %s' % tests['passed'])
    if tests['failed']:
        log(0, 'Tests Failed: %s' % tests['failed'], 'red')
    if not tests['failed']:
        log(0, '')
        log(0, 'EVERYTHING OK!! :)')
    raise SystemExit(tests['failed'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run PlexAPI tests.')
    # Auth Method 1: Pass --username, --password, and optionally --resource.
    parser.add_argument('-u', '--username', help='Username for your MyPlex account.')
    parser.add_argument('-p', '--password', help='Password for your MyPlex account.')
    parser.add_argument('-r', '--resource', help='Name of the Plex resource (requires user/pass).')
    # Auth Method 2: Pass --baseurl and --token.
    parser.add_argument('-b', '--baseurl', help='Baseurl needed for auth token authentication')
    parser.add_argument('-t', '--token', help='Auth token (instead of user/pass)')
    # Misc options
    parser.add_argument('-q', '--query', help='Only run the specified tests.')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print verbose logging.')
    runtests(parser.parse_args())
