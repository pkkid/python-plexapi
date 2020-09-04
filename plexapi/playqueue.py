# -*- coding: utf-8 -*-
from urllib.parse import quote_plus

from plexapi import utils
from plexapi.base import PlexObject
from plexapi.exceptions import Unsupported


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
    def create(cls, server, item, shuffle=0, repeat=0, includeChapters=1, includeRelated=1, continuous=0):
        """ Create and returns a new :class:`~plexapi.playqueue.PlayQueue`.

            Paramaters:
                server (:class:`~plexapi.server.PlexServer`): Server you are connected to.
                item (:class:`~plexapi.media.Media` or class:`~plexapi.playlist.Playlist`):
                    A media item, list of media items, or Playlist.
                shuffle (int, optional): Start the playqueue shuffled.
                repeat (int, optional): Start the playqueue shuffled.
                includeChapters (int, optional): include Chapters.
                includeRelated (int, optional): include Related.
                continuous (int, optional): include additional items after the initial item.
                    For a show this would be the next episodes, for a movie it does nothing.
        """
        args = {}
        args['includeChapters'] = includeChapters
        args['includeRelated'] = includeRelated
        args['repeat'] = repeat
        args['shuffle'] = shuffle
        args['continuous'] = continuous

        if isinstance(item, list):
            item_keys = ",".join([str(x.ratingKey) for x in item])
            uri_args = quote_plus('/library/metadata/%s' % item_keys)
            args["uri"] = 'library:///directory/%s' % uri_args
            args["type"] = item[0].listType
        elif item.type == 'playlist':
            args['playlistID'] = item.ratingKey
            args['type'] = item.playlistType

        path = '/playQueues%s' % utils.joinArgs(args)
        data = server.query(path, method=server._session.post)
        c = cls(server, data, initpath=path)
        c.playQueueType = args["type"]
        c._server = server
        return c

    def append(self, item, playNext=False):
        """
        Append the provided item to the "Up Next" section of the PlayQueue.
        Items can only be added to the section immediately following the current playing item.

            Parameters:
                item (:class:`~plexapi.media.Media` or class:`~plexapi.playlist.Playlist`):
                    A single media item or Playlist.
                playNext (int, optional):
                    If True, add this item to the front of the "Up Next" section.
                    If False, it will be appended to the end of the "Up Next" section.
                    See https://support.plex.tv/articles/202188298-play-queues/ for more details.
        """
        args = {}
        if item.type == "playlist":
            args["playlistID"] = item.ratingKey
            itemType = item.playlistType
        else:
            uuid = item.section().uuid
            itemType = item.listType
            args["uri"] = "library://%s/item%s" % (uuid, item.key)

        if itemType != self.playQueueType:
            raise Unsupported("Item type does not match PlayQueue type")

        if playNext:
            args["next"] = playNext

        path = '/playQueues/%s%s' % (self.playQueueID, utils.joinArgs(args))
        data = self._server.query(path, method=self._server._session.put)
        self._loadData(data)
