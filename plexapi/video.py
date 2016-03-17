"""
PlexVideo
"""
import re
from requests import put
from plexapi import media, utils
from plexapi.client import Client
from plexapi.compat import urlencode
from plexapi.myplex import MyPlexUser
from plexapi.exceptions import Unsupported
NA = utils.NA


class Video(utils.PlexPartialObject):
    TYPE = None

    def _loadData(self, data):
        self.type = data.attrib.get('type', NA)
        self.key = data.attrib.get('key', NA)
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.title = data.attrib.get('title', NA)
        self.originalTitle = data.attrib.get('originalTitle', NA)
        self.summary = data.attrib.get('summary', NA)
        self.art = data.attrib.get('art', NA)
        self.thumb = data.attrib.get('thumb', NA)
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt', NA))
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt', NA))
        self.lastViewedAt = utils.toDatetime(data.attrib.get('lastViewedAt', NA))
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.user = self._find_user(data)       # for active sessions
        self.player = self._find_player(data)   # for active sessions
        self.transcodeSession = self._find_transcodeSession(data)
        if self.isFullObject():
            # These are auto-populated when requested
            self.media = [media.Media(self.server, elem, self.initpath, self) for elem in data if elem.tag == media.Media.TYPE]
            self.countries = [media.Country(self.server, elem) for elem in data if elem.tag == media.Country.TYPE]
            self.directors = [media.Director(self.server, elem) for elem in data if elem.tag == media.Director.TYPE]
            self.genres = [media.Genre(self.server, elem) for elem in data if elem.tag == media.Genre.TYPE]
            self.producers = [media.Producer(self.server, elem) for elem in data if elem.tag == media.Producer.TYPE]
            self.actors = [media.Actor(self.server, elem) for elem in data if elem.tag == media.Actor.TYPE]
            self.writers = [media.Writer(self.server, elem) for elem in data if elem.tag == media.Writer.TYPE]

    @property
    def thumbUrl(self):
        return self.server.url(self.thumb)

    def _find_user(self, data):
        elem = data.find('User')
        if elem is not None:
            return MyPlexUser(elem, self.initpath)
        return None

    def _find_player(self, data):
        elem = data.find('Player')
        if elem is not None:
            return Client(self.server, elem)
        return None

    def _find_transcodeSession(self, data):
        elem = data.find('TranscodeSession')
        if elem is not None:
            return media.TranscodeSession(self.server, elem)
        return None

    def iter_parts(self):
        for item in self.media:
            for part in item.parts:
                yield part

    def analyze(self):
        self.server.query('/%s/analyze' % self.key)

    def getStreamUrl(self, offset=0, maxVideoBitrate=None, videoResolution=None, **kwargs):
        """ Fetch URL to stream video directly.
            offset: Start time (in seconds) video will initiate from (ex: 300).
            maxVideoBitrate: Max bitrate video and audio stream (ex: 64).
            videoResolution: Max resolution of a video stream (ex: 1280x720).
            params: Dict of additional parameters to include in URL.
        """
        if self.TYPE not in [Movie.TYPE, Episode.TYPE]:
            raise Unsupported('Cannot get stream URL for %s.' % self.TYPE)
        params = {}
        params['path'] = self.key
        params['offset'] = offset
        params['copyts'] = kwargs.get('copyts', 1)
        params['mediaIndex'] = kwargs.get('mediaIndex', 0)
        params['X-Plex-Platform'] = kwargs.get('platform', 'Chrome')
        if 'protocol' in kwargs:
            params['protocol'] = kwargs['protocol']
        if maxVideoBitrate:
            params['maxVideoBitrate'] = max(maxVideoBitrate, 64)
        if videoResolution and re.match('^\d+x\d+$', videoResolution):
            params['videoResolution'] = videoResolution
        return self.server.url('/video/:/transcode/universal/start.m3u8?%s' % urlencode(params))

    def markWatched(self):
        path = '/:/scrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self.server.query(path)
        self.reload()

    def markUnwatched(self):
        path = '/:/unscrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self.server.query(path)
        self.reload()

    def play(self, client):
        client.playMedia(self)

    def refresh(self):
        self.server.query('%s/refresh' % self.key, method=put)


