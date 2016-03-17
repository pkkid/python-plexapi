"""
PlexAPI Utils
"""
from datetime import datetime
from threading import Thread
from Queue import Queue
from plexapi.exceptions import UnknownType
try:
    from urllib import quote  # Python2
except ImportError:
    from urllib.parse import quote  # Python3


# Registry of library types we may come across when parsing XML. This allows us to
# define a few helper functions to dynamically convery the XML into objects.
# see build_item() below for an example.
LIBRARY_TYPES = {}
def register_libtype(cls):
    LIBRARY_TYPES[cls.TYPE] = cls
    return cls


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


# Not all objects in the Plex listings return the complete list of elements for the object.
# This object will allow you to assume each object is complete, and if the specified value
# you request is None it will fetch the full object automatically and update itself.
class PlexPartialObject(object):

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


def build_item(server, elem, initpath):
    libtype = elem.attrib.get('type')
    if libtype in LIBRARY_TYPES:
        cls = LIBRARY_TYPES[libtype]
        return cls(server, elem, initpath)
    raise UnknownType('Unknown library type: %s' % libtype)


def find_key(server, key):
    path = '/library/metadata/{0}'.format(key)
    try:
        # Item seems to be the first sub element
        elem = server.query(path)[0]
        return build_item(server, elem, path)
    except:
        raise NotFound('Unable to find key: %s' % key)


def find_item(server, path, title):
    for elem in server.query(path):
        if elem.attrib.get('title').lower() == title.lower():
            return build_item(server, elem, path)
    raise NotFound('Unable to find item: %s' % title)


def list_items(server, path, libtype=None, watched=None):
    items = []
    for elem in server.query(path):
        if libtype and elem.attrib.get('type') != libtype: continue
        if watched is True and elem.attrib.get('viewCount', 0) == 0: continue
        if watched is False and elem.attrib.get('viewCount', 0) >= 1: continue
        try:
            items.append(build_item(server, elem, path))
        except UnknownType:
            pass
    return items
    

def search_type(libtype):
    if libtype == LIBRARY_TYPES['movie'].TYPE: return 1
    elif libtype == LIBRARY_TYPES['show'].TYPE: return 2
    elif libtype == LIBRARY_TYPES['season'].TYPE: return 3
    elif libtype == LIBRARY_TYPES['episode'].TYPE: return 4
    elif libtype == LIBRARY_TYPES['artist'].TYPE: return 8
    elif libtype == LIBRARY_TYPES['album'].TYPE: return 9
    elif libtype == LIBRARY_TYPES['track'].TYPE: return 10
    raise NotFound('Unknown libtype: %s' % libtype)


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
