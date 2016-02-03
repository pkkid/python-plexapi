"""
PlexPlaylist
"""
import re
from plexapi.client import Client
#from plexapi.media import Media, Genre, Producer, Country #, TranscodeSession
from plexapi.myplex import MyPlexUser
from plexapi.exceptions import NotFound, UnknownType, Unsupported
from plexapi.utils import PlexPartialObject, NA
from plexapi.utils import cast, toDatetime

from plexapi.video import Video # TODO: remove this when the Audio class can stand on its own legs

try:
    from urllib import urlencode  # Python2
except ImportError:
    from urllib.parse import urlencode  # Python3


class Playlist(Video): # TODO: inherit from PlexPartialObject, like the Video class does
    TYPE = 'playlist'

    def _loadData(self, data):
        self.type = data.attrib.get('type', NA)
        self.key = data.attrib.get('key', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.title = data.attrib.get('title', NA)
        self.summary = data.attrib.get('summary', NA)
        self.smart = cast(bool, data.attrib.get('smart', NA))
        self.playlistType = data.attrib.get('playlistType', NA)
        self.addedAt = toDatetime(data.attrib.get('addedAt', NA))
        self.updatedAt = toDatetime(data.attrib.get('updatedAt', NA))
        self.composite = data.attrib.get('composite', NA) # plex uri to thumbnail
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.leafCount = cast(int, data.attrib.get('leafCount', NA)) # number of items in playlist
        self.durationInSeconds = cast(int, data.attrib.get('durationInSeconds', NA))
        self.guid = data.attrib.get('guid', NA)
        self.user = self._find_user(data)       # for active sessions
        self.player = self._find_player(data)   # for active sessions
        if False: #self.isFullObject():
            # These are auto-populated when requested
            self.media = [Media(self.server, elem, self.initpath, self) for elem in data if elem.tag == Media.TYPE]
            self.genres = [Genre(self.server, elem) for elem in data if elem.tag == Genre.TYPE]
            self.producers = [Producer(self.server, elem) for elem in data if elem.tag == Producer.TYPE]
            # will we ever see other elements?
            #self.actors = [Actor(self.server, elem) for elem in data if elem.tag == Actor.TYPE]
            #self.writers = [Writer(self.server, elem) for elem in data if elem.tag == Writer.TYPE]


    def getStreamUrl(self, offset=0, **kwargs):
        """ Fetch URL to stream audio directly.
            offset: Start time (in seconds) audio will initiate from (ex: 300).
            params: Dict of additional parameters to include in URL.
        """
        if self.TYPE not in [Track.TYPE, Album.TYPE]:
            raise Unsupported('Cannot get stream URL for %s.' % self.TYPE)
        params = {}
        params['path'] = self.key
        params['offset'] = offset
        params['copyts'] = kwargs.get('copyts', 1)
        params['mediaIndex'] = kwargs.get('mediaIndex', 0)
        params['X-Plex-Platform'] = kwargs.get('platform', 'Chrome')
        if 'protocol' in kwargs:
            params['protocol'] = kwargs['protocol']
        return self.server.url('/audio/:/transcode/universal/start.m3u8?%s' % urlencode(params))

    def items(self, watched=None):
        if self.playlistType == 'audio':
            from audio import list_items
        elif self.playlistType == 'video':
            from video import list_items
        return list_items(self.server, self.key, watched=watched)

    # TODO: figure out if we really need to override these methods, or if there is a  bug in the default
    # implementation
    def isFullObject(self):
        return self.initpath == '/playlists/{0!s}'.format(self.ratingKey)

    def isPartialObject(self):
        return self.initpath != '/playlists/{0!s}'.format(self.ratingKey)

    def reload(self):
        self.initpath = '/playlists/{0!s}'.format(self.ratingKey)
        data = self.server.query(self.initpath)
        self._loadData(data[0])

