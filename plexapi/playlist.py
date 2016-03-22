# -*- coding: utf-8 -*-
"""
PlexPlaylist
"""
from plexapi import utils
from plexapi.compat import urlencode
from plexapi.exceptions import Unsupported
from plexapi.utils import cast, toDatetime
NA = utils.NA


@utils.register_libtype
class Playlist(utils.PlexPartialObject):
    TYPE = 'playlist'

    def _loadData(self, data):
        self.addedAt = toDatetime(data.attrib.get('addedAt', NA))
        self.composite = data.attrib.get('composite', NA)  # uri to thumbnail
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.durationInSeconds = cast(int, data.attrib.get('durationInSeconds', NA))
        self.guid = data.attrib.get('guid', NA)
        self.key = data.attrib.get('key', NA).replace('/items', '')  # plex bug? http://bit.ly/1Sc2J3V
        self.leafCount = cast(int, data.attrib.get('leafCount', NA))
        self.playlistType = data.attrib.get('playlistType', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.smart = cast(bool, data.attrib.get('smart', NA))
        self.summary = data.attrib.get('summary', NA)
        self.title = data.attrib.get('title', NA)
        self.type = data.attrib.get('type', NA)
        self.updatedAt = toDatetime(data.attrib.get('updatedAt', NA))

    # TODO: FIXME (Let's move getStreamURL to utils and make it more generic)
    def getStreamUrl(self, offset=0, **kwargs):
        """ Fetch URL to stream audio directly.
            offset: Start time (in seconds) audio will initiate from (ex: 300).
            params: Dict of additional parameters to include in URL.
        """
        if self.TYPE not in [Track.TYPE, Album.TYPE]:
            raise Unsupported('Cannot get stream URL for %s.' % self.TYPE)
        params = {}
        params['path'] = self.key
        params['offset'] = offset
        params['copyts'] = kwargs.get('copyts', 1)
        params['mediaIndex'] = kwargs.get('mediaIndex', 0)
        params['X-Plex-Platform'] = kwargs.get('platform', 'Chrome')
        if 'protocol' in kwargs:
            params['protocol'] = kwargs['protocol']
        return self.server.url('/audio/:/transcode/universal/start.m3u8?%s' % urlencode(params))

    def items(self):
        path = '%s/items' % self.key
        return utils.listItems(self.server, path)

    def isFullObject(self):
        # plex bug? http://bit.ly/1Sc2J3V
        fixed_key = self.key.replace('/items', '')
        return self.initpath == fixed_key
