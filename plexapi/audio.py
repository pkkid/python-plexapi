# -*- coding: utf-8 -*-
from plexapi import media, utils
from plexapi.base import Playable, PlexPartialObject


class Audio(PlexPartialObject):
    """ Base class for audio :class:`~plexapi.audio.Artist`, :class:`~plexapi.audio.Album`
        and :class:`~plexapi.audio.Track` objects.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).

        Attributes:
            addedAt (datetime): Datetime this item was added to the library.
            index (sting): Index Number (often the track number).
            key (str): API URL (/library/metadata/<ratingkey>).
            lastViewedAt (datetime): Datetime item was last accessed.
            librarySectionID (int): :class:`~plexapi.library.LibrarySection` ID.
            listType (str): Hardcoded as 'audio' (useful for search filters).
            ratingKey (int): Unique key identifying this item.
            summary (str): Summary of the artist, track, or album.
            thumb (str): URL to thumbnail image.
            title (str): Artist, Album or Track title. (Jason Mraz, We Sing, Lucky, etc.)
            titleSort (str): Title to use when sorting (defaults to title).
            type (str): 'artist', 'album', or 'track'.
            updatedAt (datatime): Datetime this item was updated.
            viewCount (int): Count of times this item was accessed.
    """
    TYPE = None

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self._data = data
        self.listType = 'audio'
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt'))
        self.index = data.attrib.get('index')
        self.key = data.attrib.get('key')
        self.lastViewedAt = utils.toDatetime(data.attrib.get('lastViewedAt'))
        self.librarySectionID = data.attrib.get('librarySectionID')
        self.ratingKey = utils.cast(int, data.attrib.get('ratingKey'))
        self.summary = data.attrib.get('summary')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.titleSort = data.attrib.get('titleSort', self.title)
        self.type = data.attrib.get('type')
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt'))
        self.viewCount = utils.cast(int, data.attrib.get('viewCount', 0))

    @property
    def thumbUrl(self):
        """ Returns the URL to this items thumbnail image. """
        if self.thumb:
            return self._server.url(self.thumb)

    def refresh(self):
        """ Tells Plex to refresh the metadata for this and all subitems. """
        self._server.query('%s/refresh' % self.key, method=self._server.session.put)

    def section(self):
        """ Returns the :class:`~plexapi.library.LibrarySection` this item belongs to. """
        return self._server.library.sectionByID(self.librarySectionID)


@utils.register_libtype
class Artist(Audio):
    """ Represents a single audio artist.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).

        Attributes:
            art (str): Artist artwork (/library/metadata/<ratingkey>/art/<artid>)
            countries (list): List of :class:`~plexapi.media.Country` objects this artist respresents.
            genres (list): List of :class:`~plexapi.media.Genre` objects this artist respresents.
            guid (str): Unknown (unique ID; com.plexapp.agents.plexmusic://gracenote/artist/05517B8701668D28?lang=en)
            key (str): API URL (/library/metadata/<ratingkey>).
            location (str): Filepath this artist is found on disk.
            similar (list): List of :class:`~plexapi.media.Similar` artists.
    """
    TYPE = 'artist'

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        Audio._loadData(self, data)
        self.art = data.attrib.get('art')
        self.guid = data.attrib.get('guid')
        self.key = self.key.replace('/children', '')  # FIX_BUG_50
        self.location = utils.findLocations(data, single=True)
        self.countries = self._buildItems(data, media.Country, bytag=True)
        self.genres = self._buildItems(data, media.Genre, bytag=True)
        self.similar = self._buildItems(data, media.Similar, bytag=True)

    def album(self, title):
        """ Returns the :class:`~plexapi.audio.Album` that matches the specified title.

            Parameters:
                title (str): Title of the album to return.
        """
        key = '%s/children' % self.key
        return self.fetchItem(key, title__iexact=title)

    def albums(self, **kwargs):
        """ Returns a list of :class:`~plexapi.audio.Album` objects by this artist. """
        key = '%s/children' % self.key
        return self.fetchItems(key, **kwargs)

    def track(self, title):
        """ Returns the :class:`~plexapi.audio.Track` that matches the specified title.

            Parameters:
                title (str): Title of the track to return.
        """
        key = '%s/allLeaves' % self.key
        return self.fetchItem(key, title__iexact=title)

    def tracks(self, **kwargs):
        """ Returns a list of :class:`~plexapi.audio.Track` objects by this artist. """
        key = '%s/allLeaves' % self.key
        return self.fetchItems(key, **kwargs)

    def get(self, title):
        """ Alias of :func:`~plexapi.audio.Artist.track`. """
        return self.track(title)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        """ Downloads all tracks for this artist to the specified location.
            
            Parameters:
                savepath (str): Title of the track to return.
                keep_orginal_name (bool): Set True to keep the original filename as stored in
                    the Plex server. False will create a new filename with the format
                    "<Atrist> - <Album> <Track>".
                kwargs (dict): If specified, a :func:`~plexapi.audio.Track.getStreamURL()` will
                    be returned and the additional arguments passed in will be sent to that
                    function. If kwargs is not specified, the media items will be downloaded
                    and saved to disk.
        """
        filepaths = []
        for album in self.albums():
            for track in album.tracks():
                filepaths += track.download(savepath, keep_orginal_name, **kwargs)
        return filepaths


