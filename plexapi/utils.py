# -*- coding: utf-8 -*-
"""
PlexAPI Utils
"""
import re
from datetime import datetime
from plexapi.compat import quote, urlencode
from plexapi.exceptions import NotFound, UnknownType, Unsupported
from threading import Thread
from plexapi import log

# Search Types - Plex uses these to filter specific media types when searching.
SEARCHTYPES = {'movie':1, 'show':2, 'season':3, 'episode':4, 'artist':8, 'album':9, 'track':10}

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

    def __init__(self, data, initpath, server=None):
        self.server = server
        self.initpath = initpath
        self._loadData(data)

    def __eq__(self, other):
        return other is not None and self.key == other.key

    def __repr__(self):
        clsname = self.__class__.__name__
        key = self.key.replace('/library/metadata/', '') if self.key else 'NA'
        title = self.title.replace(' ','.')[0:20].encode('utf8')
        return '<%s:%s:%s>' % (clsname, key, title)

    def __getattr__(self, attr):
        if attr == 'key' or self.__dict__.get(attr) or self.isFullObject():
            return self.__dict__.get(attr, NA)
        self.reload()
        return self.__dict__.get(attr, NA)

    def __setattr__(self, attr, value):     
        if value != NA or self.isFullObject():
            super(PlexPartialObject, self).__setattr__(attr, value)

    def _loadData(self, data):
        raise Exception('Abstract method not implemented.')

    def isFullObject(self):
        return not self.key or self.key == self.initpath

    def isPartialObject(self):
        return not self.isFullObject()

    def reload(self):
        """ Reload the data for this object from PlexServer XML. """
        data = self.server.query(self.key)
        self.initpath = self.key
        self._loadData(data[0])


# This is a general place to store functions specific to media that is Playable. Things
# were getting mixed up a bit when dealing with Shows, Season, Artists, Albums which
# are all not playable.
class Playable(object):
    
    def _loadData(self, data):
        # data for active sessions (/status/sessions)
        self.sessionKey = cast(int, data.attrib.get('sessionKey', NA))
        self.username = findUsername(data)
        self.player = findPlayer(self.server, data)
        self.transcodeSession = findTranscodeSession(self.server, data)
        # data for history details (/status/sessions/history/all)
        self.viewedAt = toDatetime(data.attrib.get('viewedAt', NA))
        # data for playlist items
        self.playlistItemID = cast(int, data.attrib.get('playlistItemID', NA))
    
    def getStreamURL(self, **params):
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
    
    def iterParts(self):
        for item in self.media:
            for part in item.parts:
                yield part
    
    def play(self, client):
        client.playMedia(self)


def buildItem(server, elem, initpath, bytag=False):
    libtype = elem.tag if bytag else elem.attrib.get('type')
    if libtype == 'photo' and elem.tag == 'Directory':
        libtype = 'photoalbum'
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


def findLocations(data, single=False):
    locations = []
    for elem in data:
        if elem.tag == 'Location':
            locations.append(elem.attrib.get('path'))
    if single:
        return locations[0] if locations else None
    return locations
    

def findPlayer(server, data):
    elem = data.find('Player')
    if elem is not None:
        from plexapi.client import PlexClient
        baseurl = 'http://%s:%s' % (elem.attrib.get('address'), elem.attrib.get('port'))
        return PlexClient(baseurl, server=server, data=elem)
    return None


def findStreams(media, streamtype):
    streams = []
    for mediaitem in media:
        for part in mediaitem.parts:
            for stream in part.streams:
                if stream.TYPE == streamtype:
                    streams.append(stream)
    return streams


def findTranscodeSession(server, data):
    elem = data.find('TranscodeSession')
    if elem is not None:
        from plexapi import media
        return media.TranscodeSession(server, elem)
    return None


def findUsername(data):
    elem = data.find('User')
    if elem is not None:
        return elem.attrib.get('title')
    return None


def isInt(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False


def joinArgs(args):
    if not args: return ''
    arglist = []
    for key in sorted(args, key=lambda x:x.lower()):
        value = str(args[key])
        arglist.append('%s=%s' % (key, quote(value)))
    return '?%s' % '&'.join(arglist)


def listChoices(server, path):
    return {c.attrib['title']:c.attrib['key'] for c in server.query(path)}


def listItems(server, path, libtype=None, watched=None, bytag=False):
    items = []
    for elem in server.query(path):
        if libtype and elem.attrib.get('type') != libtype: continue
        if watched is True and elem.attrib.get('viewCount', 0) == 0: continue
        if watched is False and elem.attrib.get('viewCount', 0) >= 1: continue
        try:
            items.append(buildItem(server, elem, path, bytag))
        except UnknownType:
            pass
    return items
    

def rget(obj, attrstr, default=None, delim='.'):
    try:
        parts = attrstr.split(delim, 1)
        attr = parts[0]
        attrstr = parts[1] if len(parts) == 2 else None
        if isinstance(obj, dict): value = obj[attr]
        elif isinstance(obj, list): value = obj[int(attr)]
        elif isinstance(obj, tuple): value = obj[int(attr)]
        elif isinstance(obj, object): value = getattr(obj, attr)
        if attrstr: return rget(value, attrstr, default, delim)
        return value
    except:
        return default
    

def searchType(libtype):
    libtype = str(libtype)
    if libtype in [str(v) for v in SEARCHTYPES.values()]:
        return libtype
    if SEARCHTYPES.get(libtype) is not None:
        return SEARCHTYPES[libtype]
    raise NotFound('Unknown libtype: %s' % libtype)


def threaded(callback, listargs):
    threads, results = [], []
    for args in listargs:
        args += [results, len(results)]
        results.append(None)
        threads.append(Thread(target=callback, args=args))
        threads[-1].start()
    for thread in threads:
        thread.join()
    return results


def toDatetime(value, format=None):
    if value and value != NA:
        if format: value = datetime.strptime(value, format)
        else: value = datetime.fromtimestamp(int(value))
    return value
