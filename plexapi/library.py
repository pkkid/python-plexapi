# -*- coding: utf-8 -*-
from plexapi import X_PLEX_CONTAINER_SIZE, log, utils
from plexapi.base import PlexObject
from plexapi.compat import unquote
from plexapi.media import MediaTag, Genre, Role, Director
from plexapi.exceptions import BadRequest, NotFound


class Library(PlexObject):
    """ Represents a PlexServer library. This contains all sections of media defined
        in your Plex server including video, shows and audio.

        Attributes:
            identifier (str): Unknown ('com.plexapp.plugins.library').
            mediaTagVersion (str): Unknown (/system/bundle/media/flags/)
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to.
            title1 (str): 'Plex Library' (not sure how useful this is).
            title2 (str): Second title (this is blank on my setup).
    """
    key = '/library'

    def _loadData(self, data):
        self._data = data
        self._sectionsByID = {}  # cached Section UUIDs
        self.identifier = data.attrib.get('identifier')
        self.mediaTagVersion = data.attrib.get('mediaTagVersion')
        self.title1 = data.attrib.get('title1')
        self.title2 = data.attrib.get('title2')

    def __len__(self):
        return len(self.sections())

    def sections(self):
        """ Returns a list of all media sections in this library. Library sections may be any of
            :class:`~plexapi.library.MovieSection`, :class:`~plexapi.library.ShowSection`,
            :class:`~plexapi.library.MusicSection`, :class:`~plexapi.library.PhotoSection`.
        """
        SECTION_TYPES = {MovieSection.TYPE:MovieSection, ShowSection.TYPE:ShowSection,
            MusicSection.TYPE: MusicSection, PhotoSection.TYPE: PhotoSection}
        items = []
        key = '/library/sections'
        for elem in self._server._query(key):
            stype = elem.attrib['type']
            if stype in SECTION_TYPES:
                cls = SECTION_TYPES[stype]
                section = cls(self._server, elem, key)
                self._sectionsByID[section.key] = section
                items.append(section)
        return items

    def section(self, title=None):
        """ Returns the :class:`~plexapi.library.LibrarySection` that matches the specified title.

            Parameters:
                title (str): Title of the section to return.

            Raises:
                :class:`~plexapi.exceptions.NotFound`: Invalid library section title.
        """
        for section in self.sections():
            if section.title == title:
                return section
        raise NotFound('Invalid library section: %s' % title)

    def sectionByID(self, sectionID):
        """ Returns the :class:`~plexapi.library.LibrarySection` that matches the specified sectionID.

            Parameters:
                sectionID (str): ID of the section to return.
        """
        if not self._sectionsByID or sectionID not in self._sectionsByID:
            self.sections()
        return self._sectionsByID[sectionID]

    def all(self, **kwargs):
        """ Returns a list of all media from all library sections.
            This may be a very large dataset to retrieve.
        """
        return [item for section in self.sections() for item in section.all(**kwargs)]

    def onDeck(self):
        """ Returns a list of all media items on deck. """
        return self.fetchItems('/library/onDeck')

    def recentlyAdded(self):
        """ Returns a list of all media items recently added. """
        return self.fetchItems('/library/recentlyAdded')

    def search(self, title=None, libtype=None, **kwargs):
        """ Searching within a library section is much more powerful. It seems certain
            attributes on the media objects can be targeted to filter this search down
            a bit, but I havent found the documentation for it.

            Example: "studio=Comedy%20Central" or "year=1999" "title=Kung Fu" all work. Other items
            such as actor=<id> seem to work, but require you already know the id of the actor.
            TLDR: This is untested but seems to work. Use library section search when you can.
        """
        args = {}
        if title:
            args['title'] = title
        if libtype:
            args['type'] = utils.searchType(libtype)
        for attr, value in kwargs.items():
            args[attr] = value
        key = '/library/all%s' % utils.joinArgs(args)
        return self.fetchItems(key)

    def cleanBundles(self):
        """ Poster images and other metadata for items in your library are kept in "bundle"
            packages. When you remove items from your library, these bundles aren't immediately
            removed. Removing these old bundles can reduce the size of your install. By default, your
            server will automatically clean up old bundles once a week as part of Scheduled Tasks.
        """
        # TODO: Should this check the response for success or the correct mediaprefix?
        self._server._query('/library/clean/bundles')

    def emptyTrash(self):
        """ If a library has items in the Library Trash, use this option to empty the Trash. """
        for section in self.sections():
            section.emptyTrash()

    def optimize(self):
        """ The Optimize option cleans up the server database from unused or fragmented data.
            For example, if you have deleted or added an entire library or many items in a
            library, you may like to optimize the database.
        """
        self._server._query('/library/optimize')

    def refresh(self):
        """ Refresh the metadata for the entire library. This will fetch fresh metadata for
            all contents in the library, including items that already have metadata.
        """
        self._server._query('/library/sections/all/refresh')


