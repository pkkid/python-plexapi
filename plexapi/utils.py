"""
PlexAPI Utils
"""
from datetime import datetime

try:
    from urllib import quote  # Python2
except ImportError:
    from urllib.parse import quote  # Python3

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
        arglist.append('%s=%s' % (key, quote(value)))
    return '?%s' % '&'.join(arglist)


def toDatetime(value, format=None):
    if value and value != NA:
        if format: value = datetime.strptime(value, format)
        else: value = datetime.fromtimestamp(int(value))
    return value
