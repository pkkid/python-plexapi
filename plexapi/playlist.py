# -*- coding: utf-8 -*-
"""
PlexPlaylist
"""
from plexapi import utils
from plexapi.utils import cast, toDatetime
from plexapi.utils import PlexPartialObject, Playable
NA = utils.NA


@utils.register_libtype
class Playlist(PlexPartialObject, Playable):
    TYPE = 'playlist'

    def __init__(self, server, data, initpath):
        super(Playlist, self).__init__(data, initpath, server)

    def _loadData(self, data):
        Playable._loadData(self, data)
        self.addedAt = toDatetime(data.attrib.get('addedAt', NA))
        self.composite = data.attrib.get('composite', NA)  # url to thumbnail
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.durationInSeconds = cast(int, data.attrib.get('durationInSeconds', NA))
        self.guid = data.attrib.get('guid', NA)
        self.key = data.attrib.get('key', NA)
        if self.key: self.key = self.key.replace('/items', '')  # FIX_BUG_50
        self.leafCount = cast(int, data.attrib.get('leafCount', NA))
        self.playlistType = data.attrib.get('playlistType', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.smart = cast(bool, data.attrib.get('smart', NA))
        self.summary = data.attrib.get('summary', NA)
        self.title = data.attrib.get('title', NA)
        self.type = data.attrib.get('type', NA)
        self.updatedAt = toDatetime(data.attrib.get('updatedAt', NA))

    def items(self):
        path = '%s/items' % self.key
        return utils.listItems(self.server, path)
