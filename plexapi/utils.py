# -*- coding: utf-8 -*-
"""
PlexAPI Utils
"""
import re
from requests import put
from datetime import datetime
from plexapi.compat import quote, urlencode
from plexapi.exceptions import NotFound, UnknownType, Unsupported


# Registry of library types we may come across when parsing XML. This allows us to
# define a few helper functions to dynamically convery the XML into objects.
# see buildItem() below for an example.
LIBRARY_TYPES = {}
def register_libtype(cls):
    LIBRARY_TYPES[cls.TYPE] = cls
    return cls


# This used to be a simple variable equal to '__NA__'. However, there has been need to
# compare NA against None in some use cases. This object allows the internals of PlexAPI 
# to distinguish between unfetched values and fetched, but non-existent values.
# (NA == None results to True; NA is None results to False)
class _NA(object):
    def __bool__(self): return False
    def __eq__(self, other): return isinstance(other, _NA) or other in [None, '__NA__']
    def __nonzero__(self): return False
    def __repr__(self): return '__NA__'
NA = _NA()


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

    @property
    def thumbUrl(self):
        return self.server.url(self.thumb)
        
    def _getStreamURL(self, **params):
        if self.TYPE not in ('movie', 'episode', 'track'):
            raise Unsupported('Fetching stream URL for %s is unsupported.' % self.TYPE)
        mvb = params.get('maxVideoBitrate')
        vr = params.get('videoResolution', '')
        params = {
            'path': self.key,
            'offset': params.get('offset', 0),
            'copyts': params.get('copyts', 1),
            'protocol': params.get('protocol'),
            'mediaIndex': params.get('mediaIndex', 0),
            'X-Plex-Platform': params.get('platform', 'Chrome'),
            'maxVideoBitrate': max(mvb,64) if mvb else None,
            'videoResolution': vr if re.match('^\d+x\d+$', vr) else None
        }
        params = {k:v for k,v in params.items() if v is not None}  # remove None values
        streamtype = 'audio' if self.TYPE in ('track', 'album') else 'video'
        return self.server.url('/%s/:/transcode/universal/start.m3u8?%s' % (streamtype, urlencode(params)))

    def _findLocation(self, data):
        elem = data.find('Location')
        if elem is not None:
            return elem.attrib.get('path')
        return None

    def _findPlayer(self, data):
        elem = data.find('Player')
        if elem is not None:
            from plexapi.client import Client
            return Client(self.server, elem)
        return None

    def _findTranscodeSession(self, data):
        elem = data.find('TranscodeSession')
        if elem is not None:
            from plexapi import media
            return media.TranscodeSession(self.server, elem)
        return None

    def _findUser(self, data):
        elem = data.find('User')
        if elem is not None:
            from plexapi.myplex import MyPlexUser
            return MyPlexUser(elem, self.initpath)
        return None

    def _loadData(self, data):
        raise Exception('Abstract method not implemented.')

    def isFullObject(self):
        return self.initpath == self.key

    def isPartialObject(self):
        return not self.isFullObject()
        
    def iterParts(self):
        for item in self.media:
            for part in item.parts:
                yield part

    def play(self, client):
        client.playMedia(self)

    def refresh(self):
        self.server.query('%s/refresh' % self.key, method=put)

    def reload(self):
        """ Reload the data for this object from PlexServer XML. """
        data = self.server.query(self.key)
        self.initpath = self.key
        self._loadData(data[0])


def buildItem(server, elem, initpath):
    libtype = elem.attrib.get('type')
    if libtype in LIBRARY_TYPES:
        cls = LIBRARY_TYPES[libtype]
        return cls(server, elem, initpath)
    raise UnknownType('Unknown library type: %s' % libtype)


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


def findKey(server, key):
    path = '/library/metadata/{0}'.format(key)
    try:
        # Item seems to be the first sub element
        elem = server.query(path)[0]
        return buildItem(server, elem, path)
    except:
        raise NotFound('Unable to find key: %s' % key)


def findItem(server, path, title):
    for elem in server.query(path):
        if elem.attrib.get('title').lower() == title.lower():
            return buildItem(server, elem, path)
    raise NotFound('Unable to find item: %s' % title)


def joinArgs(args):
    if not args: return ''
    arglist = []
    for key in sorted(args, key=lambda x:x.lower()):
        value = str(args[key])
        arglist.append('%s=%s' % (key, quote(value)))
    return '?%s' % '&'.join(arglist)


def listItems(server, path, libtype=None, watched=None):
    items = []
    for elem in server.query(path):
        if libtype and elem.attrib.get('type') != libtype: continue
        if watched is True and elem.attrib.get('viewCount', 0) == 0: continue
        if watched is False and elem.attrib.get('viewCount', 0) >= 1: continue
        try:
            items.append(buildItem(server, elem, path))
        except UnknownType:
            pass
    return items
    

def searchType(libtype):
    if libtype == 'movie': return 1
    elif libtype == 'show': return 2
    elif libtype == 'season': return 3
    elif libtype == 'episode': return 4
    elif libtype == 'artist': return 8
    elif libtype == 'album': return 9
    elif libtype == 'track': return 10
    raise NotFound('Unknown libtype: %s' % libtype)


def toDatetime(value, format=None):
    if value and value != NA:
        if format: value = datetime.strptime(value, format)
        else: value = datetime.fromtimestamp(int(value))
    return value