@utils.register_libtype
class Album(Audio):
    """ Represents a single audio album.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).

        Attributes:
            art (str): Album artwork (/library/metadata/<ratingkey>/art/<artid>)
            genres (list): List of :class:`~plexapi.media.Genre` objects this album respresents.
            key (str): API URL (/library/metadata/<ratingkey>).
            originallyAvailableAt (datetime): Datetime this album was released.
            parentKey (str): API URL of this artist.
            parentRatingKey (int): Unique key identifying artist.
            parentThumb (str): URL to artist thumbnail image.
            parentTitle (str): Name of the artist for this album.
            studio (str): Studio that released this album.
            year (int): Year this album was released.
    """
    TYPE = 'album'

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        Audio._loadData(self, data)
        self.art = data.attrib.get('art')
        self.key = self.key.replace('/children', '')  # fixes bug #50
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt'), '%Y-%m-%d')
        self.parentKey = data.attrib.get('parentKey')
        self.parentRatingKey = data.attrib.get('parentRatingKey')
        self.parentThumb = data.attrib.get('parentThumb')
        self.parentTitle = data.attrib.get('parentTitle')
        self.studio = data.attrib.get('studio')
        self.year = utils.cast(int, data.attrib.get('year'))
        self.genres = self._buildItems(data, media.Genre, bytag=True)

    def track(self, title):
        """ Returns the :class:`~plexapi.audio.Track` that matches the specified title.

            Parameters:
                title (str): Title of the track to return.
        """
        key = '%s/children' % self.key
        return self.fetchItem(key, title__iexact=title)

    def tracks(self, **kwargs):
        """ Returns a list of :class:`~plexapi.audio.Track` objects in this album. """
        key = '%s/children' % self.key
        return self.fetchItems(key, **kwargs)

    def get(self, title):
        """ Alias of :func:`~plexapi.audio.Album.track`. """
        return self.track(title)

    def artist(self):
        """ Return :func:`~plexapi.audio.Artist` of this album. """
        return self.fetchItem(self.parentKey)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        """ Downloads all tracks for this artist to the specified location.
            
            Parameters:
                savepath (str): Title of the track to return.
                keep_orginal_name (bool): Set True to keep the original filename as stored in
                    the Plex server. False will create a new filename with the format
                    "<Atrist> - <Album> <Track>".
                kwargs (dict): If specified, a :func:`~plexapi.audio.Track.getStreamURL()` will
                    be returned and the additional arguments passed in will be sent to that
                    function. If kwargs is not specified, the media items will be downloaded
                    and saved to disk.
        """
        filepaths = []
        for track in self.tracks():
            filepaths += track.download(savepath, keep_orginal_name, **kwargs)
        return filepaths


