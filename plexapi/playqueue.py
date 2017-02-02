# -*- coding: utf-8 -*-
import plexapi
import requests
from plexapi import utils


class PlayQueue(object):
    """Summary

    Attributes:
        identifier (TYPE): Description
        initpath (TYPE): Description
        items (TYPE): Description
        mediaTagPrefix (TYPE): Description
        mediaTagVersion (TYPE): Description
        playQueueID (TYPE): Description
        playQueueSelectedItemID (TYPE): Description
        playQueueSelectedItemOffset (TYPE): Description
        playQueueTotalCount (TYPE): Description
        playQueueVersion (TYPE): Description
        server (TYPE): Description
    """
    def __init__(self, server, data, initpath):
        """Summary

        Args:
            server (TYPE): Description
            data (TYPE): Description
            initpath (TYPE): Description
        """
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
        """Summary

        Args:
            server (TYPE): Description
            item (TYPE): Description
            shuffle (int, optional): Description
            repeat (int, optional): Description
            includeChapters (int, optional): Description
            includeRelated (int, optional): Description

        Returns:
            TYPE: Description
        """
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
