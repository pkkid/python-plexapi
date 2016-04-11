# -*- coding: utf-8 -*-
"""
PlexPlaylist
"""
import requests
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
        # PUT /playlists/29988/items?uri=library%3A%2F%2F32268d7c-3e8c-4ab5-98ad-bad8a3b78c63%2Fitem%2F%252Flibrary%252Fmetadata%252F801
        if not isinstance(items, (list, tuple)):
            items = [items]
        ratingKeys = []
        for item in items:
            if item.__class__.LISTTYPE != self.playlistType:
                raise BadRequest('Can not mix media types when building a playlist: %s and %s' % (self.playlistType, item.__class__.LISTTYPE))
            ratingKeys.append(item.ratingKey)
        path = '%s/items%s' % (self.key, utils.joinArgs({
            'uri': 'library://__GID__/directory//library/metadata/%s' % ','.join(ratingKeys),
        }))
        return self.server.query(path, method=self.server.session.put)

    def removeItem(self, item):
        # DELETE /playlists/29988/items/4866
        path = '%s/items/%s' % (self.key, item.playlistItemID)
        return self.server.query(path, method=self.server.session.delete)

    def moveItem(self, item, after=None):
        # PUT /playlists/29988/items/4556/move?after=4445
        # PUT /playlists/29988/items/4556/move  (to first item)
        path = '%s/items/%s/move' % (self.key, item.playlistItemID)
        if after:
            path += '?after=%s' % after.playlistItemID
        return self.server.query(path, method=self.server.session.put)
        
    def edit(self, title=None, summary=None):
        # PUT /library/metadata/29988?title=You%20Look%20Like%20Gollum2&summary=foobar
        path = '/library/metadata/%s%s' % (self.ratingKey, utils.joinArgs({'title':title, 'summary':summary}))
        return self.server.query(path, method=self.server.session.put)
        
    def delete(self):
        # DELETE /library/metadata/29988
        return self.server.query(self.key, method=self.server.session.delete)
        
    @classmethod
    def create(cls, server, title, items):
        # NOTE: I have not yet figured out what __GID__ is below or where the proper value
        # can be obtained. However, the good news is passing anything in seems to work.
        if not isinstance(items, (list, tuple)):
            items = [items]
        # collect a list of itemkeys and make sure all items share the same listtype
        listtype = items[0].__class__.LISTTYPE
        ratingKeys = []
        for item in items:
            if item.__class__.LISTTYPE != listtype:
                raise BadRequest('Can not mix media types when building a playlist')
            ratingKeys.append(item.ratingKey)
        # build and send the request
        path = '/playlists%s' % utils.joinArgs({
            'uri': 'library://__GID__/directory//library/metadata/%s' % ','.join(ratingKeys),
            'type': listtype,
            'title': title,
            'smart': 0
        })
        data = server.query(path, method=server.session.post)[0]
        return cls(server, data, initpath=path)