@utils.register_libtype
class Track(Audio, Playable):
    """ Represents a single audio track.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): XML response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).

        Attributes:
            art (str): Track artwork (/library/metadata/<ratingkey>/art/<artid>)
            chapterSource (TYPE): Unknown
            duration (int): Length of this album in seconds.
            grandparentArt (str): Artist artowrk.
            grandparentKey (str): Artist API URL.
            grandparentRatingKey (str): Unique key identifying artist.
            grandparentThumb (str): URL to artist thumbnail image.
            grandparentTitle (str): Name of the artist for this track.
            guid (str): Unknown (unique ID).
            media (list): List of :class:`~plexapi.media.Media` objects for this track.
            moods (list): List of :class:`~plexapi.media.Mood` objects for this track.
            originalTitle (str): Original track title (if translated).
            parentIndex (int): Album index.
            parentKey (str): Album API URL.
            parentRatingKey (int): Unique key identifying album.
            parentThumb (str): URL to album thumbnail image.
            parentTitle (str): Name of the album for this track.
            primaryExtraKey (str): Unknown
            ratingCount (int): Rating of this track (1-10?)
            viewOffset (int): Unknown
            year (int): Year this track was released.
            sessionKey (int): Session Key (active sessions only).
            username (str): Username of person playing this track (active sessions only).
            player (str): :class:`~plexapi.client.PlexClient` for playing track (active sessions only).
            transcodeSession (None): :class:`~plexapi.media.TranscodeSession` for playing
                track (active sessions only).
    """
    TYPE = 'track'

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        Audio._loadData(self, data)
        Playable._loadData(self, data)
        self.art = data.attrib.get('art')
        self.chapterSource = data.attrib.get('chapterSource')
        self.duration = utils.cast(int, data.attrib.get('duration'))
        self.grandparentArt = data.attrib.get('grandparentArt')
        self.grandparentKey = data.attrib.get('grandparentKey')
        self.grandparentRatingKey = data.attrib.get('grandparentRatingKey')
        self.grandparentThumb = data.attrib.get('grandparentThumb')
        self.grandparentTitle = data.attrib.get('grandparentTitle')
        self.guid = data.attrib.get('guid')
        self.originalTitle = data.attrib.get('originalTitle')
        self.parentIndex = data.attrib.get('parentIndex')
        self.parentKey = data.attrib.get('parentKey')
        self.parentRatingKey = data.attrib.get('parentRatingKey')
        self.parentThumb = data.attrib.get('parentThumb')
        self.parentTitle = data.attrib.get('parentTitle')
        self.primaryExtraKey = data.attrib.get('primaryExtraKey')
        self.ratingCount = utils.cast(int, data.attrib.get('ratingCount'))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year'))
        self.media = self._buildItems(data, media.Media, bytag=True)
        self.moods = self._buildItems(data, media.Mood, bytag=True)
        # data for active sessions and history
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey'))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self._server, data)
        self.transcodeSession = utils.findTranscodeSession(self._server, data)

    def _prettyfilename(self):
        """ Returns a filename for use in download. """
        return '%s - %s %s' % (self.grandparentTitle, self.parentTitle, self.title)

    @property
    def thumbUrl(self):
        """ Returns the URL thumbnail image for this track's album. """
        if self.parentThumb:
            return self._server.url(self.parentThumb)

    def album(self):
        """ Return this track's :class:`~plexapi.audio.Album`. """
        return self.fetchItems(self.parentKey)[0]

    def artist(self):
        """ Return this track's :class:`~plexapi.audio.Artist`. """
        return self.fetchItems(self.grandparentKey)[0]
