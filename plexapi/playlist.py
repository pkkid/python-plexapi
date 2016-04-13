# -*- coding: utf-8 -*-
"""
PlexPlaylist
"""
from plexapi import utils
from plexapi.exceptions import BadRequest
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
        self.key = self.key.replace('/items', '') if self.key else self.key  # FIX_BUG_50
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
        
    def addItems(self, items):
        if not isinstance(items, (list, tuple)):
            items = [items]
        ratingKeys = []
        for item in items:
            if item.listType != self.playlistType:
                raise BadRequest('Can not mix media types when building a playlist: %s and %s' % (self.playlistType, item.listType))
            ratingKeys.append(item.ratingKey)
        uuid = items[0].section().uuid
        ratingKeys = ','.join(ratingKeys)
        path = '%s/items%s' % (self.key, utils.joinArgs({
            'uri': 'library://%s/directory//library/metadata/%s' % (uuid, ratingKeys),
        }))
        return self.server.query(path, method=self.server.session.put)

    def removeItem(self, item):
        path = '%s/items/%s' % (self.key, item.playlistItemID)
        return self.server.query(path, method=self.server.session.delete)

    def moveItem(self, item, after=None):
        path = '%s/items/%s/move' % (self.key, item.playlistItemID)
        if after: path += '?after=%s' % after.playlistItemID
        return self.server.query(path, method=self.server.session.put)
        
    def edit(self, title=None, summary=None):
        path = '/library/metadata/%s%s' % (self.ratingKey, utils.joinArgs({'title':title, 'summary':summary}))
        return self.server.query(path, method=self.server.session.put)
        
    def delete(self):
        return self.server.query(self.key, method=self.server.session.delete)
        
    @classmethod
    def create(cls, server, title, items):
        if not isinstance(items, (list, tuple)):
            items = [items]
        ratingKeys = []
        for item in items:
            if item.listType != items[0].listType:
                raise BadRequest('Can not mix media types when building a playlist')
            ratingKeys.append(item.ratingKey)
        ratingKeys = ','.join(ratingKeys)
        uuid = items[0].section().uuid
        path = '/playlists%s' % utils.joinArgs({
            'uri': 'library://%s/directory//library/metadata/%s' % (uuid, ratingKeys),
            'type': items[0].listType,
            'title': title,
            'smart': 0
        })
        data = server.query(path, method=server.session.post)[0]
        return cls(server, data, initpath=path)
