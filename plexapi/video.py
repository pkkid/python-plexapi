# -*- coding: utf-8 -*-
"""
PlexVideo
"""
import re
from plexapi import media, utils
from plexapi.compat import urlencode
from plexapi.exceptions import Unsupported
NA = utils.NA


class Video(utils.PlexPartialObject):
    TYPE = None

    def _loadData(self, data):
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt', NA))
        self.key = data.attrib.get('key', NA)
        self.lastViewedAt = utils.toDatetime(data.attrib.get('lastViewedAt', NA))
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.summary = data.attrib.get('summary', NA)
        self.thumb = data.attrib.get('thumb', NA)
        self.title = data.attrib.get('title', NA)
        self.titleSort = data.attrib.get('titleSort', self.title)
        self.type = data.attrib.get('type', NA)
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt', NA))
        self.viewCount = utils.cast(int, data.attrib.get('viewCount', 0))

    def analyze(self):
        """ The primary purpose of media analysis is to gather information about that media
            item. All of the media you add to a Library has properties that are useful to
            know–whether it's a video file, a music track, or one of your photos.
        """
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
        self.art = data.attrib.get('art', NA)
        self.audienceRating = utils.cast(float, data.attrib.get('audienceRating', NA))
        self.audienceRatingImage = data.attrib.get('audienceRatingImage', NA)
        self.chapterSource = data.attrib.get('chapterSource', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.guid = data.attrib.get('guid', NA)
        self.originalTitle = data.attrib.get('originalTitle', NA)
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.primaryExtraKey = data.attrib.get('primaryExtraKey', NA)
        self.rating = data.attrib.get('rating', NA)
        self.ratingImage = data.attrib.get('ratingImage', NA)
        self.studio = data.attrib.get('studio', NA)
        self.tagline = data.attrib.get('tagline', NA)
        self.userRating = utils.cast(float, data.attrib.get('userRating', NA))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            #self.collections = [media.Collection(self.server, elem) for elem in data if elem.tag == media.Collection.TYPE]
            self.countries = [media.Country(self.server, elem) for elem in data if elem.tag == media.Country.TYPE]
            self.directors = [media.Director(self.server, elem) for elem in data if elem.tag == media.Director.TYPE]
            #self.fields = [media.Field(self.server, elem) for elem in data if elem.tag == media.Field.TYPE]
            self.genres = [media.Genre(self.server, elem) for elem in data if elem.tag == media.Genre.TYPE]
            self.media = [media.Media(self.server, elem, self.initpath, self) for elem in data if elem.tag == media.Media.TYPE]
            self.producers = [media.Producer(self.server, elem) for elem in data if elem.tag == media.Producer.TYPE]
            self.roles = [media.Role(self.server, elem) for elem in data if elem.tag == media.Role.TYPE]
            self.writers = [media.Writer(self.server, elem) for elem in data if elem.tag == media.Writer.TYPE]
        # data for active sessions
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.user = self._findUser(data)
        self.player = self._findPlayer(data)
        self.transcodeSession = self._findTranscodeSession(data)
    
    @property
    def actors(self):
        return self.roles
    
    @property
    def is_watched(self):
        return bool(self.viewCount > 0)


@utils.register_libtype
class Show(Video):
    TYPE = 'show'

    def _loadData(self, data):
        super(Show, self)._loadData(data)
        self.art = data.attrib.get('art', NA)
        self.banner = data.attrib.get('banner', NA)
        self.childCount = utils.cast(int, data.attrib.get('childCount', NA))
        self.contentRating = data.attrib.get('contentRating', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.guid = data.attrib.get('guid', NA)
        self.leafCount = utils.cast(int, data.attrib.get('leafCount', NA))
        self.location = self._findLocation(data)
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.rating = utils.cast(float, data.attrib.get('rating', NA))
        self.studio = data.attrib.get('studio', NA)
        self.theme = data.attrib.get('theme', NA)
        self.viewedLeafCount = utils.cast(int, data.attrib.get('viewedLeafCount', NA))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            #self.fields = [media.Field(self.server, elem) for elem in data if elem.tag == media.Field.TYPE]
            self.genres = [media.Genre(self.server, elem) for elem in data if elem.tag == media.Genre.TYPE]
            self.roles = [media.Role(self.server, elem) for elem in data if elem.tag == media.Role.TYPE]

    @property
    def actors(self):
        return self.roles
        
    @property
    def is_watched(self):
        return bool(self.viewedLeafCount == self.leafCount)

    def seasons(self):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, path, Season.TYPE)

    def season(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def episodes(self, watched=None):
        leavesKey = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.listItems(self.server, leavesKey, watched=watched)

    def episode(self, title):
        path = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.findItem(self.server, path, title)

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
        self.leafCount = utils.cast(int, data.attrib.get('leafCount', NA))
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.viewedLeafCount = utils.cast(int, data.attrib.get('viewedLeafCount', NA))
        
    @property
    def is_watched(self):
        return bool(self.viewedLeafCount == self.leafCount)

    def episodes(self, watched=None):
        childrenKey = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, childrenKey, watched=watched)

    def episode(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def get(self, title):
        return self.episode(title)

    def show(self):
        return utils.listItems(self.server, self.parentKey)[0]

    def watched(self):
        return self.episodes(watched=True)

    def unwatched(self):
        return self.episodes(watched=False)


@utils.register_libtype
class Episode(Video):
    TYPE = 'episode'

    def _loadData(self, data):
        super(Episode, self)._loadData(data)
        self.art = data.attrib.get('art', NA)
        self.chapterSource = data.attrib.get('chapterSource', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.grandparentArt = data.attrib.get('grandparentArt', NA)
        self.grandparentKey = data.attrib.get('grandparentKey', NA)
        self.grandparentRatingKey = data.attrib.get('grandparentRatingKey', NA)
        self.grandparentTheme = data.attrib.get('grandparentTheme', NA)
        self.grandparentThumb = data.attrib.get('grandparentThumb', NA)
        self.grandparentTitle = data.attrib.get('grandparentTitle', NA)
        self.guid = data.attrib.get('guid', NA)
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.rating = utils.cast(float, data.attrib.get('rating', NA))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            self.directors = [media.Director(self.server, elem) for elem in data if elem.tag == media.Director.TYPE]
            #self.fields = [media.Field(self.server, elem) for elem in data if elem.tag == media.Field.TYPE]
            self.media = [media.Media(self.server, elem, self.initpath, self) for elem in data if elem.tag == media.Media.TYPE]
            self.writers = [media.Writer(self.server, elem) for elem in data if elem.tag == media.Writer.TYPE]
        # data for active sessions
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.user = self._findUser(data)
        self.player = self._findPlayer(data)
        self.transcodeSession = self._findTranscodeSession(data)

    @property
    def is_watched(self):
        return bool(self.viewCount > 0)

    @property
    def thumbUrl(self):
        return self.server.url(self.grandparentThumb)

    def season(self):
        return utils.listItems(self.server, self.parentKey)[0]

    def show(self):
        return utils.listItems(self.server, self.grandparentKey)[0]
