# -*- coding: utf-8 -*-

from plexapi import media, utils
from plexapi.utils import Playable, PlexPartialObject

NA = utils.NA


class Audio(PlexPartialObject):
    """Base class for audio.

    Attributes:
        addedAt (int): int from epoch, datetime.datetime
        index (sting): 1
        key (str): Fx /library/metadata/102631
        lastViewedAt (datetime.datetime): parse int into datetime.datetime.
        librarySectionID (int):
        listType (str): audio
        ratingKey (int): Unique key to identify this item
        summary (str): Summery of the artist, track, album
        thumb (str): Url to thumb image
        title (str): Fx Aerosmith
        titleSort (str): Defaults title if None
        TYPE (str):  overwritten by subclass
        type (string, NA): Description
        updatedAt (datatime.datetime): parse int to datetime.datetime
        viewCount (int): How many time has this item been played
    """
    TYPE = None

    def __init__(self, server, data, initpath):
        """Used to set the attributes.

        Args:
            server (Plexserver): PMS your connected to
            data (Element): XML reponse from PMS as Element
                            normally built from server.query
            initpath (str): Fx /library/sections/7/all
        """
        super(Audio, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """Used to set the attributes.

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
        """Return url to thumb image."""
        if self.thumb:
            return self.server.url(self.thumb)

    def refresh(self):
        """Refresh the metadata."""
        self.server.query('%s/refresh' % self.key, method=self.server.session.put)

    def section(self):
        """Library section."""
        return self.server.library.sectionByID(self.librarySectionID)


@utils.register_libtype
class Artist(Audio):
    """Artist.

    Attributes:
        art (str): /library/metadata/102631/art/1469310342
        countries (list): List of media.County fx [<Country:24200:United.States>]
        genres (list): List of media.Genre fx [<Genre:25555:Classic.Rock>]
        guid (str): Fx guid com.plexapp.agents.plexmusic://gracenote/artist/05517B8701668D28?lang=en
        key (str): Fx /library/metadata/102631
        location (str): Filepath
        similar (list): List of media.Similar fx [<Similar:25220:Guns.N'.Roses>]
        TYPE (str): artist
    """

    TYPE = 'artist'

    def _loadData(self, data):
        """Used to set the attributes.

        Args:
            data (Element): XML reponse from PMS as Element
                            normally built from server.query
        """
        Audio._loadData(self, data)
        self.art = data.attrib.get('art', NA)
        self.guid = data.attrib.get('guid', NA)
        self.key = self.key.replace('/children', '')  # FIX_BUG_50
        self.location = utils.findLocations(data, single=True)
        if self.isFullObject():  # check if this is needed
            self.countries = [media.Country(self.server, e)
                              for e in data if e.tag == media.Country.TYPE]
            self.genres = [media.Genre(self.server, e)
                           for e in data if e.tag == media.Genre.TYPE]
            self.similar = [media.Similar(self.server, e)
                            for e in data if e.tag == media.Similar.TYPE]

    def albums(self):
        """Return a list of Albums by thus artist."""
        path = '%s/children' % self.key
        return utils.listItems(self.server, path, Album.TYPE)

    def album(self, title):
        """Return a album from this artist that match title."""
        path = '%s/children' % self.key
        return utils.findItem(self.server, path, title)

    def tracks(self, watched=None):
        """Return all tracks to this artist.

        Args:
            watched(None, False, True): Default to None.

        Returns:
            List: of Track
        """
        path = '%s/allLeaves' % self.key
        return utils.listItems(self.server, path, watched=watched)

    def track(self, title):
        """Return a Track that matches title.

        Args:
            title (str): Fx song name

        Returns:
            Track:
        """
        path = '%s/allLeaves' % self.key
        return utils.findItem(self.server, path, title)

    def get(self, title):
        """Alias. See track."""
        return self.track(title)


@utils.register_libtype
class Album(Audio):
    """Album.

    Attributes:
        art (str): Fx /library/metadata/102631/art/1469310342
        genres (list): List of media.Genre
        key (str): Fx /library/metadata/102632
        originallyAvailableAt (TYPE): Description
        parentKey (str): /library/metadata/102631
        parentRatingKey (int): Fx 1337
        parentThumb (TYPE): Relative url to parent thumb image
        parentTitle (str): Aerosmith
        studio (str):
        TYPE (str): album
        year (int): 1999
    """

    TYPE = 'album'

    def _loadData(self, data):
        """Used to set the attributes.

        Args:
            data (Element): XML reponse from PMS as Element
                            normally built from server.query
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
        """Return all tracks to this album.

        Args:
            watched(None, False, True): Default to None.

        Returns:
            List: of Track
        """
        path = '%s/children' % self.key
        return utils.listItems(self.server, path, watched=watched)

    def track(self, title):
        """Return a Track that matches title.

        Args:
            title (str): Fx song name

        Returns:
            Track:
        """
        path = '%s/children' % self.key
        return utils.findItem(self.server, path, title)

    def get(self, title):
        """Alias. See track."""
        return self.track(title)

    def artist(self):
        """Return Artist of this album."""
        return utils.listItems(self.server, self.parentKey)[0]

    def watched(self):
        """Return Track that is lisson on."""
        return self.tracks(watched=True)

    def unwatched(self):
        """Return Track that is not lisson on."""
        return self.tracks(watched=False)


@utils.register_libtype
class Track(Audio, Playable):
    """Track.

    Attributes:
        art (str): Relative path fx /library/metadata/102631/art/1469310342
        chapterSource (TYPE): Description
        duration (TYPE): Description
        grandparentArt (str): Relative path
        grandparentKey (str): Relative path Fx /library/metadata/102631
        grandparentRatingKey (TYPE): Description
        grandparentThumb (str): Relative path to Artist thumb img
        grandparentTitle (str): Aerosmith
        guid (TYPE): Description
        media (list): List of media.Media
        moods (list): List of media.Moods
        originalTitle (str): Some track title
        parentIndex (int): 1
        parentKey (str): Relative path Fx /library/metadata/102632
        parentRatingKey (int): 1337
        parentThumb (str): Relative path to Album thumb
        parentTitle (str): Album title
        player (None): #TODO
        primaryExtraKey (TYPE): #TODO
        ratingCount (int): 10
        sessionKey (int): Description
        transcodeSession (None):
        TYPE (str): track
        username (str): username@mail.com
        viewOffset (int): 100
        year (int): 1999
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
        if self.isFullObject():  # check me
            self.moods = [media.Mood(self.server, e)
                          for e in data if e.tag == media.Mood.TYPE]
            self.media = [media.Media(self.server, e, self.initpath, self)
                          for e in data if e.tag == media.Media.TYPE]
        # data for active sessions and history
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self.server, data)
        self.transcodeSession = utils.findTranscodeSession(self.server, data)

    @property
    def thumbUrl(self):
        """Return url to thumb image."""
        if self.parentThumb:
            return self.server.url(self.parentThumb)

    def album(self):
        """Return this track's Album."""
        return utils.listItems(self.server, self.parentKey)[0]

    def artist(self):
        """Return this track's Artist."""
        return utils.listItems(self.server, self.grandparentKey)[0]