class LibrarySection(PlexObject):
    """ Base class for a single library section.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this library section is from.
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).

        Attributes:
            server (:class:`~plexapi.server.PlexServer`): Server this client is connected to.
            initpath (str): Path requested when building this object.
            agent (str): Unknown (com.plexapp.agents.imdb, etc)
            allowSync (bool): True if you allow syncing content from this section.
            art (str): Wallpaper artwork used to respresent this section.
            composite (str): Composit image used to represent this section.
            createdAt (datetime): Datetime this library section was created.
            filters (str): Unknown
            key (str): Key (or ID) of this library section.
            language (str): Language represented in this section (en, xn, etc).
            locations (str): Paths on disk where section content is stored.
            refreshing (str): True if this section is currently being refreshed.
            scanner (str): Internal scanner used to find media (Plex Movie Scanner, Plex Premium Music Scanner, etc.)
            thumb (str): Thumbnail image used to represent this section.
            title (str): Title of this section.
            type (str): Type of content section represents (movie, artist, photo, show).
            updatedAt (datetime): Datetime this library section was last updated.
            uuid (str): Unique id for this section (32258d7c-3e6c-4ac5-98ad-bad7a3b78c63)
    """
    ALLOWED_FILTERS = ()
    ALLOWED_SORT = ()
    BOOLEAN_FILTERS = ('unwatched', 'duplicate')

    def _loadData(self, data):
        self._data = data
        self.agent = data.attrib.get('agent')
        self.allowSync = utils.cast(bool, data.attrib.get('allowSync'))
        self.art = data.attrib.get('art')
        self.composite = data.attrib.get('composite')
        self.createdAt = utils.toDatetime(data.attrib.get('createdAt'))
        self.filters = data.attrib.get('filters')
        self.key = data.attrib.get('key')  # invalid key from plex
        self.language = data.attrib.get('language')
        self.locations = utils.findLocations(data)
        self.refreshing = utils.cast(bool, data.attrib.get('refreshing'))
        self.scanner = data.attrib.get('scanner')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.type = data.attrib.get('type')
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt'))
        self.uuid = data.attrib.get('uuid')

    def __repr__(self):
        return '<%s>' % ':'.join([p for p in [self.__class__.__name__,
            self.key, self.librarySectionTitle] if p])

    def get(self, title):
        """ Returns the media item with the specified title.

            Parameters:
                title (str): Title of the item to return.
        """
        key = '/library/sections/%s/all' % self.key
        return self.fetchItem(key, title=title)

    def all(self, **kwargs):
        """ Returns a list of media from this library section. """
        key = '/library/sections/%s/all' % self.key
        return self.fetchItems(key, **kwargs)

    def onDeck(self):
        """ Returns a list of media items on deck from this library section. """
        key = '/library/sections/%s/onDeck' % self.key
        return self.fetchItems(key)

    def recentlyAdded(self, maxresults=50):
        """ Returns a list of media items recently added from this library section.

            Parameters:
                maxresults (int): Max number of items to return (default 50).
        """
        return self.search(sort='addedAt:desc', maxresults=maxresults)

    def analyze(self):
        """ Run an analysis on all of the items in this library section. """
        key = '/library/sections/%s/analyze' % self.key
        self._server._query(key, method=self._server._session.put)

    def emptyTrash(self):
        """ If a section has items in the Trash, use this option to empty the Trash. """
        key = '/library/sections/%s/emptyTrash' % self.key
        self._server._query(key)

    def refresh(self):
        """ Refresh the metadata for this library section. This will fetch fresh metadata for
            all contents in the section, including items that already have metadata.
        """
        key = '/library/sections/%s/refresh' % self.key
        self._server._query(key)

    def listChoices(self, category, libtype=None, **kwargs):
        """ Returns a list of :class:`~plexapi.library.FilterChoice` objects for the
            specified category and libtype. kwargs can be any of the same kwargs in
            :func:`plexapi.library.LibraySection.search()` to help narrow down the choices
            to only those that matter in your current context.

            Parameters:
                category (str): Category to list choices for (genre, contentRating, etc).
                libtype (int): Library type of item filter.
                **kwargs (dict): Additional kwargs to narrow down the choices.

            Raises:
                :class:`~plexapi.exceptions.BadRequest`: Cannot include kwarg equal to specified category.
        """
        # TODO: Should this be moved to base?
        if category in kwargs:
            raise BadRequest('Cannot include kwarg equal to specified category: %s' % category)
        args = {}
        for subcategory, value in kwargs.items():
            args[category] = self._cleanSearchFilter(subcategory, value)
        if libtype is not None:
            args['type'] = utils.searchType(libtype)
        key = '/library/sections/%s/%s%s' % (self.key, category, utils.joinArgs(args))
        return self.fetchItems(key, bytag=True)

    def search(self, title=None, sort=None, maxresults=999999, libtype=None, **kwargs):
        """ Search the library. If there are many results, they will be fetched from the server
            in batches of X_PLEX_CONTAINER_SIZE amounts. If you're only looking for the first <num>
            results, it would be wise to set the maxresults option to that amount so this functions
            doesn't iterate over all results on the server.

            Parameters:
                title (str): General string query to search for (optional).
                sort (str): column:dir; column can be any of {addedAt, originallyAvailableAt, lastViewedAt,
                      titleSort, rating, mediaHeight, duration}. dir can be asc or desc (optional).
                maxresults (int): Only return the specified number of results (optional).
                libtype (str): Filter results to a spcifiec libtype (movie, show, episode, artist, album, track; optional).
                **kwargs (dict): Any of the available filters for the current library section. Partial string
                        matches allowed. Multiple matches OR together. All inputs will be compared with the
                        available options and a warning logged if the option does not appear valid.

                        * unwatched: Display or hide unwatched content (True, False). [all]
                        * duplicate: Display or hide duplicate items (True, False). [movie]
                        * actor: List of actors to search ([actor_or_id, ...]). [movie]
                        * collection: List of collections to search within ([collection_or_id, ...]). [all]
                        * contentRating: List of content ratings to search within ([rating_or_key, ...]). [movie,tv]
                        * country: List of countries to search within ([country_or_key, ...]). [movie,music]
                        * decade: List of decades to search within ([yyy0, ...]). [movie]
                        * director: List of directors to search ([director_or_id, ...]). [movie]
                        * genre: List Genres to search within ([genere_or_id, ...]). [all]
                        * network: List of TV networks to search within ([resolution_or_key, ...]). [tv]
                        * resolution: List of video resolutions to search within ([resolution_or_key, ...]). [movie]
                        * studio: List of studios to search within ([studio_or_key, ...]). [music]
                        * year: List of years to search within ([yyyy, ...]). [all]
        """
        # cleanup the core arguments
        args = {}
        for category, value in kwargs.items():
            args[category] = self._cleanSearchFilter(category, value, libtype)
        if title is not None:
            args['title'] = title
        if sort is not None:
            args['sort'] = self._cleanSearchSort(sort)
        if libtype is not None:
            args['type'] = utils.searchType(libtype)
        # iterate over the results
        results, subresults = [], '_init'
        args['X-Plex-Container-Start'] = 0
        args['X-Plex-Container-Size'] = min(X_PLEX_CONTAINER_SIZE, maxresults)
        while subresults and maxresults > len(results):
            key = '/library/sections/%s/all%s' % (self.key, utils.joinArgs(args))
            subresults = self.fetchItems(key)
            results += subresults[:maxresults - len(results)]
            args['X-Plex-Container-Start'] += args['X-Plex-Container-Size']
        return results

    def _cleanSearchFilter(self, category, value, libtype=None):
        # check a few things before we begin
        if category not in self.ALLOWED_FILTERS:
            raise BadRequest('Unknown filter category: %s' % category)
        if category in self.BOOLEAN_FILTERS:
            return '1' if value else '0'
        if not isinstance(value, (list, tuple)):
            value = [value]

        # convert list of values to list of keys or ids
        result = set()
        choices = self.listChoices(category, libtype)
        lookup = {c.title.lower(): unquote(unquote(c.key)) for c in choices}
        allowed = set(c.key for c in choices)
        for item in value:
            print(item)
            item = str((item.id or item.tag) if isinstance(item, MediaTag) else item).lower()
            # find most logical choice(s) to use in url
            if item in allowed: result.add(item); continue
            if item in lookup: result.add(lookup[item]); continue
            matches = [k for t, k in lookup.items() if item in t]
            if matches: map(result.add, matches); continue
            # nothing matched; use raw item value
            log.warning('Filter value not listed, using raw item value: %s' % item)
            result.add(item)
        return ','.join(result)

    def _cleanSearchSort(self, sort):
        sort = '%s:asc' % sort if ':' not in sort else sort
        scol, sdir = sort.lower().split(':')
        lookup = {s.lower(): s for s in self.ALLOWED_SORT}
        if scol not in lookup:
            raise BadRequest('Unknown sort column: %s' % scol)
        if sdir not in ('asc', 'desc'):
            raise BadRequest('Unknown sort dir: %s' % sdir)
        return '%s:%s' % (lookup[scol], sdir)


