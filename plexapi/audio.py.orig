# -*- coding: utf-8 -*-
from plexapi import media, utils
from plexapi.utils import Playable, PlexPartialObject

NA = utils.NA


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

    def __init__(self, server, data, initpath):
        super(Audio, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
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
        """ Returns the URL to this items thumbnail image. """
        if self.thumb:
            return self.server.url(self.thumb)

    def refresh(self):
        """ Tells Plex to refresh the metadata for this and all subitems. """
        self.server.query('%s/refresh' % self.key, method=self.server.session.put)

    def section(self):
        """ Returns the :class:`~plexapi.library.LibrarySection` this item belongs to. """
        return self.server.library.sectionByID(self.librarySectionID)


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
        self.art = data.attrib.get('art', NA)
        self.guid = data.attrib.get('guid', NA)
        self.key = self.key.replace('/children', '')  # FIX_BUG_50
        self.location = utils.findLocations(data, single=True)
        if self.isFullObject():  # check if this is needed
            self.countries = [media.Country(self.server, e) for e in data if e.tag == media.Country.TYPE]
            self.genres = [media.Genre(self.server, e) for e in data if e.tag == media.Genre.TYPE]
            self.similar = [media.Similar(self.server, e) for e in data if e.tag == media.Similar.TYPE]

    def albums(self):
        """ Returns a list of :class:`~plexapi.audio.Album` objects by this artist. """
        path = '%s/children' % self.key
        return utils.listItems(self.server, path, Album.TYPE)

    def album(self, title):
        """ Returns the :class:`~plexapi.audio.Album` that matches the specified title.

            Parameters:
                title (str): Title of the album to return.
        """
        path = '%s/children' % self.key
        return utils.findItem(self.server, path, title)

    def tracks(self):
        """ Returns a list of :class:`~plexapi.audio.Track` objects by this artist. """
        path = '%s/allLeaves' % self.key
        return utils.listItems(self.server, path)

    def track(self, title):
        """ Returns the :class:`~plexapi.audio.Track` that matches the specified title.

            Parameters:
                title (str): Title of the track to return.
        """
        path = '%s/allLeaves' % self.key
        return utils.findItem(self.server, path, title)

    def get(self, title):
        """ Alias of :func:`~plexapi.audio.Artist.track`. """
        return self.track(title)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        downloaded = []
        for album in self.albums():
            for track in album.tracks():
                dl = track.download(savepath=savepath, keep_orginal_name=keep_orginal_name, **kwargs)
                if dl:
                    downloaded.extend(dl)

        return downloaded


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
        self.art = data.attrib.get('art', NA)
        self.key = self.key.replace('/children', '')  # fixes bug #50
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.studio = data.attrib.get('studio', NA)
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            self.genres = [media.Genre(self.server, e) for e in data if e.tag == media.Genre.TYPE]

    def tracks(self):
        """ Returns a list of :class:`~plexapi.audio.Track` objects in this album. """
        path = '%s/children' % self.key
        return utils.listItems(self.server, path)

    def track(self, title):
        """ Returns the :class:`~plexapi.audio.Track` that matches the specified title.

            Parameters:
                title (str): Title of the track to return.
        """
        path = '%s/children' % self.key
        return utils.findItem(self.server, path, title)

    def get(self, title):
        """ Alias of :func:`~plexapi.audio.Album.track`. """
        return self.track(title)

    def artist(self):
        """ Return :func:`~plexapi.audio.Artist` of this album. """
        return utils.listItems(self.server, self.parentKey)[0]

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        downloaded = []
        for ep in self.tracks():
            dl = ep.download(savepath=savepath, keep_orginal_name=keep_orginal_name, **kwargs)
            if dl:
                downloaded.extend(dl)

        return downloaded


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
        # media is included in /children
        self.media = [media.Media(self.server, e, self.initpath, self)
                      for e in data if e.tag == media.Media.TYPE]
        if self.isFullObject():  # check me
            self.moods = [media.Mood(self.server, e) for e in data if e.tag == media.Mood.TYPE]
            self.media = [media.Media(self.server, e, self.initpath, self) for e in data if e.tag == media.Media.TYPE]

            #self.media = [media.Media(self.server, e, self.initpath, self)
            #              for e in data if e.tag == media.Media.TYPE]
        # data for active sessions and history
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self.server, data)
        self.transcodeSession = utils.findTranscodeSession(self.server, data)

    @property
    def thumbUrl(self):
        """ Returns the URL thumbnail image for this track's album. """
        if self.parentThumb:
            return self.server.url(self.parentThumb)

    def album(self):
        """ Return this track's :class:`~plexapi.audio.Album`. """
        return utils.listItems(self.server, self.parentKey)[0]

    def artist(self):
        """ Return this track's :class:`~plexapi.audio.Artist`. """
        return utils.listItems(self.server, self.grandparentKey)[0]

    def _prettyfilename(self):
        return '%s - %s %s' % (self.grandparentTitle, self.parentTitle, self.title)

    '''
    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        """Download a episode. If kwargs are passed your can download a trancoded file.

           Args:
                savepath (str): Abs path to savefolder
                keep_orginal_name (bool): Use the mediafiles orginal name

           kwargs:
                See getStreamURL docs.

        """
        downloaded = []
        locs = [i for i in self.iterParts() if i]
        for loc in locs:
            if keep_orginal_name is False:
                name = '%s.%s' % (self._prettyfilename(), loc.container)
            else:
                name = loc.file

            # So this seems to be a alot slower but allows transcode.
            if kwargs:
                download_url = self.getStreamURL(**kwargs)
            else:
                download_url = self.server.url('%s?download=1' % loc.key)

            dl = utils.download(download_url, filename=name, savepath=savepath, session=self.server.session)
            if dl:
                downloaded.append(dl)

        return downloaded
    '''
