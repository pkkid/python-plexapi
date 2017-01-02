# -*- coding: utf-8 -*-
"""
PlexPhoto

Attributes:
    NA (TYPE): Description
"""
from plexapi import media, utils
from plexapi.utils import PlexPartialObject
NA = utils.NA


@utils.register_libtype
class Photoalbum(PlexPartialObject):
    """Summary

    Attributes:
        addedAt (TYPE): Description
        art (TYPE): Description
        composite (TYPE): Description
        guid (TYPE): Description
        index (TYPE): Description
        key (TYPE): Description
        librarySectionID (TYPE): Description
        listType (str): Description
        ratingKey (TYPE): Description
        summary (TYPE): Description
        thumb (TYPE): Description
        title (TYPE): Description
        TYPE (str): Description
        type (TYPE): Description
        updatedAt (TYPE): Description
    """
    TYPE = 'photoalbum'

    def __init__(self, server, data, initpath):
        """Summary

        Args:
            server (TYPE): Description
            data (TYPE): Description
            initpath (TYPE): Description
        """
        super(Photoalbum, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """Summary

        Args:
            data (TYPE): Description

        Returns:
            TYPE: Description
        """
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
        """Summary

        Returns:
            TYPE: Description
        """
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.listItems(self.server, path, Photo.TYPE)

    def photo(self, title):
        """Summary

        Args:
            title (TYPE): Description

        Returns:
            TYPE: Description
        """
        path = '/library/metadata/%s/children' % self.ratingKey
        return utils.findItem(self.server, path, title)

    def section(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.server.library.sectionByID(self.librarySectionID)


@utils.register_libtype
class Photo(PlexPartialObject):
    """Summary

    Attributes:
        addedAt (TYPE): Description
        index (TYPE): Description
        key (TYPE): Description
        listType (str): Description
        media (TYPE): Description
        originallyAvailableAt (TYPE): Description
        parentKey (TYPE): Description
        parentRatingKey (TYPE): Description
        ratingKey (TYPE): Description
        summary (TYPE): Description
        thumb (TYPE): Description
        title (TYPE): Description
        TYPE (str): Description
        type (TYPE): Description
        updatedAt (TYPE): Description
        year (TYPE): Description
    """
    TYPE = 'photo'

    def __init__(self, server, data, initpath):
        """Summary

        Args:
            server (TYPE): Description
            data (TYPE): Description
            initpath (TYPE): Description
        """
        super(Photo, self).__init__(data, initpath, server)

    def _loadData(self, data):
        """Summary

        Args:
            data (TYPE): Description

        Returns:
            TYPE: Description
        """
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
        """Summary

        Returns:
            TYPE: Description
        """
        return utils.listItems(self.server, self.parentKey)[0]

    def section(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.server.library.sectionByID(self.photoalbum().librarySectionID)