class MovieSection(LibrarySection):
    """ Represents a :class:`~plexapi.library.LibrarySection` section containing movies.

        Attributes:
            ALLOWED_FILTERS (list<str>): List of allowed search filters. ('unwatched',
                'duplicate', 'year', 'decade', 'genre', 'contentRating', 'collection',
                'director', 'actor', 'country', 'studio', 'resolution')
            ALLOWED_SORT (list<str>): List of allowed sorting keys. ('addedAt',
                'originallyAvailableAt', 'lastViewedAt', 'titleSort', 'rating',
                'mediaHeight', 'duration')
            TYPE (str): 'movie'
    """
    ALLOWED_FILTERS = ('unwatched', 'duplicate', 'year', 'decade', 'genre', 'contentRating',
        'collection', 'director', 'actor', 'country', 'studio', 'resolution')
    ALLOWED_SORT = ('addedAt', 'originallyAvailableAt', 'lastViewedAt', 'titleSort', 'rating',
        'mediaHeight', 'duration')
    TYPE = 'movie'


class ShowSection(LibrarySection):
    """ Represents a :class:`~plexapi.library.LibrarySection` section containing tv shows.

        Attributes:
            ALLOWED_FILTERS (list<str>): List of allowed search filters. ('unwatched',
                'year', 'genre', 'contentRating', 'network', 'collection')
            ALLOWED_SORT (list<str>): List of allowed sorting keys. ('addedAt', 'lastViewedAt',
                'originallyAvailableAt', 'titleSort', 'rating', 'unwatched')
            TYPE (str): 'show'
    """
    ALLOWED_FILTERS = ('unwatched', 'year', 'genre', 'contentRating', 'network', 'collection')
    ALLOWED_SORT = ('addedAt', 'lastViewedAt', 'originallyAvailableAt', 'titleSort',
        'rating', 'unwatched')
    TYPE = 'show'

    def searchShows(self, **kwargs):
        """ Search for a show. See :func:`~plexapi.library.LibrarySection.search()` for usage. """
        return self.search(libtype='show', **kwargs)

    def searchEpisodes(self, **kwargs):
        """ Search for an episode. See :func:`~plexapi.library.LibrarySection.search()` for usage. """
        return self.search(libtype='episode', **kwargs)

    def recentlyAdded(self, libtype='episode', maxresults=50):
        """ Returns a list of recently added episodes from this library section.

            Parameters:
                maxresults (int): Max number of items to return (default 50).
        """
        return self.search(sort='addedAt:desc', libtype=libtype, maxresults=maxresults)


