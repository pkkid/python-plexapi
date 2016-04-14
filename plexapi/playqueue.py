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
    def create(cls, server, item, shuffle=0, repeat=0, includeChapters=1, includeRelated=1):
        args = {}
        args['includeChapters'] = includeChapters
        args['includeRelated'] = includeRelated
        args['repeat'] = repeat
        args['shuffle'] = shuffle
        if item.type == 'playlist':
            args['playlistID'] = item.ratingKey
            args['type'] = item.playlistType
        else:
            uuid = item.section().uuid
            args['key'] = item.key
            args['type'] = item.listType
            args['uri'] = 'library://%s/item/%s' % (uuid, item.key)
        path = '/playQueues%s' % utils.joinArgs(args)
        data = server.query(path, method=requests.post)
        return cls(server, data, initpath=path)
