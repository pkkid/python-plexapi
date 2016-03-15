"""
PlexAPI Utils
"""
from datetime import datetime
from threading import Thread
from Queue import Queue
try:
    from urllib import quote  # Python2
except ImportError:
    from urllib.parse import quote  # Python3

# This used to be a simple variable equal to '__NA__'. However, there has been need to
# compare NA against None in some use cases. This object allows the internals of PlexAPI 
# to distinguish between unfetched values and fetched, but non-existent values.
# (NA == None results to True; NA is None results to False)
class __NA__(object):
    def __bool__(self): return False  # Python3; flake8: noqa
    def __eq__(self, other): return isinstance(other, __NA__) or other in [None, '__NA__']  # flake8: noqa
    def __nonzero__(self): return False  # Python2; flake8: noqa
    def __repr__(self): return '__NA__'  # flake8: noqa
NA = __NA__()
    

class PlexPartialObject(object):
    """ Not all objects in the Plex listings return the complete list of
        elements for the object. This object will allow you to assume each
        object is complete, and if the specified value you request is None
        it will fetch the full object automatically and update itself.
    """

    def __init__(self, server, data, initpath):
        self.server = server
        self.initpath = initpath
        self._loadData(data)
        
    def __eq__(self, other):
        return other is not None and self.type == other.type and self.key == other.key

    def __repr__(self):
        title = self.title.replace(' ','.')[0:20]
        return '<%s:%s>' % (self.__class__.__name__, title.encode('utf8'))

    def __getattr__(self, attr):
        if self.isPartialObject():
            self.reload()
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        if value != NA:
            super(PlexPartialObject, self).__setattr__(attr, value)

    def _loadData(self, data):
        raise Exception('Abstract method not implemented.')

    def isFullObject(self):
        return self.initpath == self.key

    def isPartialObject(self):
        return self.initpath != self.key

    def reload(self):
        data = self.server.query(self.key)
        self.initpath = self.key
        self._loadData(data[0])


def cast(func, value):
    if value not in [None, NA]:
        if func == bool:
            return bool(int(value))
        elif func in [int, float]:
            try:
                return func(value)
            except ValueError:
                return float('nan')
        return func(value)
    return value


def joinArgs(args):
    if not args: return ''
    arglist = []
    for key in sorted(args, key=lambda x:x.lower()):
        value = str(args[key])
        arglist.append('%s=%s' % (key, quote(value)))
    return '?%s' % '&'.join(arglist)


def threaded(funcs, *args, **kwargs):
    def _run(func, _args, _kwargs, results):
        results.put(func(*_args, **_kwargs))
    threads = []
    results = Queue(len(funcs) + 1)
    for func in funcs:
        targs = [func, args, kwargs, results]
        threads.append(Thread(target=_run, args=targs))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    results.put(None)
    return results


def toDatetime(value, format=None):
    if value and value != NA:
        if format: value = datetime.strptime(value, format)
        else: value = datetime.fromtimestamp(int(value))
    return value