class MusicSection(LibrarySection):
    """ Represents a :class:`~plexapi.library.LibrarySection` section containing music artists.

        Attributes:
            ALLOWED_FILTERS (list<str>): List of allowed search filters. ('genre',
                'country', 'collection')
            ALLOWED_SORT (list<str>): List of allowed sorting keys. ('addedAt',
                'lastViewedAt', 'viewCount', 'titleSort')
            TYPE (str): 'artist'
    """
    ALLOWED_FILTERS = ('genre', 'country', 'collection')
    ALLOWED_SORT = ('addedAt', 'lastViewedAt', 'viewCount', 'titleSort')
    TYPE = 'artist'

    def albums(self):
        """ Returns a list of :class:`~plexapi.audio.Album` objects in this section. """
        key = '/library/sections/%s/albums' % self.key
        return self.fetchItems(key)

    def searchArtists(self, **kwargs):
        """ Search for an artist. See :func:`~plexapi.library.LibrarySection.search()` for usage. """
        return self.search(libtype='artist', **kwargs)

    def searchAlbums(self, **kwargs):
        """ Search for an album. See :func:`~plexapi.library.LibrarySection.search()` for usage. """
        return self.search(libtype='album', **kwargs)

    def searchTracks(self, **kwargs):
        """ Search for a track. See :func:`~plexapi.library.LibrarySection.search()` for usage. """
        return self.search(libtype='track', **kwargs)


