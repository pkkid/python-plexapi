# -*- coding: utf-8 -*-
"""
PlexAPI Play PlayQueues
"""
import plexapi, requests
from plexapi import utils


class PlayQueue(object):

    def __init__(self, server, data, initpath):
        self.server = server
        self.initpath = initpath
        self.identifier = data.attrib.get('identifier')
        self.mediaTagPrefix = data.attrib.get('mediaTagPrefix')
        self.mediaTagVersion = data.attrib.get('mediaTagVersion')
        self.playQueueID = data.attrib.get('playQueueID')
        self.playQueueSelectedItemID = data.attrib.get('playQueueSelectedItemID')
        self.playQueueSelectedItemOffset = data.attrib.get('playQueueSelectedItemOffset')
        self.playQueueTotalCount = data.attrib.get('playQueueTotalCount')
        self.playQueueVersion = data.attrib.get('playQueueVersion')
        self.items = [utils.buildItem(server, elem, initpath) for elem in data]

    @classmethod
    def create(cls, server, video, shuffle=0, continuous=0):
        uuid = video.section().uuid
        path = '/playQueues%s' % utils.joinArgs({
            'uri': 'library://%s/item/%s' % (uuid, video.key),
            'key': video.key,
            'type': 'video',
            'shuffle': shuffle,
            'continuous': continuous,
            'X-Plex-Client-Identifier': plexapi.X_PLEX_IDENTIFIER,
        })
        data = server.query(path, method=requests.post)
        return cls(server, data, initpath=path)
