# -*- coding: utf-8 -*-
from plexapi import utils
from plexapi.base import PlexObject


class PlayQueue(PlexObject):
    """ Control a PlayQueue.

        Attributes:
            key (str): This is only added to support playMedia
            identifier (str): com.plexapp.plugins.library
            initpath (str): Relative url where data was grabbed from.
            items (list): List of :class:`~plexapi.media.Media` or class:`~plexapi.playlist.Playlist`
            mediaTagPrefix (str): Fx /system/bundle/media/flags/
            mediaTagVersion (str): Fx 1485957738
            playQueueID (str): a id for the playqueue
            playQueueSelectedItemID (str): playQueueSelectedItemID
            playQueueSelectedItemOffset (str): playQueueSelectedItemOffset
            playQueueSelectedMetadataItemID (<type 'str'>): 7
            playQueueShuffled (bool): True if shuffled
            playQueueSourceURI (str): Fx library://150425c9-0d99-4242-821e-e5ab81cd2221/item//library/metadata/7
            playQueueTotalCount (str): How many items in the play queue.
            playQueueVersion (str): What version the playqueue is.
            server (:class:`~plexapi.server.PlexServer`): Server you are connected to.
            size (str): Seems to be a alias for playQueueTotalCount.
    """

    def _loadData(self, data):
        self._data = data
        self.identifier = data.attrib.get('identifier')
        self.mediaTagPrefix = data.attrib.get('mediaTagPrefix')
        self.mediaTagVersion = data.attrib.get('mediaTagVersion')
        self.playQueueID = data.attrib.get('playQueueID')
        self.playQueueSelectedItemID = data.attrib.get('playQueueSelectedItemID')
        self.playQueueSelectedItemOffset = data.attrib.get('playQueueSelectedItemOffset')
        self.playQueueSelectedMetadataItemID = data.attrib.get('playQueueSelectedMetadataItemID')
        self.playQueueShuffled = utils.cast(bool, data.attrib.get('playQueueShuffled', 0))
        self.playQueueSourceURI = data.attrib.get('playQueueSourceURI')
        self.playQueueTotalCount = data.attrib.get('playQueueTotalCount')
        self.playQueueVersion = data.attrib.get('playQueueVersion')
        self.size = utils.cast(int, data.attrib.get('size', 0))
        self.items = self.findItems(data)


    @classmethod
    def create(cls, server, item, shuffle=0, repeat=0, includeChapters=1, includeRelated=1, continuous=0, parent=None, sort=None):
        """ Create and returns a new :class:`~plexapi.playqueue.PlayQueue`.

            Paramaters:
                server (:class:`~plexapi.server.PlexServer`): Server you are connected to.
                item (:class:`~plexapi.media.Media` or class:`~plexapi.playlist.Playlist`): A media or Playlist.
                shuffle (int, optional): Start the playqueue shuffled.
                repeat (int, optional): Start the playqueue shuffled.
                includeChapters (int, optional): include Chapters.
                includeRelated (int, optional): include Related.
                continuous (int, optional): include rest of item collection.
                parent (str, optional): use a custom uri.
                sort (str, optional): if playing a section this param will be used.
        """
        args = {}
        args['includeChapters'] = includeChapters
        args['includeRelated'] = includeRelated
        args['repeat'] = repeat
        args['shuffle'] = shuffle
        args['continuous'] = continuous
        if item.type == 'playlist':
            args['playlistID'] = item.ratingKey
            args['type'] = item.playlistType
        elif hasattr(item, 'uuid'):
            args['type'] = item.type
            sortStr = ""
            if sort is not None:
                sortStr = "sort=" + sort
            args['uri'] = 'server://%s/com.plexapp.plugins.library/library/sections/%s/all?%s' % (server.machineIdentifier, item.key, sortStr)
        else:
            uuid = item.section().uuid
            args['key'] = item.key
            args['type'] = item.listType
            if parent is not None:
                args['uri'] = 'library://%s/item/%s' % (uuid, parent.key)
            else:
                args['uri'] = 'library://%s/item/%s' % (uuid, item.key)
        path = '/playQueues%s' % utils.joinArgs(args)
        data = server.query(path, method=server._session.post)
        c = cls(server, data, initpath=path)
        # we manually add a key so we can pass this to playMedia
        # since the data, does not contain a key.
        c.key = item.key
        c.repeat = repeat
        c.includeChapters = includeChapters
        c.includeRelated = includeRelated
        c.server = server
        return c

    @classmethod
    def get_from_url(cls, server, path, key):
        """ Create from url the playqueue. """
        data = server.query(path, method=server._session.get)
        c = cls(server, data, initpath=path)
        c.key = key
        c.repeat = 0
        c.includeChapters = 1
        c.includeRelated = 1
        c.server = server
        return c

    def refresh(self):
        """ Refresh the playqueue data. """
        args = {}
        args['includeChapters'] = self.includeChapters
        args['includeRelated'] = self.includeRelated
        args['repeat'] = self.repeat
        path = '/playQueues/%s%s' % (self.playQueueID, utils.joinArgs(args))
        data = self.server.query(path, method=self.server._session.get)
        self._loadData(data)