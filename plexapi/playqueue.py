# -*- coding: utf-8 -*-
from urllib.parse import quote_plus

from plexapi import utils
from plexapi.base import PlexObject
from plexapi.exceptions import BadRequest, Unsupported


class PlayQueue(PlexObject):
    """Control a PlayQueue.

    Attributes:
        identifier (str): com.plexapp.plugins.library
        items (list): List of :class:`~plexapi.media.Media` or :class:`~plexapi.playlist.Playlist`
        mediaTagPrefix (str): Fx /system/bundle/media/flags/
        mediaTagVersion (int): Fx 1485957738
        playQueueID (int): ID of the PlayQueue.
        playQueueLastAddedItemID (int):
            Defines where the "Up Next" region starts. Empty unless PlayQueue is modified after creation.
        playQueueSelectedItemID (int): The queue item ID of the currently selected item.
        playQueueSelectedItemOffset (int): The offset of the selected item in the PlayQueue, from the beginning of the queue.
        playQueueSelectedMetadataItemID (int): ID of the currently selected item, matches ratingKey.
        playQueueShuffled (bool): True if shuffled.
        playQueueSourceURI (str): Original URI used to create the PlayQueue.
        playQueueTotalCount (int): How many items in the PlayQueue.
        playQueueVersion (int): Version of the PlayQueue. Increments every time a change is made to the PlayQueue.
        _server (:class:`~plexapi.server.PlexServer`): PlexServer associated with the PlayQueue.
        size (int): Alias for playQueueTotalCount.
    """

    def _loadData(self, data):
        self._data = data
        self.identifier = data.attrib.get("identifier")
        self.mediaTagPrefix = data.attrib.get("mediaTagPrefix")
        self.mediaTagVersion = utils.cast(int, data.attrib.get("mediaTagVersion"))
        self.playQueueID = utils.cast(int, data.attrib.get("playQueueID"))
        self.playQueueLastAddedItemID = utils.cast(
            int, data.attrib.get("playQueueLastAddedItemID")
        )
        self.playQueueSelectedItemID = utils.cast(
            int, data.attrib.get("playQueueSelectedItemID")
        )
        self.playQueueSelectedItemOffset = utils.cast(
            int, data.attrib.get("playQueueSelectedItemOffset")
        )
        self.playQueueSelectedMetadataItemID = utils.cast(
            int, data.attrib.get("playQueueSelectedMetadataItemID")
        )
        self.playQueueShuffled = utils.cast(
            bool, data.attrib.get("playQueueShuffled", 0)
        )
        self.playQueueSourceURI = data.attrib.get("playQueueSourceURI")
        self.playQueueTotalCount = utils.cast(
            int, data.attrib.get("playQueueTotalCount")
        )
        self.playQueueVersion = utils.cast(int, data.attrib.get("playQueueVersion"))
        self.size = utils.cast(int, data.attrib.get("size", 0))
        self.items = self.findItems(data)

    def __contains__(self, playQueueItemID):
        return any(x.playQueueItemID == playQueueItemID for x in self.items)

    @classmethod
    def create(cls, server, item, shuffle=0, repeat=0, includeChapters=1, includeRelated=1, continuous=0):
        """Create and return a new :class:`~plexapi.playqueue.PlayQueue`.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): Server you are connected to.
            item (:class:`~plexapi.media.Media` or :class:`~plexapi.playlist.Playlist`):
                A media item, list of media items, or Playlist.
            shuffle (int, optional): Start the playqueue shuffled.
            repeat (int, optional): Start the playqueue shuffled.
            includeChapters (int, optional): include Chapters.
            includeRelated (int, optional): include Related.
            continuous (int, optional): include additional items after the initial item.
                For a show this would be the next episodes, for a movie it does nothing.
        """
        args = {}
        args["includeChapters"] = includeChapters
        args["includeRelated"] = includeRelated
        args["repeat"] = repeat
        args["shuffle"] = shuffle
        args["continuous"] = continuous

        if isinstance(item, list):
            item_keys = ",".join([str(x.ratingKey) for x in item])
            uri_args = quote_plus(f"/library/metadata/{item_keys}")
            args["uri"] = f"library:///directory/{uri_args}"
            args["type"] = item[0].listType
        elif item.type == "playlist":
            args["playlistID"] = item.ratingKey
            args["type"] = item.playlistType
        else:
            uuid = item.section().uuid
            args["type"] = item.listType
            args["uri"] = f"library://{uuid}/item/{item.key}"

        path = f"/playQueues{utils.joinArgs(args)}"
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
                item (:class:`~plexapi.media.Media` or :class:`~plexapi.playlist.Playlist`):
                    A single media item or Playlist.
                playNext (bool, optional):
                    If True, add this item to the front of the "Up Next" section.
                    If False, the item will be appended to the end of the "Up Next" section.
                    Only has an effect if an item has already been added to the "Up Next" section.
                    See https://support.plex.tv/articles/202188298-play-queues/ for more details.
        """
        args = {}
        if item.type == "playlist":
            args["playlistID"] = item.ratingKey
            itemType = item.playlistType
        else:
            uuid = item.section().uuid
            itemType = item.listType
            args["uri"] = f"library://{uuid}/item{item.key}"

        if itemType != self.playQueueType:
            raise Unsupported("Item type does not match PlayQueue type")

        if playNext:
            args["next"] = 1

        path = f"/playQueues/{self.playQueueID}{utils.joinArgs(args)}"
        data = self._server.query(path, method=self._server._session.put)
        self._loadData(data)

    def move(self, playQueueItemID, afterItemID=None):
        """
        Moves an item to the beginning of the PlayQueue.  If `afterItemID` is provided,
        the item will be placed immediately after the specified item.

            Parameters:
                playQueueItemID (int): Item in the PlayQueue to move.
                afterItemID (int, optional):
                    The playQueueItemID of a different item in the PlayQueue.
                    If provided, `playQueueItemID` will be placed in the PlayQueue after this item.
        """
        for itemID in [playQueueItemID, afterItemID]:
            if itemID not in self:
                raise BadRequest(
                    f"playQueueItemID {itemID} not valid for this PlayQueue"
                )

        args = {}
        if afterItemID:
            args["after"] = afterItemID

        path = f"/playQueues/{self.playQueueID}/items/{playQueueItemID}/move{utils.joinArgs(args)}"
        data = self._server.query(path, method=self._server._session.put)
        self._loadData(data)

    def remove(self, playQueueItemID):
        """Remove an item from the PlayQueue. If playQueueItemID is not specified, remove all items."""
        if playQueueItemID not in self:
            raise BadRequest(
                f"playQueueItemID {playQueueItemID} not valid for this PlayQueue"
            )

        path = f"/playQueues/{self.playQueueID}/items/{playQueueItemID}"
        data = self._server.query(path, method=self._server._session.delete)
        self._loadData(data)

    def clear(self):
        """Remove all items from the PlayQueue except for the currently playing item."""
        path = f"/playQueues/{self.playQueueID}/items"
        data = self._server.query(path, method=self._server._session.delete)
        self._loadData(data)
