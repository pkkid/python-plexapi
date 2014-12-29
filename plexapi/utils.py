"""
PlexAPI Utils
"""
import urllib
from datetime import datetime

NA = '__NA__'  # Value not available


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

    def __getattr__(self, attr):
        if self.isPartialObject():
            self.reload()
        return self.__dict__.get(attr)

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


class Connection(object):
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)

    @classmethod
    def from_xml(cls, data):
        uri = data.attrib.get('uri')
        addr, port = [elem.strip('/') for elem in uri.split(':')[1:]]
        return Connection(addr, port)

    def __repr__(self):
        return '<Connection:{0}:{1}>'.format(self.addr, self.port)


def cast(func, value):
    if value not in [None, NA]:
        if func == bool:
            value = int(value)
        value = func(value)
    return value


def joinArgs(args):
    if not args: return ''
    arglist = []
    for key in sorted(args, key=lambda x:x.lower()):
        value = str(args[key])
        arglist.append('%s=%s' % (key, urllib.quote(value)))
    return '?%s' % '&'.join(arglist)


def toDatetime(value, format=None):
    if value and value != NA:
        if format: value = datetime.strptime(value, format)
        else: value = datetime.fromtimestamp(int(value))
    return value


def lazyproperty(func):
    """ Decorator: Memoize method result. """
    attr = '_lazy_%s' % func.__name__
    @property
    def wrapper(self):
        if not hasattr(self, attr):
            setattr(self, attr, func(self))
        return getattr(self, attr)
    return wrapper
