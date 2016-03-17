"""
PlexAudio
"""
from plexapi import utils
from plexapi.media import Media, Genre, Producer
from plexapi.exceptions import Unsupported
from plexapi.utils import NA
from plexapi.utils import cast, toDatetime, register_libtype
from plexapi.video import Video  # TODO: remove this when Audio class can stand on its own legs
try:
    from urllib import urlencode  # Python2
except ImportError:
    from urllib.parse import urlencode  # Python3


class Audio(Video):  # TODO: inherit from PlexPartialObject, like the Video class does

    def _loadData(self, data):
        self.type = data.attrib.get('type', NA)
        self.key = data.attrib.get('key', NA)
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.title = data.attrib.get('title', NA)
        self.summary = data.attrib.get('summary', NA)
        self.art = data.attrib.get('art', NA)
        self.thumb = data.attrib.get('thumb', NA)
        self.addedAt = toDatetime(data.attrib.get('addedAt', NA))
        self.updatedAt = toDatetime(data.attrib.get('updatedAt', NA))
        self.sessionKey = cast(int, data.attrib.get('sessionKey', NA))
        self.user = self._find_user(data)       # for active sessions
        self.player = self._find_player(data)   # for active sessions
        self.transcodeSession = self._find_transcodeSession(data)
        if self.isFullObject():
            # These are auto-populated when requested
            self.media = [Media(self.server, elem, self.initpath, self) for elem in data if elem.tag == Media.TYPE]
            self.genres = [Genre(self.server, elem) for elem in data if elem.tag == Genre.TYPE]
            self.producers = [Producer(self.server, elem) for elem in data if elem.tag == Producer.TYPE]

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

    # TODO: figure out if we really need to override these methods, or if
    # there is a  bug in the default implementation
    def isFullObject(self):
        return self.initpath == '/library/metadata/{0!s}'.format(self.ratingKey)

    def isPartialObject(self):
        return self.initpath != '/library/metadata/{0!s}'.format(self.ratingKey)

    def reload(self):
        self.initpath = '/library/metadata/{0!s}'.format(self.ratingKey)
        data = self.server.query(self.initpath)
        self._loadData(data[0])


@register_libtype
class Artist(Audio):
    TYPE = 'artist'

    def _loadData(self, data):
        super(Artist, self)._loadData(data)
        # TODO: get proper metadata for artists, not this blue copy
        self.studio = data.attrib.get('studio', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.rating = data.attrib.get('rating', NA)
        self.year = cast(int, data.attrib.get('year', NA))
        self.banner = data.attrib.get('banner', NA)
        self.theme = data.attrib.get('theme', NA)
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.leafCount = cast(int, data.attrib.get('leafCount', NA))
        self.viewedLeafCount = cast(int, data.attrib.get('viewedLeafCount', NA))
        self.childCount = cast(int, data.attrib.get('childCount', NA))
        self.titleSort = data.attrib.get('titleSort', NA)

    def albums(self):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.list_items(self.server, path, Album.TYPE)

    def album(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.find_item(self.server, path, title)

    def tracks(self, watched=None):
        leavesKey = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.list_items(self.server, leavesKey, watched=watched)

    def track(self, title):
        path = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.find_item(self.server, path, title)

    def watched(self):
        return self.episodes(watched=True)

    def unwatched(self):
        return self.episodes(watched=False)

    def get(self, title):
        return self.track(title)

    def refresh(self):
        self.server.query('/library/metadata/%s/refresh' % self.ratingKey)


@register_libtype
class Album(Audio):
    TYPE = 'album'

    def _loadData(self, data):
        super(Album, self)._loadData(data)
        # TODO: get proper metadata for artists, not this blue copy
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.librarySectionTitle = data.attrib.get('librarySectionTitle', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.parentSummary = data.attrib.get('parentSummary', NA)
        self.index = data.attrib.get('index', NA)
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.parentTheme = data.attrib.get('parentTheme', NA)
        self.leafCount = cast(int, data.attrib.get('leafCount', NA))
        self.viewedLeafCount = cast(int, data.attrib.get('viewedLeafCount', NA))
        self.year = cast(int, data.attrib.get('year', NA))

    def tracks(self, watched=None):
        childrenKey = '/library/metadata/%s/children' % self.ratingKey
        return utils.list_items(self.server, childrenKey, watched=watched)

    def track(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.find_item(self.server, path, title)

    def get(self, title):
        return self.track(title)

    def artist(self):
        return utils.list_items(self.server, self.parentKey)[0]

    def watched(self):
        return self.tracks(watched=True)

    def unwatched(self):
        return self.tracks(watched=False)


@register_libtype
class Track(Audio):
    TYPE = 'track'

    def _loadData(self, data):
        super(Track, self)._loadData(data)
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.librarySectionTitle = data.attrib.get('librarySectionTitle', NA)
        self.grandparentKey = data.attrib.get('grandparentKey', NA)
        self.grandparentTitle = data.attrib.get('grandparentTitle', NA)
        self.grandparentThumb = data.attrib.get('grandparentThumb', NA)
        self.grandparentArt = data.attrib.get('grandparentArt', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.index = data.attrib.get('index', NA)
        self.rating = data.attrib.get('rating', NA)
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')

    @property
    def thumbUrl(self):
        return self.server.url(self.grandparentThumb)

    def album(self):
        return utils.list_items(self.server, self.parentKey)[0]

    def artist(self):
        raise NotImplemented
        #return list_items(self.server, self.grandparentKey)[0]
