# -*- coding: utf-8 -*-
from plexapi import media, utils
from plexapi.exceptions import BadRequest, NotFound
from plexapi.base import Playable, PlexPartialObject


class Video(PlexPartialObject):
    """ Base class for all video objects including :class:`~plexapi.video.Movie`, 
        :class:`~plexapi.video.Show`, :class:`~plexapi.video.Season`,
        :class:`~plexapi.video.Episode`.

        Attributes:
            addedAt (datetime): Datetime this item was added to the library.
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
    def _loadData(self, data):
        self._data = data
        self.listType = 'video'
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt'))
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
        """ Return url to for the thumbnail image. """
        if self.thumb:
            return self._server.url(self.thumb)

    def markWatched(self):
        """ Mark video as watched. """
        key = '/:/scrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self._server.query(key)
        self.reload()

    def markUnwatched(self):
        """ Mark video unwatched. """
        key = '/:/unscrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self._server.query(key)
        self.reload()


@utils.registerPlexObject
class Movie(Video, Playable):
    """ Represents a single Movie.
        
        Attributes:
            art (str): Key to movie artwork (/library/metadata/<ratingkey>/art/<artid>)
            audienceRating (float): Audience rating (usually from Rotten Tomatoes).
            audienceRatingImage (str): Key to audience rating image (rottentomatoes://image.rating.spilled)
            chapterSource (str): Chapter source (agent; media; mixed).
            contentRating (str) Content rating (PG-13; NR; TV-G).
            duration (int): Duration of movie in milliseconds.
            guid: Plex GUID (com.plexapp.agents.imdb://tt4302938?lang=en).
            originalTitle (str): Original title, often the foreign title (転々; 엽기적인 그녀).
            originallyAvailableAt (datetime): Datetime movie was released.
            primaryExtraKey (str) Primary extra key (/library/metadata/66351).
            rating (float): Movie rating (7.9; 9.8; 8.1).
            ratingImage (str): Key to rating image (rottentomatoes://image.rating.rotten).
            studio (str): Studio that created movie (Di Bonaventura Pictures; 21 Laps Entertainment).
            tagline (str): Movie tag line (Back 2 Work; Who says men can't change?).
            userRating (float): User rating (2.0; 8.0).
            viewOffset (int): View offset in milliseconds.
            year (int): Year movie was released.
            
            # TODO: Finish documenting plexapi.video.Movie
    """
    TAG = 'Video'
    TYPE = 'movie'

    def _loadData(self, data):
        Video._loadData(self, data)
        Playable._loadData(self, data)
        self.art = data.attrib.get('art')
        self.audienceRating = utils.cast(float, data.attrib.get('audienceRating'))
        self.audienceRatingImage = data.attrib.get('audienceRatingImage')
        self.chapterSource = data.attrib.get('chapterSource')
        self.contentRating = data.attrib.get('contentRating')
        self.duration = utils.cast(int, data.attrib.get('duration'))
        self.guid = data.attrib.get('guid')
        self.originalTitle = data.attrib.get('originalTitle')
        self.originallyAvailableAt = utils.toDatetime(
            data.attrib.get('originallyAvailableAt'), '%Y-%m-%d')
        self.primaryExtraKey = data.attrib.get('primaryExtraKey')
        self.rating = data.attrib.get('rating')
        self.ratingImage = data.attrib.get('ratingImage')
        self.studio = data.attrib.get('studio')
        self.tagline = data.attrib.get('tagline')
        self.userRating = utils.cast(float, data.attrib.get('userRating'))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year'))
        self.collections = self.findItems(data, media.Collection)
        self.countries = self.findItems(data, media.Country)
        self.directors = self.findItems(data, media.Director)
        self.fields = self.findItems(data, media.Field)
        self.genres = self.findItems(data, media.Genre)
        self.media = self.findItems(data, media.Media)
        self.producers = self.findItems(data, media.Producer)
        self.roles = self.findItems(data, media.Role)
        self.writers = self.findItems(data, media.Writer)

    @property
    def actors(self):
        return self.roles

    @property
    def isWatched(self):
        return bool(self.viewCount > 0)

    @property
    def location(self):
        """ This does not exist in plex xml response but is added to have a common
            interface to get the location of the Movie/Show/Episode
        """
        files = [i.file for i in self.iterParts() if i]
        if len(files) == 1:
            files = files[0]
        return files

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        downloaded = []
        locs = [i for i in self.iterParts() if i]
        for loc in locs:
            if keep_orginal_name is False:
                name = '%s.%s' % (self.title.replace(' ', '.'), loc.container)
            else:
                name = loc.file
            # So this seems to be a alot slower but allows transcode.
            if kwargs:
                download_url = self.getStreamURL(**kwargs)
            else:
                download_url = self._server.url('%s?download=1' % loc.key)
            dl = utils.download(download_url, filename=name, savepath=savepath, session=self._server._session)
            if dl:
                downloaded.append(dl)
        return downloaded


@utils.registerPlexObject
class Show(Video):
    TAG = 'Directory'
    TYPE = 'show'

    def _loadData(self, data):
        Video._loadData(self, data)
        # fix the key if this was loaded from search..
        self.key = self.key.replace('/children', '')
        self.art = data.attrib.get('art')
        self.banner = data.attrib.get('banner')
        self.childCount = utils.cast(int, data.attrib.get('childCount'))
        self.contentRating = data.attrib.get('contentRating')
        self.duration = utils.cast(int, data.attrib.get('duration'))
        self.guid = data.attrib.get('guid')
        self.index = data.attrib.get('index')
        self.leafCount = utils.cast(int, data.attrib.get('leafCount'))
        self.locations = self.listAttrs(data, 'path', etag='Location')
        self.originallyAvailableAt = utils.toDatetime(
            data.attrib.get('originallyAvailableAt'), '%Y-%m-%d')
        self.rating = utils.cast(float, data.attrib.get('rating'))
        self.studio = data.attrib.get('studio')
        self.theme = data.attrib.get('theme')
        self.viewedLeafCount = utils.cast(int, data.attrib.get('viewedLeafCount'))
        self.year = utils.cast(int, data.attrib.get('year'))
        self.genres = self.findItems(data, media.Genre)
        self.roles = self.findItems(data, media.Role)

    @property
    def actors(self):
        return self.roles

    @property
    def isWatched(self):
        return bool(self.viewedLeafCount == self.leafCount)

    def seasons(self, **kwargs):
        """Returns a list of Season."""
        key = '/library/metadata/%s/children' % self.ratingKey
        return self.fetchItems(key, **kwargs)

    def season(self, title=None):
        """ Returns the season with the specified title or number.

            Parameters:
                title (str or int): Title or Number of the season to return.
        """
        if isinstance(title, int):
            title = 'Season %s' % title
        key = '/library/metadata/%s/children' % self.ratingKey
        return self.fetchItem(key, etag='Directory', title__iexact=title)

    def episodes(self, **kwargs):
        """ Returs a list of Episode """
        key = '/library/metadata/%s/allLeaves' % self.ratingKey
        return self.fetchItems(key, **kwargs)

    def episode(self, title=None, season=None, episode=None):
        """Find a episode using a title or season and episode.

           Note:
                Both season and episode is required if title is missing.

           Args:
                title (str): Default None
                season (int): Season number, default None
                episode (int): Episode number, default None

           Raises:
                ValueError: If season and episode is missing.
                NotFound: If the episode is missing.

           Returns:
                Episode

           Examples:
                >>> plex.search('The blacklist')[0].episode(season=1, episode=1)
                <Episode:116263:The.Freelancer>
                >>> plex.search('The blacklist')[0].episode('The Freelancer')
                <Episode:116263:The.Freelancer>
        """
        if title:
            key = '/library/metadata/%s/allLeaves' % self.ratingKey
            return self.fetchItem(key, title__iexact=title)
        elif season and episode:
            results = [i for i in self.episodes() if i.seasonNumber == season and i.index == episode]
            if results:
                return results[0]
            raise NotFound('Couldnt find %s S%s E%s' % (self.title, season, episode))
        raise TypeError('Missing argument: title or season and episode are required')

    def watched(self):
        """Return a list of watched episodes"""
        return self.episodes(viewCount__gt=0)

    def unwatched(self):
        """Return a list of unwatched episodes"""
        return self.episodes(viewCount=0)

    def get(self, title):
        """Get a Episode with a title.

           Args:
                title (str): fx Secret santa
        """
        return self.episode(title)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        downloaded = []
        for ep in self.episodes():
            dl = ep.download(savepath=savepath, keep_orginal_name=keep_orginal_name, **kwargs)
            if dl:
                downloaded.extend(dl)
        return downloaded


@utils.registerPlexObject
class Season(Video):
    TAG = 'Directory'
    TYPE = 'season'

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): Usually built from server.query
        """
        Video._loadData(self, data)
        self.key = self.key.replace('/children', '')
        self.leafCount = utils.cast(int, data.attrib.get('leafCount'))
        self.index = utils.cast(int, data.attrib.get('index'))
        self.parentKey = data.attrib.get('parentKey')
        self.parentRatingKey = utils.cast(int, data.attrib.get('parentRatingKey'))
        self.parentTitle = data.attrib.get('parentTitle')
        self.viewedLeafCount = utils.cast(int, data.attrib.get('viewedLeafCount'))

    def __repr__(self):
        return '<%s>' % ':'.join([p for p in [
            self.__class__.__name__,
            self.key.replace('/library/metadata/', '').replace('/children', ''),
            '%s-s%s' % (self.parentTitle.replace(' ','-')[:20], self.seasonNumber),
        ] if p])

    @property
    def isWatched(self):
        return bool(self.viewedLeafCount == self.leafCount)

    @property
    def seasonNumber(self):
        """Returns season number."""
        return self.index

    def episodes(self, **kwargs):
        """ Returs a list of Episode. """
        key = '/library/metadata/%s/children' % self.ratingKey
        return self.fetchItems(key, **kwargs)

    def episode(self, title=None, num=None):
        """ Returns the episode with the given title or number.

           Parameters:
                title (str): Title of the episode to return.
                num (int): Number of the episode to return (if title not specified).

           Raises:
                TypeError: If title and episode is missing.
                NotFound: If that episode cant be found.

           Examples:
                >>> plex.search('The blacklist').season(1).episode(episode=1)
                <Episode:116263:The.Freelancer>
                >>> plex.search('The blacklist').season(1).episode('The Freelancer')
                <Episode:116263:The.Freelancer>

        """
        if not title and not num:
            raise BadRequest('Missing argument, you need to use title or episode.')
        
        key = '/library/metadata/%s/children' % self.ratingKey
        if title:
            return self.fetchItem(key, title=title)
        return self.fetchItem(key, seasonNumber=self.index, index=num)

    def get(self, title):
        """ Alias for self.episode. """
        return self.episode(title)

    def show(self):
        """Return this seasons show."""
        return self.fetchItem(self.parentKey)

    def watched(self):
        """Returns a list of watched Episode"""
        return self.episodes(watched=True)

    def unwatched(self):
        """Returns a list of unwatched Episode"""
        return self.episodes(watched=False)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        downloaded = []
        for ep in self.episodes():
            dl = ep.download(savepath=savepath, keep_orginal_name=keep_orginal_name, **kwargs)
            if dl:
                downloaded.extend(dl)
        return downloaded


@utils.registerPlexObject
class Episode(Video, Playable):
    TAG = 'Video'
    TYPE = 'episode'

    def _loadData(self, data):
        """Used to set the attributes

            Args:
                data (Element): Usually built from server.query
        """
        Video._loadData(self, data)
        Playable._loadData(self, data)
        self._seasonNumber = None  # cached season number
        self.art = data.attrib.get('art')
        self.chapterSource = data.attrib.get('chapterSource')
        self.contentRating = data.attrib.get('contentRating')
        self.duration = utils.cast(int, data.attrib.get('duration'))
        self.grandparentArt = data.attrib.get('grandparentArt')
        self.grandparentKey = data.attrib.get('grandparentKey')
        self.grandparentRatingKey = utils.cast(int, data.attrib.get('grandparentRatingKey'))
        self.grandparentTheme = data.attrib.get('grandparentTheme')
        self.grandparentThumb = data.attrib.get('grandparentThumb')
        self.grandparentTitle = data.attrib.get('grandparentTitle')
        self.guid = data.attrib.get('guid')
        self.index = utils.cast(int, data.attrib.get('index'))
        self.originallyAvailableAt = utils.toDatetime(data.attrib.get('originallyAvailableAt'), '%Y-%m-%d')
        self.parentIndex = data.attrib.get('parentIndex')
        self.parentKey = data.attrib.get('parentKey')
        self.parentRatingKey = utils.cast(int, data.attrib.get('parentRatingKey'))
        self.parentThumb = data.attrib.get('parentThumb')
        self.rating = utils.cast(float, data.attrib.get('rating'))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year'))
        self.directors = self.findItems(data, media.Director)
        self.media = self.findItems(data, media.Media)
        self.writers = self.findItems(data, media.Writer)
        # data for active sessions and history
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey'))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self._server, data)
        self.transcodeSession = utils.findTranscodeSession(self._server, data)

    def __repr__(self):
        return '<%s>' % ':'.join([p for p in [
            self.__class__.__name__,
            self.key.replace('/library/metadata/', '').replace('/children', ''),
            '%s-s%se%s' % (self.grandparentTitle.replace(' ','-')[:20], self.seasonNumber, self.index),
        ] if p])

    @property
    def isWatched(self):
        """Returns True if watched, False if not."""
        return bool(self.viewCount > 0)

    @property
    def seasonNumber(self):
        """Return this episode seasonnumber."""
        if self._seasonNumber is None:
            self._seasonNumber = self.parentIndex if self.parentIndex else self.season().seasonNumber
        return utils.cast(int, self._seasonNumber)

    @property
    def thumbUrl(self):
        """ Return url to for the thumbnail image. """
        if self.grandparentThumb:
            return self._server.url(self.grandparentThumb)

    def season(self):
        """Return this episode Season"""
        return self.fetchItem(self.parentKey)

    def show(self):
        """Return this episodes Show"""
        return self.fetchItem(self.grandparentKey)

    @property
    def location(self):
        """ This does not exist in plex xml response but is added to have a common
            interface to get the location of the Movie/Show
        """
        # Note this should probably belong to some parent.
        files = [i.file for i in self.iterParts() if i]
        if len(files) == 1:
            files = files[0]
        return files

    def _prettyfilename(self):
        return '%s.S%sE%s' % (self.grandparentTitle.replace(' ', '.'),
            str(self.seasonNumber).zfill(2), str(self.index).zfill(2))
