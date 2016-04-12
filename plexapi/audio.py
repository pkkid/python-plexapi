# -*- coding: utf-8 -*-
"""
PlexAPI Audio
"""
from plexapi import media, utils
from plexapi.utils import Playable, PlexPartialObject
NA = utils.NA


class Audio(PlexPartialObject):
    TYPE = None
    
    def __init__(self, server, data, initpath):
        super(Audio, self).__init__(data, initpath, server)

    def _loadData(self, data):
        self.listType = 'audio'
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
        
    @property
    def thumbUrl(self):
        return self.server.url(self.thumb)
    
    def refresh(self):
        self.server.query('%s/refresh' % self.key, method=self.server.session.put)
    
    def section(self):
        return self.server.library.sectionByID(self.librarySectionID)


@utils.register_libtype
class Artist(Audio):
    TYPE = 'artist'

    def _loadData(self, data):
        Audio._loadData(self, data)
        self.art = data.attrib.get('art', NA)
        self.guid = data.attrib.get('guid', NA)
        self.key = self.key.replace('/children', '')  # FIX_BUG_50
        self.location = utils.findLocations(data, single=True)
        if self.isFullObject():
            self.countries = [media.Country(self.server, e) for e in data if e.tag == media.Country.TYPE]
            self.genres = [media.Genre(self.server, e) for e in data if e.tag == media.Genre.TYPE]
            self.similar = [media.Similar(self.server, e) for e in data if e.tag == media.Similar.TYPE]

    def albums(self):
        path = '%s/children' % self.key
        return utils.listItems(self.server, path, Album.TYPE)

    def album(self, title):
        path = '%s/children' % self.key
        return utils.findItem(self.server, path, title)

    def tracks(self, watched=None):
        path = '%s/allLeaves' % self.key
        return utils.listItems(self.server, path, watched=watched)

    def track(self, title):
        path = '%s/allLeaves' % self.key
        return utils.findItem(self.server, path, title)

    def get(self, title):
        return self.track(title)


@utils.register_libtype
class Album(Audio):
    TYPE = 'album'

    def _loadData(self, data):
        Audio._loadData(self, data)
        self.art = data.attrib.get('art', NA)
        self.key = self.key.replace('/children', '')  # FIX_BUG_50
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.studio = data.attrib.get('studio', NA)
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            self.genres = [media.Genre(self.server, e) for e in data if e.tag == media.Genre.TYPE]

    def tracks(self, watched=None):
        path = '%s/children' % self.key
        return utils.listItems(self.server, path, watched=watched)

    def track(self, title):
        path = '%s/children' % self.key
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
class Track(Audio, Playable):
    TYPE = 'track'

    def _loadData(self, data):
        Audio._loadData(self, data)
        Playable._loadData(self, data)
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
            self.moods = [media.Mood(self.server, e) for e in data if e.tag == media.Mood.TYPE]
            self.media = [media.Media(self.server, e, self.initpath, self) for e in data if e.tag == media.Media.TYPE]
        # data for active sessions and history
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self.server, data)
        self.transcodeSession = utils.findTranscodeSession(self.server, data)

    @property
    def thumbUrl(self):
        return self.server.url(self.parentThumb)

    def album(self):
        return utils.listItems(self.server, self.parentKey)[0]

    def artist(self):
        return utils.listItems(self.server, self.grandparentKey)[0]