@utils.register_libtype
class Movie(Video):
    TYPE = 'movie'

    def _loadData(self, data):
        super(Movie, self)._loadData(data)
        self.studio = data.attrib.get('studio', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.rating = data.attrib.get('rating', NA)
        self.viewCount = utils.cast(int, data.attrib.get('viewCount', 0))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        self.summary = data.attrib.get('summary', NA)
        self.tagline = data.attrib.get('tagline', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.primaryExtraKey = data.attrib.get('primaryExtraKey', NA)
        self.is_watched = bool(self.viewCount > 0)  # custom attr


@utils.register_libtype
class Show(Video):
    TYPE = 'show'

    def _loadData(self, data):
        super(Show, self)._loadData(data)
        self.studio = data.attrib.get('studio', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.rating = data.attrib.get('rating', NA)
        self.year = utils.cast(int, data.attrib.get('year', NA))
        self.banner = data.attrib.get('banner', NA)
        self.theme = data.attrib.get('theme', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.leafCount = utils.cast(int, data.attrib.get('leafCount', NA))
        self.viewedLeafCount = utils.cast(int, data.attrib.get('viewedLeafCount', NA))
        self.childCount = utils.cast(int, data.attrib.get('childCount', NA))

    def seasons(self):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.list_items(self.server, path, Season.TYPE)

    def season(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.find_item(self.server, path, title)

    def episodes(self, watched=None):
        leavesKey = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.list_items(self.server, leavesKey, watched=watched)

    def episode(self, title):
        path = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.find_item(self.server, path, title)

    def watched(self):
        return self.episodes(watched=True)

    def unwatched(self):
        return self.episodes(watched=False)

    def get(self, title):
        return self.episode(title)

    def refresh(self):
        self.server.query('/library/metadata/%s/refresh' % self.ratingKey)


@utils.register_libtype
class Season(Video):
    TYPE = 'season'

    def _loadData(self, data):
        super(Season, self)._loadData(data)
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
        self.leafCount = utils.cast(int, data.attrib.get('leafCount', NA))
        self.viewedLeafCount = utils.cast(int, data.attrib.get('viewedLeafCount', NA))

    def episodes(self, watched=None):
        childrenKey = '/library/metadata/%s/children' % self.ratingKey
        return utils.list_items(self.server, childrenKey, watched=watched)

    def episode(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.find_item(self.server, path, title)

    def get(self, title):
        return self.episode(title)

    def show(self):
        return utils.list_items(self.server, self.parentKey)[0]

    def watched(self):
        return self.episodes(watched=True)

    def unwatched(self):
        return self.episodes(watched=False)


@utils.register_libtype
class Episode(Video):
    TYPE = 'episode'

    def _loadData(self, data):
        super(Episode, self)._loadData(data)
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.librarySectionTitle = data.attrib.get('librarySectionTitle', NA)
        self.grandparentKey = data.attrib.get('grandparentKey', NA)
        self.grandparentTitle = data.attrib.get('grandparentTitle', NA)
        self.grandparentThumb = data.attrib.get('grandparentThumb', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.index = data.attrib.get('index', NA)
        self.rating = data.attrib.get('rating', NA)
        self.viewCount = utils.cast(int, data.attrib.get('viewCount', 0))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.is_watched = bool(self.viewCount > 0)  # custom attr

    @property
    def thumbUrl(self):
        return self.server.url(self.grandparentThumb)

    def season(self):
        return utils.list_items(self.server, self.parentKey)[0]

    def show(self):
        return utils.list_items(self.server, self.grandparentKey)[0]
