# -*- coding: utf-8 -*-
"""Summary

Attributes:
    NA (TYPE): Description
"""

from plexapi import media, utils
from plexapi.utils import Playable, PlexPartialObject

NA = utils.NA


class Audio(PlexPartialObject):
    """Base class for audio.

    Attributes:
        addedAt (int): int from epoch, datetime.datetime
        index (sting): 1
        key (string): Fx /library/metadata/102631
        lastViewedAt (datetime.datetime): parse int into datetime.datetime.
        librarySectionID (int):
        listType (str): audio
        ratingKey (int): Unique key to identify this item
        summary (string): Summery of the artist, track, album
        thumb (string): Url to thumb image
        title (string): Fx Aerosmith
        titleSort (string): Defaults title if None
        TYPE (string):  overwritten by subclass
        type (string, NA): Description
        updatedAt (datatime.datetime): parse int to datetime.datetime
        viewCount (int): How many time has this item been played
    """
    TYPE = None

    def __init__(self, server, data, initpath):
        """Used to set the attributes

        Args:
            server (Plexserver): PMS your connected to
            data (Element): XML reponse from PMS as Element
                            normally built from server.query
            initpath (string): Fx /library/sections/7/all
        """
        super(Audio, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): XML reponse from PMS as Element
                            normally built from server.query
        """
        self.listType = 'audio'
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt', NA))
        self.index = data.attrib.get('index', NA)
        self.key = data.attrib.get('key', NA)
        self.lastViewedAt = utils.toDatetime(data.attrib.get('lastViewedAt', NA))
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.ratingKey = utils.cast(int, data.attrib.get('ratingKey', NA))
        self.summary = data.attrib.get('summary', NA)
        self.thumb = data.attrib.get('thumb', NA)
        self.title = data.attrib.get('title', NA)
        self.titleSort = data.attrib.get('titleSort', self.title)
        self.type = data.attrib.get('type', NA)
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt', NA))
        self.viewCount = utils.cast(int, data.attrib.get('viewCount', 0))

    @property
    def thumbUrl(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.server.url(self.thumb)

    def refresh(self):
        """Summary

        Returns:
            TYPE: Description
        """
        self.server.query('%s/refresh' % self.key, method=self.server.session.put)

    def section(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.server.library.sectionByID(self.librarySectionID)


@utils.register_libtype
class Artist(Audio):
    """Summary

    Attributes:
        art (string): /library/metadata/102631/art/1469310342
        countries (string): Description
        genres (list): Description
        guid (string): Fx guid com.plexapp.agents.plexmusic://gracenote/artist/05517B8701668D28?lang=en
        key (string): Fx /library/metadata/102631
        location (string): Filepath
        similar (list): Description
        TYPE (string): artist
    """

    TYPE = 'artist'

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): XML reponse from PMS as Element
                            normally built from server.query
        """
        Audio._loadData(self, data)
        self.art = data.attrib.get('art', NA)
        self.guid = data.attrib.get('guid', NA)
        self.key = self.key.replace('/children', '')  # FIX_BUG_50
        self.location = utils.findLocations(data, single=True)
        if self.isFullObject(): # check if this is needed
            self.countries = [media.Country(self.server, e) for e in data if e.tag == media.Country.TYPE]
            self.genres = [media.Genre(self.server, e) for e in data if e.tag == media.Genre.TYPE]
            self.similar = [media.Similar(self.server, e) for e in data if e.tag == media.Similar.TYPE]

    def albums(self):
        """Summary

        Returns:
            TYPE: Description
        """
        path = '%s/children' % self.key
        return utils.listItems(self.server, path, Album.TYPE)

    def album(self, title):
        """Summary

        Args:
            title (TYPE): Description

        Returns:
            TYPE: Description
        """
        path = '%s/children' % self.key
        return utils.findItem(self.server, path, title)

    def tracks(self, watched=None):
        """Summary

        Args:
            watched (None, optional): Description

        Returns:
            TYPE: Description
        """
        path = '%s/allLeaves' % self.key
        return utils.listItems(self.server, path, watched=watched)

    def track(self, title):
        """Summary

        Args:
            title (TYPE): Description

        Returns:
            TYPE: Description
        """
        path = '%s/allLeaves' % self.key
        return utils.findItem(self.server, path, title)

    def get(self, title):
        """Summary

        Args:
            title (TYPE): Description

        Returns:
            TYPE: Description
        """
        return self.track(title)


@utils.register_libtype
class Album(Audio):
    """Summary

    Attributes:
        art (TYPE): Description
        genres (TYPE): Description
        key (TYPE): Description
        originallyAvailableAt (TYPE): Description
        parentKey (TYPE): Description
        parentRatingKey (TYPE): Description
        parentThumb (TYPE): Description
        parentTitle (TYPE): Description
        studio (TYPE): Description
        TYPE (str): Description
        year (TYPE): Description
    """
    TYPE = 'album'

    def _loadData(self, data):
        """Summary

        Args:
            data (TYPE): Description

        Returns:
            TYPE: Description
        """
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
        """Summary

        Args:
            watched (None, optional): Description

        Returns:
            TYPE: Description
        """
        path = '%s/children' % self.key
        return utils.listItems(self.server, path, watched=watched)

    def track(self, title):
        """Summary

        Args:
            title (TYPE): Description

        Returns:
            TYPE: Description
        """
        path = '%s/children' % self.key
        return utils.findItem(self.server, path, title)

    def get(self, title):
        """Summary

        Args:
            title (TYPE): Description

        Returns:
            TYPE: Description
        """
        return self.track(title)

    def artist(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return utils.listItems(self.server, self.parentKey)[0]

    def watched(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.tracks(watched=True)

    def unwatched(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.tracks(watched=False)


@utils.register_libtype
class Track(Audio, Playable):
    """Summary

    Attributes:
        art (TYPE): Description
        chapterSource (TYPE): Description
        duration (TYPE): Description
        grandparentArt (TYPE): Description
        grandparentKey (TYPE): Description
        grandparentRatingKey (TYPE): Description
        grandparentThumb (TYPE): Description
        grandparentTitle (TYPE): Description
        guid (TYPE): Description
        media (TYPE): Description
        moods (TYPE): Description
        originalTitle (TYPE): Description
        parentIndex (TYPE): Description
        parentKey (TYPE): Description
        parentRatingKey (TYPE): Description
        parentThumb (TYPE): Description
        parentTitle (TYPE): Description
        player (TYPE): Description
        primaryExtraKey (TYPE): Description
        ratingCount (TYPE): Description
        sessionKey (TYPE): Description
        transcodeSession (TYPE): Description
        TYPE (str): Description
        username (TYPE): Description
        viewOffset (TYPE): Description
        year (TYPE): Description
    """
    TYPE = 'track'

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): Usually built from server.query
        """
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
        if self.isFullObject(): # check me
            self.moods = [media.Mood(self.server, e) for e in data if e.tag == media.Mood.TYPE]
            self.media = [media.Media(self.server, e, self.initpath, self) for e in data if e.tag == media.Media.TYPE]
        # data for active sessions and history
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self.server, data)
        self.transcodeSession = utils.findTranscodeSession(self.server, data)

    @property
    def thumbUrl(self):
        """Return url to thumb image."""
        return self.server.url(self.parentThumb)

    def album(self):
        """Return this track's Album"""
        return utils.listItems(self.server, self.parentKey)[0]

    def artist(self):
        """Return this track's Artist"""
        return utils.listItems(self.server, self.grandparentKey)[0]
