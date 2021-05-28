# -*- coding: utf-8 -*-
from plexapi import media, utils
from plexapi.base import PlexPartialObject
from plexapi.exceptions import BadRequest, NotFound, Unsupported
from plexapi.library import LibrarySection
from plexapi.mixins import ArtMixin, PosterMixin
from plexapi.mixins import LabelMixin
from plexapi.playqueue import PlayQueue
from plexapi.settings import Setting
from plexapi.utils import deprecated


@utils.registerPlexObject
class Collection(PlexPartialObject, ArtMixin, PosterMixin, LabelMixin):
    """ Represents a single Collection.

        Attributes:
            TAG (str): 'Directory'
            TYPE (str): 'collection'
            addedAt (datetime): Datetime the collection was added to the library.
            art (str): URL to artwork image (/library/metadata/<ratingKey>/art/<artid>).
            artBlurHash (str): BlurHash string for artwork image.
            childCount (int): Number of items in the collection.
            collectionMode (str): How the items in the collection are displayed.
            collectionPublished (bool): True if the collection is published to the Plex homepage.
            collectionSort (str): How to sort the items in the collection.
            content (str): The filter URI string for smart collections.
            contentRating (str) Content rating (PG-13; NR; TV-G).
            fields (List<:class:`~plexapi.media.Field`>): List of field objects.
            guid (str): Plex GUID for the collection (collection://XXXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXX).
            index (int): Plex index number for the collection.
            key (str): API URL (/library/metadata/<ratingkey>).
            labels (List<:class:`~plexapi.media.Label`>): List of label objects.
            librarySectionID (int): :class:`~plexapi.library.LibrarySection` ID.
            librarySectionKey (str): :class:`~plexapi.library.LibrarySection` key.
            librarySectionTitle (str): :class:`~plexapi.library.LibrarySection` title.
            maxYear (int): Maximum year for the items in the collection.
            minYear (int): Minimum year for the items in the collection.
            ratingCount (int): The number of ratings.
            ratingKey (int): Unique key identifying the collection.
            smart (bool): True if the collection is a smart collection.
            subtype (str): Media type of the items in the collection (movie, show, artist, or album).
            summary (str): Summary of the collection.
            thumb (str): URL to thumbnail image (/library/metadata/<ratingKey>/thumb/<thumbid>).
            thumbBlurHash (str): BlurHash string for thumbnail image.
            title (str): Name of the collection.
            titleSort (str): Title to use when sorting (defaults to title).
            type (str): 'collection'
            updatedAt (datatime): Datetime the collection was updated.
    """

    TAG = 'Directory'
    TYPE = 'collection'

    def _loadData(self, data):
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt'))
        self.art = data.attrib.get('art')
        self.artBlurHash = data.attrib.get('artBlurHash')
        self.childCount = utils.cast(int, data.attrib.get('childCount'))
        self.collectionMode = utils.cast(int, data.attrib.get('collectionMode', '-1'))
        self.collectionPublished = utils.cast(bool, data.attrib.get('collectionPublished', '0'))
        self.collectionSort = utils.cast(int, data.attrib.get('collectionSort', '0'))
        self.content = data.attrib.get('content')
        self.contentRating = data.attrib.get('contentRating')
        self.fields = self.findItems(data, media.Field)
        self.guid = data.attrib.get('guid')
        self.index = utils.cast(int, data.attrib.get('index'))
        self.key = data.attrib.get('key', '').replace('/children', '')  # FIX_BUG_50
        self.labels = self.findItems(data, media.Label)
        self.librarySectionID = utils.cast(int, data.attrib.get('librarySectionID'))
        self.librarySectionKey = data.attrib.get('librarySectionKey')
        self.librarySectionTitle = data.attrib.get('librarySectionTitle')
        self.maxYear = utils.cast(int, data.attrib.get('maxYear'))
        self.minYear = utils.cast(int, data.attrib.get('minYear'))
        self.ratingCount = utils.cast(int, data.attrib.get('ratingCount'))
        self.ratingKey = utils.cast(int, data.attrib.get('ratingKey'))
        self.smart = utils.cast(bool, data.attrib.get('smart', '0'))
        self.subtype = data.attrib.get('subtype')
        self.summary = data.attrib.get('summary')
        self.thumb = data.attrib.get('thumb')
        self.thumbBlurHash = data.attrib.get('thumbBlurHash')
        self.title = data.attrib.get('title')
        self.titleSort = data.attrib.get('titleSort', self.title)
        self.type = data.attrib.get('type')
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt'))
        self._items = None  # cache for self.items
        self._section = None  # cache for self.section

    def __len__(self):  # pragma: no cover
        return self.childCount

    def __iter__(self):  # pragma: no cover
        for item in self.items():
            yield item

    def __contains__(self, other):  # pragma: no cover
        return any(i.key == other.key for i in self.items())

    def __getitem__(self, key):  # pragma: no cover
        return self.items()[key]

    def _uriRoot(self, server=None):
        if server:
            uuid = server.machineIentifier
        else:
            uuid = self._server.machineIdentifier
        return 'server://%s/com.plexapp.plugins.library' % uuid

    @property
    @deprecated('use "items" instead', stacklevel=3)
    def children(self):
        return self.items()

    def section(self):
        """ Returns the :class:`~plexapi.library.LibrarySection` this collection belongs to.
        """
        if self._section is None:
            self._section = super(Collection, self).section()
        return self._section

    def item(self, title):
        """ Returns the item in the collection that matches the specified title.

            Parameters:
                title (str): Title of the item to return.

            Raises:
                :class:`plexapi.exceptions.NotFound`: When the item is not found in the collection.
        """
        for item in self.items():
            if item.title.lower() == title.lower():
                return item
        raise NotFound('Item with title "%s" not found in the collection' % title)

    def items(self):
        """ Returns a list of all items in the collection. """
        if self._items is None:
            key = '%s/children' % self.key
            items = self.fetchItems(key)
            self._items = items
        return self._items

    def get(self, title):
        """ Alias to :func:`~plexapi.library.Collection.item`. """
        return self.item(title)

    def _preferences(self):
        """ Returns a list of :class:`~plexapi.settings.Preferences` objects. """
        items = []
        data = self._server.query(self._details_key)
        for item in data.iter('Setting'):
            items.append(Setting(data=item, server=self._server))

        return items

    def modeUpdate(self, mode=None):
        """ Update Collection Mode

            Parameters:
                mode: default     (Library default)
                      hide        (Hide Collection)
                      hideItems   (Hide Items in this Collection)
                      showItems   (Show this Collection and its Items)
            Example:

                collection = 'plexapi.collection.Collection'
                collection.updateMode(mode="hide")
        """
        mode_dict = {'default': -1,
                     'hide': 0,
                     'hideItems': 1,
                     'showItems': 2}
        key = mode_dict.get(mode)
        if key is None:
            raise BadRequest('Unknown collection mode : %s. Options %s' % (mode, list(mode_dict)))
        part = '/library/metadata/%s/prefs?collectionMode=%s' % (self.ratingKey, key)
        return self._server.query(part, method=self._server._session.put)

    def sortUpdate(self, sort=None):
        """ Update Collection Sorting

            Parameters:
                sort: realease     (Order Collection by realease dates)
                      alpha        (Order Collection alphabetically)
                      custom       (Custom collection order)

            Example:

                colleciton = 'plexapi.collection.Collection'
                collection.updateSort(mode="alpha")
        """
        sort_dict = {'release': 0,
                     'alpha': 1,
                     'custom': 2}
        key = sort_dict.get(sort)
        if key is None:
            raise BadRequest('Unknown sort dir: %s. Options: %s' % (sort, list(sort_dict)))
        part = '/library/metadata/%s/prefs?collectionSort=%s' % (self.ratingKey, key)
        return self._server.query(part, method=self._server._session.put)

    def addItems(self, items):
        """ Add items to the collection.

            Parameters:
                items (List<:class:`~plexapi.audio.Audio`> or List<:class:`~plexapi.video.Video`>
                    or List<:class:`~plexapi.photo.Photo`>): List of audio, video, or photo objects
                    to be added to the collection.

            Raises:
                :class:`plexapi.exceptions.BadRequest`: When trying to add items to a smart collection.
        """
        if self.smart:
            raise BadRequest('Cannot add items to a smart collection.')

        if items and not isinstance(items, (list, tuple)):
            items = [items]

        ratingKeys = []
        for item in items:
            if item.type != self.subtype:  # pragma: no cover
                raise BadRequest('Can not mix media types when building a collection: %s and %s' %
                    (self.subtype, item.type))
            ratingKeys.append(str(item.ratingKey))

        ratingKeys = ','.join(ratingKeys)
        uri = '%s/library/metadata/%s' % (self._uriRoot(), ratingKeys)

        key = '%s/items%s' % (self.key, utils.joinArgs({
            'uri': uri
        }))
        self._server.query(key, method=self._server._session.put)

    def removeItems(self, items):
        """ Remove items from the collection.

            Parameters:
                items (List<:class:`~plexapi.audio.Audio`> or List<:class:`~plexapi.video.Video`>
                    or List<:class:`~plexapi.photo.Photo`>): List of audio, video, or photo objects
                    to be removed from the collection. Items must be retrieved from
                    :func:`plexapi.collection.Collection.items`.

            Raises:
                :class:`plexapi.exceptions.BadRequest`: When trying to remove items from a smart collection.
        """
        if self.smart:
            raise BadRequest('Cannot remove items from a smart collection.')

        if items and not isinstance(items, (list, tuple)):
            items = [items]

        for item in items:
            key = '%s/items/%s' % (self.key, item.ratingKey)
            self._server.query(key, method=self._server._session.delete)

    def updateFilters(self, libtype=None, limit=None, sort=None, filters=None, **kwargs):
        """ Update the filters for a smart collection.

            Parameters:
                libtype (str): The specific type of content to filter
                    (movie, show, season, episode, artist, album, track, photoalbum, photo, collection).
                limit (int): Limit the number of items in the collection.
                sort (str or list, optional): A string of comma separated sort fields
                    or a list of sort fields in the format ``column:dir``.
                    See :func:`plexapi.library.LibrarySection.search` for more info.
                filters (dict): A dictionary of advanced filters.
                    See :func:`plexapi.library.LibrarySection.search` for more info.
                **kwargs (dict): Additional custom filters to apply to the search results.
                    See :func:`plexapi.library.LibrarySection.search` for more info.

            Raises:
                :class:`plexapi.exceptions.BadRequest`: When trying update filters for a regular collection.
        """
        if not self.smart:
            raise BadRequest('Cannot update filters for a regular collection.')

        section = self.section()
        searchKey = section._buildSearchKey(
            sort=sort, libtype=libtype, limit=limit, filters=filters, **kwargs)
        uri = '%s%s' % (self._uriRoot(), searchKey)

        key = '%s/items%s' % (self.key, utils.joinArgs({
            'uri': uri
        }))
        self._server.query(key, method=self._server._session.put)

    def edit(self, title=None, titleSort=None, contentRating=None, summary=None, **kwargs):
        """ Edit the collection.
        
            Parameters:
                title (str, optional): The title of the collection.
                titleSort (str, optional): The sort title of the collection.
                contentRating (str, optional): The summary of the collection.
                summary (str, optional): The summary of the collection.
        """
        args = {}
        if title:
            args['title.value'] = title
            args['title.locked'] = 1
        if titleSort:
            args['titleSort.value'] = titleSort
            args['titleSort.locked'] = 1
        if contentRating:
            args['contentRating.value'] = contentRating
            args['contentRating.locked'] = 1
        if summary:
            args['summary.value'] = summary
            args['summary.locked'] = 1

        args.update(kwargs)
        super(Collection, self).edit(**args)

    def delete(self):
        """ Delete the collection. """
        super(Collection, self).delete()

    def playQueue(self, *args, **kwargs):
        """ Returns a new :class:`~plexapi.playqueue.PlayQueue` from the collection. """
        return PlayQueue.create(self._server, self.items(), *args, **kwargs)

    @classmethod
    def _create(cls, server, title, section, items):
        """ Create a regular collection. """
        if not items:
            raise BadRequest('Must include items to add when creating new collection.')

        if not isinstance(section, LibrarySection):
            section = server.library.section(section)

        if items and not isinstance(items, (list, tuple)):
            items = [items]

        itemType = items[0].type
        ratingKeys = []
        for item in items:
            if item.type != itemType:  # pragma: no cover
                raise BadRequest('Can not mix media types when building a collection.')
            ratingKeys.append(str(item.ratingKey))

        ratingKeys = ','.join(ratingKeys)
        uri = '%s/library/metadata/%s' % (cls._uriRoot(server), ratingKeys)

        key = '/library/collections%s' % utils.joinArgs({
            'uri': uri,
            'type': utils.searchType(itemType),
            'title': title,
            'smart': 0,
            'sectionId': section.key
        })
        data = server.query(key, method=server._session.post)[0]
        return cls(server, data, initpath=key)

    @classmethod
    def _createSmart(cls, server, title, section, limit=None, libtype=None, sort=None, filters=None, **kwargs):
        """ Create a smart collection. """
        if not isinstance(section, LibrarySection):
            section = server.library.section(section)

        libtype = libtype or section.TYPE

        searchKey = section._buildSearchKey(
            sort=sort, libtype=libtype, limit=limit, filters=filters, **kwargs)
        uri = '%s%s' % (cls._uriRoot(server), searchKey)

        key = '/library/collections%s' % utils.joinArgs({
            'uri': uri,
            'type': utils.searchType(libtype),
            'title': title,
            'smart': 1,
            'sectionId': section.key
        })
        data = server.query(key, method=server._session.post)[0]
        return cls(server, data, initpath=key)

    @classmethod
    def create(cls, server, title, section, items=None, smart=False, limit=None,
               libtype=None, sort=None, filters=None, **kwargs):
        """ Create a collection.

            Parameters:
                server (:class:`~plexapi.server.PlexServer`): Server to create the collection on.
                title (str): Title of the collection.
                section (:class:`~plexapi.library.LibrarySection`, str): The library section to create the collection in.
                items (List<:class:`~plexapi.audio.Audio`> or List<:class:`~plexapi.video.Video`>
                    or List<:class:`~plexapi.photo.Photo`>): Regular collections only, list of audio,
                    video, or photo objects to be added to the collection.
                smart (bool): True to create a smart collection. Default False.
                limit (int): Smart collections only, limit the number of items in the collection.
                libtype (str): Smart collections only, the specific type of content to filter
                    (movie, show, season, episode, artist, album, track, photoalbum, photo, collection).
                sort (str or list, optional): Smart collections only, a string of comma separated sort fields
                    or a list of sort fields in the format ``column:dir``.
                    See :func:`plexapi.library.LibrarySection.search` for more info.
                filters (dict): Smart collections only, a dictionary of advanced filters.
                    See :func:`plexapi.library.LibrarySection.search` for more info.
                **kwargs (dict): Smart collections only, additional custom filters to apply to the
                    search results. See :func:`plexapi.library.LibrarySection.search` for more info.

            Raises:
                :class:`plexapi.exceptions.BadRequest`: When no items are included to create the collection.
                :class:`plexapi.exceptions.BadRequest`: When mixing media types in the collection.

            Returns:
                :class:`~plexapi.collection.Collection`: A new instance of the created Collection.
        """
        if smart:
            return cls._createSmart(server, title, section, limit, libtype, sort, filters, **kwargs)
        else:
            return cls._create(server, title, section, items)
