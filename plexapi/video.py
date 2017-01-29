# -*- coding: utf-8 -*-
from plexapi import media, utils
from plexapi.exceptions import NotFound
from plexapi.utils import Playable, PlexPartialObject

NA = utils.NA


class Video(PlexPartialObject):
    TYPE = None

    def __init__(self, server, data, initpath):
        """Default class for all video types.

        Args:
            server (Plexserver): The PMS server your connected to
            data (Element): Element built from server.query
            initpath (str): Relativ path fx /library/sections/1/all

        """
        super(Video, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): Usually built from server.query
        """
        self.listType = 'video'
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt', NA))
        self.key = data.attrib.get('key', NA)
        self.lastViewedAt = utils.toDatetime(
            data.attrib.get('lastViewedAt', NA))
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

    def analyze(self):
        """The primary purpose of media analysis is to gather information about
        that mediaitem. All of the media you add to a Library has properties
        that are useful to know–whether it's a video file,
        a music track, or one of your photos.
        """
        self.server.query('/%s/analyze' % self.key.lstrip('/'), method=self.server.session.put)

    def markWatched(self):
        """Mark a items as watched."""
        path = '/:/scrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self.server.query(path)
        self.reload()

    def markUnwatched(self):
        """Mark a item as unwatched."""
        path = '/:/unscrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self.server.query(path)
        self.reload()

    def refresh(self):
        """Refresh a item."""
        self.server.query('%s/refresh' %
                          self.key, method=self.server.session.put)

    def section(self):
        """Library section."""
        return self.server.library.sectionByID(self.librarySectionID)


@utils.register_libtype
class Movie(Video, Playable):
    TYPE = 'movie'

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): XML reponse from PMS as Element
                            normally built from server.query
        """
        Video._loadData(self, data)
        Playable._loadData(self, data)
        self.art = data.attrib.get('art', NA)
        self.audienceRating = utils.cast(
            float, data.attrib.get('audienceRating', NA))
        self.audienceRatingImage = data.attrib.get('audienceRatingImage', NA)
        self.chapterSource = data.attrib.get('chapterSource', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.guid = data.attrib.get('guid', NA)
        self.originalTitle = data.attrib.get('originalTitle', NA)
        self.originallyAvailableAt = utils.toDatetime(
            data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.primaryExtraKey = data.attrib.get('primaryExtraKey', NA)
        self.rating = data.attrib.get('rating', NA)
        self.ratingImage = data.attrib.get('ratingImage', NA)
        self.studio = data.attrib.get('studio', NA)
        self.tagline = data.attrib.get('tagline', NA)
        self.userRating = utils.cast(float, data.attrib.get('userRating', NA))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():  # check this
            self.collections = [media.Collection(
                self.server, e) for e in data if e.tag == media.Collection.TYPE]
            self.countries = [media.Country(self.server, e)
                              for e in data if e.tag == media.Country.TYPE]
            self.directors = [media.Director(
                self.server, e) for e in data if e.tag == media.Director.TYPE]
            self.genres = [media.Genre(self.server, e)
                           for e in data if e.tag == media.Genre.TYPE]
            self.media = [media.Media(self.server, e, self.initpath, self)
                          for e in data if e.tag == media.Media.TYPE]
            self.producers = [media.Producer(
                self.server, e) for e in data if e.tag == media.Producer.TYPE]
            self.roles = [media.Role(self.server, e)
                          for e in data if e.tag == media.Role.TYPE]
            self.writers = [media.Writer(self.server, e)
                            for e in data if e.tag == media.Writer.TYPE]
            self.fields = [media.Field(e)
                           for e in data if e.tag == media.Field.TYPE]
            self.videoStreams = utils.findStreams(self.media, 'videostream')
            self.audioStreams = utils.findStreams(self.media, 'audiostream')
            self.subtitleStreams = utils.findStreams(
                self.media, 'subtitlestream')

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
                download_url = self.server.url('%s?download=1' % loc.key)

            dl = utils.download(download_url, filename=name, savepath=savepath, session=self.server.session)
            if dl:
                downloaded.append(dl)

        return downloaded


@utils.register_libtype
class Show(Video):
    TYPE = 'show'

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): Usually built from server.query
        """
        Video._loadData(self, data)
        # Incase this was loaded from search etc
        self.key = self.key.replace('/children', '')
        self.art = data.attrib.get('art', NA)
        self.banner = data.attrib.get('banner', NA)
        self.childCount = utils.cast(int, data.attrib.get('childCount', NA))
        self.contentRating = data.attrib.get('contentRating', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.guid = data.attrib.get('guid', NA)
        self.index = data.attrib.get('index', NA)
        self.leafCount = utils.cast(int, data.attrib.get('leafCount', NA))
        self.location = utils.findLocations(data, single=True) or NA
        self.originallyAvailableAt = utils.toDatetime(
            data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.rating = utils.cast(float, data.attrib.get('rating', NA))
        self.studio = data.attrib.get('studio', NA)
        self.theme = data.attrib.get('theme', NA)
        self.viewedLeafCount = utils.cast(
            int, data.attrib.get('viewedLeafCount', NA))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():  # will be fixed with docs.
            self.genres = [media.Genre(self.server, e)
                           for e in data if e.tag == media.Genre.TYPE]
            self.roles = [media.Role(self.server, e)
                          for e in data if e.tag == media.Role.TYPE]

    @property
    def actors(self):
        return self.roles

    @property
    def isWatched(self):
        return bool(self.viewedLeafCount == self.leafCount)

    def seasons(self):
        """Returns a list of Season."""
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, path, Season.TYPE)

    def season(self, title=None):
        """Returns a Season

        Args:
            title (str, int): fx Season 1
        """
        if isinstance(title, int):
            title = 'Season %s' % title

        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def episodes(self, watched=None):
        """Returs a list of Episode

           Args:
                watched (bool): Defaults to None. Exclude watched episodes
        """
        leavesKey = '/library/metadata/%s/allLeaves' % self.ratingKey
        return utils.listItems(self.server, leavesKey, watched=watched)

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
        if not title and (not season or not episode):
            raise TypeError('Missing argument: title or season and episode are required')

        if title:
            path = '/library/metadata/%s/allLeaves' % self.ratingKey
            return utils.findItem(self.server, path, title)

        elif season and episode:
            results = [i for i in self.episodes()
                       if i.seasonNumber == season and i.index == episode]
            if results:
                return results[0]
            else:
                raise NotFound('Couldnt find %s S%s E%s' % (self.title, season, episode))

    def watched(self):
        """Return a list of watched episodes"""
        return self.episodes(watched=True)

    def unwatched(self):
        """Return a list of unwatched episodes"""
        return self.episodes(watched=False)

    def get(self, title):
        """Get a Episode with a title.

           Args:
                title (str): fx Secret santa
        """
        return self.episode(title)

    def analyze(self):
        """ """
        raise 'Cant analyse a show'  # fix me

    def refresh(self):
        """Refresh the metadata."""
        self.server.query('/library/metadata/%s/refresh' % self.ratingKey, method=self.server.session.put)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        downloaded = []
        for ep in self.episodes():
            dl = ep.download(savepath=savepath, keep_orginal_name=keep_orginal_name, **kwargs)

            if dl:
                downloaded.extend(dl)

        return downloaded


@utils.register_libtype
class Season(Video):
    TYPE = 'season'

    def _loadData(self, data):
        """Used to set the attributes

        Args:
            data (Element): Usually built from server.query
        """
        Video._loadData(self, data)
        self.key = self.key.replace('/children', '')
        self.leafCount = utils.cast(int, data.attrib.get('leafCount', NA))
        self.index = utils.cast(int, data.attrib.get('index', NA))
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = utils.cast(int, data.attrib.get('parentRatingKey', NA))
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.viewedLeafCount = utils.cast(
            int, data.attrib.get('viewedLeafCount', NA))

    @property
    def isWatched(self):
        return bool(self.viewedLeafCount == self.leafCount)

    @property
    def seasonNumber(self):
        """Returns season number."""
        return self.index

    def episodes(self, watched=None):
        """Returs a list of Episode

           Args:
                watched (bool): Defaults to None. Exclude watched episodes

           Returns:
                list: of Episode


        """
        childrenKey = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, childrenKey, watched=watched)

    def episode(self, title=None, episode=None):
        """Find a episode using a title or season and episode.

           Note:
                episode is required if title is missing.

           Args:
                title (str): Default None
                episode (int): Episode number, default None

           Raises:
                TypeError: If title and episode is missing.
                NotFound: If that episode cant be found.

           Returns:
                Episode

           Examples:
                >>> plex.search('The blacklist').season(1).episode(episode=1)
                <Episode:116263:The.Freelancer>
                >>> plex.search('The blacklist').season(1).episode('The Freelancer')
                <Episode:116263:The.Freelancer>

        """
        if not title and not episode:
            raise TypeError('Missing argument, you need to use title or episode.')

        if title:
            path = '/library/metadata/%s/children' % self.ratingKey
            return utils.findItem(self.server, path, title)

        elif episode:
            results = [i for i in self.episodes()
                       if i.seasonNumber == self.index and i.index == episode]
            if results:
                return results[0]
            else:
                raise NotFound('Couldnt find %s.Season %s Episode %s.' % (self.grandparentTitle, self.index. episode))

    def get(self, title):
        """Get a episode with a matching title.

           Args:
                title (str): fx Secret santa

            Returns:
                Episode
        """
        return self.episode(title)

    def show(self):
        """Return this seasons show."""
        return utils.listItems(self.server, self.parentKey)[0]

    def watched(self):
        """Returns a list of watched Episode"""
        return self.episodes(watched=True)

    def unwatched(self):
        """Returns a list of unwatched Episode"""
        return self.episodes(watched=False)

    def __repr__(self):
        clsname = self.__class__.__name__
        key = self.key.replace('/library/metadata/', '').replace('/children', '') if self.key else 'NA'
        title = self.title.replace(' ', '.')[0:20].encode('utf8')
        return '<%s:%s:%s:%s>' % (clsname, key, self.parentTitle, title)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        downloaded = []
        for ep in self.episodes():
            dl = ep.download(savepath=savepath, keep_orginal_name=keep_orginal_name, **kwargs)
            if dl:
                downloaded.extend(dl)

        return downloaded


@utils.register_libtype
class Episode(Video, Playable):
    TYPE = 'episode'

    def _loadData(self, data):
        """Used to set the attributes

            Args:
                data (Element): Usually built from server.query
        """
        Video._loadData(self, data)
        Playable._loadData(self, data)
        self.art = data.attrib.get('art', NA)
        self.chapterSource = data.attrib.get('chapterSource', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.duration = utils.cast(int, data.attrib.get('duration', NA))
        self.grandparentArt = data.attrib.get('grandparentArt', NA)
        self.grandparentKey = data.attrib.get('grandparentKey', NA)
        self.grandparentRatingKey = utils.cast(int, data.attrib.get('grandparentRatingKey', NA))
        self.grandparentTheme = data.attrib.get('grandparentTheme', NA)
        self.grandparentThumb = data.attrib.get('grandparentThumb', NA)
        self.grandparentTitle = data.attrib.get('grandparentTitle', NA)
        self.guid = data.attrib.get('guid', NA)
        self.index = utils.cast(int, data.attrib.get('index', NA))
        self.originallyAvailableAt = utils.toDatetime(
            data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = utils.cast(int, data.attrib.get('parentRatingKey', NA))
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.rating = utils.cast(float, data.attrib.get('rating', NA))
        self.viewOffset = utils.cast(int, data.attrib.get('viewOffset', 0))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        self.directors = [media.Director(self.server, e)
                          for e in data if e.tag == media.Director.TYPE]
        self.media = [media.Media(self.server, e, self.initpath, self)
                      for e in data if e.tag == media.Media.TYPE]
        self.writers = [media.Writer(self.server, e)
                        for e in data if e.tag == media.Writer.TYPE]
        self.videoStreams = utils.findStreams(self.media, 'videostream')
        self.audioStreams = utils.findStreams(self.media, 'audiostream')
        self.subtitleStreams = utils.findStreams(self.media, 'subtitlestream')
        # data for active sessions and history
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey', NA))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self.server, data)
        self.transcodeSession = utils.findTranscodeSession(self.server, data)
        # Cached season number
        self._seasonNumber = None

    def __repr__(self):
        clsname = self.__class__.__name__
        key = self.key.replace('/library/metadata/', '').replace('/children', '') if self.key else 'NA'
        title = self.title.replace(' ', '.')[0:20].encode('utf8')
        return '<%s:%s:%s:S%s:E%s:%s>' % (clsname, key, self.grandparentTitle, self.seasonNumber, self.index, title)

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
        """Return url to thumb image."""
        if self.grandparentThumb:
            return self.server.url(self.grandparentThumb)

    def season(self):
        """Return this episode Season"""
        return utils.listItems(self.server, self.parentKey)[0]

    def show(self):
        """Return this episodes Show"""
        return utils.listItems(self.server, self.grandparentKey)[0]

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
        return '%s.S%sE%s' % (self.grandparentTitle.replace(' ', '.'), str(self.seasonNumber).zfill(2), str(self.index).zfill(2))
