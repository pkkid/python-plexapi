"""
Test Library Functions
"""
import inspect, sys
import datetime, time
from plexapi import server
from plexapi.myplex import MyPlexUser

COLORS = dict(
    blue = '\033[94m',
    green = '\033[92m',
    red = '\033[91m',
    yellow = '\033[93m',
    end = '\033[0m',
)


def log(indent, message, color=None):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if color:
        print('%s: %s%s%s%s' % (dt, ' '*indent, COLORS[color], message, COLORS['end']))
    else:
        print('%s: %s%s' % (dt, ' '*indent, message))


def fetch_server(args):
    if args.resource:
        user = MyPlexUser.signin(args.username, args.password)
        return user.getResource(args.resource).connect(), user
    return server.PlexServer(), None


def iter_tests(module, args):
    check_test = lambda name: name.startswith('test_') or name.startswith('example_')
    check_name = lambda name: not args.name or args.name in name
    module = sys.modules[module]
    for func in sorted(module.__dict__.values()):
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
            if check_test(func.__name__) and check_name(func.__name__):
                yield func


def run_tests(module, args):
    plex, user = fetch_server(args)
    tests = {'passed':0, 'failed':0}
    for test in iter_tests(module, args):
        startqueries = server.TOTAL_QUERIES
        starttime = time.time()
        log(0, test.__name__)
        try:
            test(plex, user)
            log(2, 'PASS!', 'blue')
            tests['passed'] += 1
        except Exception as err:
            log(2, 'FAIL!: %s' % err, 'red')
            tests['failed'] += 1
        runtime = time.time() - starttime
        log(2, 'Runtime: %.3fs' % runtime)
        log(2, 'Queries: %s' % (server.TOTAL_QUERIES - startqueries))
        log(0, '')
    log(0, 'Tests Run:    %s' % sum(tests.values()))
    log(0, 'Tests Passed: %s' % tests['passed'])
    log(0, 'Tests Failed: %s' % tests['failed'])
    if not tests['failed']:
        log(0, '')
        log(0, 'EVERYTHING OK!! :)')
    raise SystemExit(tests['failed'])
