# -*- coding: utf-8 -*-
"""
PlexAPI Audio
"""
from plexapi import media, utils
from plexapi.compat import urlencode
from plexapi.exceptions import Unsupported
NA = utils.NA


class Audio(utils.PlexPartialObject):

    def _loadData(self, data):
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt', NA))
        self.index = data.attrib.get('index', NA)
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

    def reload(self):
        self.initpath = '/library/metadata/%s' % self.ratingKey
        data = self.server.query(self.initpath)
        self._loadData(data[0])


@utils.register_libtype
class Artist(Audio):
    TYPE = 'artist'

    def _loadData(self, data):
        super(Artist, self)._loadData(data)
        self.art = data.attrib.get('art', NA)
        self.guid = data.attrib.get('guid', NA)
        self.key = self.key.replace('/children', '')  # plex bug? http://bit.ly/1Sc2J3V
        self.location = self._findLocation(data)  
        if self.isFullObject():
            self.countries = [media.Country(self.server, elem) for elem in data if elem.tag == media.Country.TYPE]
            self.genres = [media.Genre(self.server, elem) for elem in data if elem.tag == media.Genre.TYPE]
            self.similar = [media.Similar(self.server, elem) for elem in data if elem.tag == media.Similar.TYPE]

    def albums(self):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, path, Album.TYPE)

    def album(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def tracks(self, watched=None):
        leavesKey = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.listItems(self.server, leavesKey, watched=watched)

    def track(self, title):
        path = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def get(self, title):
        return self.track(title)
        
    def isFullObject(self):
        # plex bug? http://bit.ly/1Sc2J3V
        fixed_key = self.key.replace('/children', '')
        return self.initpath == fixed_key

    def refresh(self):
        self.server.query('/library/metadata/%s/refresh' % self.ratingKey)


@utils.register_libtype
class Album(Audio):
    TYPE = 'album'

    def _loadData(self, data):
        super(Album, self)._loadData(data)
        self.art = data.attrib.get('art', NA)
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.studio = data.attrib.get('studio', NA)
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            self.genres = [media.Genre(self.server, elem) for elem in data if elem.tag == media.Genre.TYPE]

    def tracks(self, watched=None):
        childrenKey = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, childrenKey, watched=watched)

    def track(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def get(self, title):
        return self.track(title)

    def artist(self):
        return utils.listItems(self.server, self.parentKey)[0]

    def watched(self):
        return self.tracks(watched=True)

    def unwatched(self):
        return self.tracks(watched=False)


@utils.register_libtype
class Track(Audio):
    TYPE = 'track'

    def _loadData(self, data):
        super(Track, self)._loadData(data)
        self.art = data.attrib.get('art', NA)
        self.chapterSource = data.attrib.get('chapterSource', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.grandparentArt = data.attrib.get('grandparentArt', NA)
        self.grandparentKey = data.attrib.get('grandparentKey', NA)
        self.grandparentRatingKey = data.attrib.get('grandparentRatingKey', NA)
        self.grandparentThumb = data.attrib.get('grandparentThumb', NA)
        self.grandparentTitle = data.attrib.get('grandparentTitle', NA)
        self.guid = data.attrib.get('guid', NA)
        self.originalTitle = data.attrib.get('originalTitle', NA)
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.primaryExtraKey = data.attrib.get('primaryExtraKey', NA)
        self.ratingCount = utils.cast(int, data.attrib.get('ratingCount', NA))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            self.moods = [media.Mood(self.server, elem) for elem in data if elem.tag == media.Mood.TYPE]
            self.media = [media.Media(self.server, elem, self.initpath, self) for elem in data if elem.tag == media.Media.TYPE]
        # data for active sessions
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.user = self._findUser(data)
        self.player = self._findPlayer(data)
        self.transcodeSession = self._findTranscodeSession(data)

    @property
    def thumbUrl(self):
        return self.server.url(self.parentThumb)

    def album(self):
        return utils.listItems(self.server, self.parentKey)[0]

    def artist(self):
        return utils.listItems(self.server, self.grandparentKey)[0]
