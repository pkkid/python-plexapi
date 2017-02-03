# -*- coding: utf-8 -*-
from plexapi import media, utils
from plexapi.utils import PlexPartialObject
NA = utils.NA


@utils.register_libtype
class Photoalbum(PlexPartialObject):
    """ Represents a photoalbum (collection of photos).

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).

        Attributes:
            addedAt (datetime): Datetime this item was added to the library.
            art (str): Photo art (/library/metadata/<ratingkey>/art/<artid>)
            composite (str): Unknown
            guid (str): Unknown (unique ID)
            index (sting): Index number of this album.
            key (str): API URL (/library/metadata/<ratingkey>).
            librarySectionID (int): :class:`~plexapi.library.LibrarySection` ID.
            listType (str): Hardcoded as 'photo' (useful for search filters).
            ratingKey (int): Unique key identifying this item.
            summary (str): Summary of the photoalbum.
            thumb (str): URL to thumbnail image.
            title (str): Photoalbum title. (Trip to Disney World)
            type (str): Unknown
            updatedAt (datatime): Datetime this item was updated.
    """
    TYPE = 'photoalbum'

    def __init__(self, server, data, initpath):
        super(Photoalbum, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self.listType = 'photo'
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt', NA))
        self.art = data.attrib.get('art', NA)
        self.composite = data.attrib.get('composite', NA)
        self.guid = data.attrib.get('guid', NA)
        self.index = utils.cast(int, data.attrib.get('index', NA))
        self.key = data.attrib.get('key', NA)
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.summary = data.attrib.get('summary', NA)
        self.thumb = data.attrib.get('thumb', NA)
        self.title = data.attrib.get('title', NA)
        self.type = data.attrib.get('type', NA)
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt', NA))

    def photos(self):
        """ Returns a list of :class:`~plexapi.photo.Photo` objects in this album. """
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, path, Photo.TYPE)

    def photo(self, title):
        """ Returns the :class:`~plexapi.photo.Photo` that matches the specified title. """
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def section(self):
        """ Returns the :class:`~plexapi.library.LibrarySection` this item belongs to. """
        return self.server.library.sectionByID(self.librarySectionID)


@utils.register_libtype
class Photo(PlexPartialObject):
    """ Represents a single photo.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).

        Attributes:
            addedAt (datetime): Datetime this item was added to the library.
            index (sting): Index number of this photo.
            key (str): API URL (/library/metadata/<ratingkey>).
            listType (str): Hardcoded as 'photo' (useful for search filters).
            media (TYPE): Unknown
            originallyAvailableAt (datetime): Datetime this photo was added to Plex.
            parentKey (str): Photoalbum API URL.
            parentRatingKey (int): Unique key identifying the photoalbum.
            ratingKey (int): Unique key identifying this item.
            summary (str): Summary of the photo.
            thumb (str): URL to thumbnail image.
            title (str): Photo title.
            type (str): Unknown
            updatedAt (datatime): Datetime this item was updated.
            year (int): Year this photo was taken.
    """
    TYPE = 'photo'

    def __init__(self, server, data, initpath):
        super(Photo, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self.listType = 'photo'
        self.addedAt = utils.toDatetime(data.attrib.get('addedAt', NA))
        self.index = utils.cast(int, data.attrib.get('index', NA))
        self.key = data.attrib.get('key', NA)
        self.originallyAvailableAt = utils.toDatetime(
            data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.summary = data.attrib.get('summary', NA)
        self.thumb = data.attrib.get('thumb', NA)
        self.title = data.attrib.get('title', NA)
        self.type = data.attrib.get('type', NA)
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt', NA))
        self.year = utils.cast(int, data.attrib.get('year', NA))
        if self.isFullObject():
            self.media = [media.Media(self.server, e, self.initpath, self)
                for e in data if e.tag == media.Media.TYPE]

    def photoalbum(self):
        """ Return this photo's :class:`~plexapi.photo.Photoalbum`. """
        return utils.listItems(self.server, self.parentKey)[0]

    def section(self):
        """ Returns the :class:`~plexapi.library.LibrarySection` this item belongs to. """
        return self.server.library.sectionByID(self.photoalbum().librarySectionID)