class PhotoSection(LibrarySection):
    """ Represents a :class:`~plexapi.library.LibrarySection` section containing photos.

        Attributes:
            ALLOWED_FILTERS (list<str>): List of allowed search filters. <NONE>
            ALLOWED_SORT (list<str>): List of allowed sorting keys. <NONE>
            TYPE (str): 'photo'
    """
    ALLOWED_FILTERS = ('all', 'iso', 'make', 'lens', 'aperture', 'exposure')
    ALLOWED_SORT = ('addedAt')
    TYPE = 'photo'

    def searchAlbums(self, title, **kwargs):
        """ Search for an album. See :func:`~plexapi.library.LibrarySection.search()` for usage. """
        key = '/library/sections/%s/all?type=14' % self.key
        return self.fetchItems(key, title=title)

    def searchPhotos(self, title, **kwargs):
        """ Search for a photo. See :func:`~plexapi.library.LibrarySection.search()` for usage. """
        key = '/library/sections/%s/all?type=13' % self.key
        return self.fetchItems(key, title=title)


@utils.register_libtype
class FilterChoice(PlexObject):
    """ Represents a single filter choice. These objects are gathered when using filters
        while searching for library items and is the object returned in the result set of
        :func:`~plexapi.library.LibrarySection.listChoices()`.

        Attributes:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to.
            initpath (str): Relative path requested when retrieving specified `data` (optional).
            fastKey (str): API path to quickly list all items in this filter
                (/library/sections/<section>/all?genre=<key>)
            key (str): Short key (id) of this filter option (used ad <key> in fastKey above).
            thumb (str): Thumbnail used to represent this filter option.
            title (str): Human readable name for this filter option.
            type (str): Filter type (genre, contentRating, etc).
    """
    TYPE = 'Directory'

    def _loadData(self, data):
        self._data = data
        self.fastKey = data.attrib.get('fastKey')
        self.key = data.attrib.get('key')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.type = data.attrib.get('type')


@utils.register_libtype
class Hub(PlexObject):
    FILTERTYPES = {'genre':Genre, 'director':Director, 'actor':Role}
    TYPE = 'Hub'

    def _loadData(self, data):
        self._data = data
        self.hubIdentifier = data.attrib.get('hubIdentifier')
        self.size = utils.cast(int, data.attrib.get('size'))
        self.title = data.attrib.get('title')
        self.type = data.attrib.get('type')
        self.items = self._buildItems(data)

    def __len__(self):
        return self.size

    def _buildItems(self, data):
        if self.type in self.FILTERTYPES:
            cls = self.FILTERTYPES[self.type]
            return [cls(self._server, elem, self._initpath) for elem in data]
        return super(Hub, self)._buildItems(data)
