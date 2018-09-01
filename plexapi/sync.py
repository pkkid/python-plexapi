# -*- coding: utf-8 -*-
"""
You can work with Mobile Sync on other devices straight away, but if you'd like to use your app as a `sync-target` (when
you can set items to be synced to your app) you need to init some variables.

.. code-block:: python

    def init_sync():
        import plexapi
        plexapi.X_PLEX_PROVIDES = 'sync-target'
        plexapi.BASE_HEADERS['X-Plex-Sync-Version'] = '2'
        plexapi.BASE_HEADERS['X-Plex-Provides'] = plexapi.X_PLEX_PROVIDES

        # mimic iPhone SE
        plexapi.X_PLEX_PLATFORM = 'iOS'
        plexapi.X_PLEX_PLATFORM_VERSION = '11.4.1'
        plexapi.X_PLEX_DEVICE = 'iPhone'

        plexapi.BASE_HEADERS['X-Plex-Platform'] = plexapi.X_PLEX_PLATFORM
        plexapi.BASE_HEADERS['X-Plex-Platform-Version'] = plexapi.X_PLEX_PLATFORM_VERSION
        plexapi.BASE_HEADERS['X-Plex-Device'] = plexapi.X_PLEX_DEVICE
        plexapi.BASE_HEADERS['X-Plex-Model'] = '8,4'
        plexapi.BASE_HEADERS['X-Plex-Vendor'] = 'Apple'

You have to fake platform/device/model because transcoding profiles are hardcoded in Plex, and you obviously have
to explicitly specify that your app supports `sync-target`.
"""

import requests
import plexapi
from plexapi.exceptions import NotFound
from plexapi.base import PlexObject


class SyncItem(PlexObject):
    """
    Represents single sync item, for specified server and client. When you saying in the UI to sync "this" to "that"
    you're basically creating a sync item.

    Attributes:
        id (int): unique id of the item
        machineIdentifier (str): the id of server which holds all this content
        version (int): current version of the item. Each time you modify the item (e.g. by changing amount if media to
            sync) the new version is created
        rootTitle (str): the title of library/media from which the sync item was created. E.g.:

            * when you create an item for an episode 3 of season 3 of show Example, the value would be `Title of
              Episode 3`
            * when you create an item for a season 3 of show Example, the value would be `Season 3`
            * when you set to sync all your movies in library named "My Movies" to value would be `My Movies`

        title (str): the title which you've set when created the sync item
        metadataType (str): the type of media which hides inside, can be `episode`, `movie`, etc.
        contentType (str): basic type of the content: `video` or `audio`
        status (:class:`~plexapi.sync.Status`): current status of the sync
        mediaSettings (:class:`~plexapi.sync.MediaSettings`): media transcoding settings used for the item
        policy (:class:`~plexapi.sync.Policy`): the policy of which media to sync
        location (str): unknown
    """
    TAG = 'SyncItem'

    def __init__(self, server, data, initpath=None, clientIdentifier=None):
        super(SyncItem, self).__init__(server, data, initpath)
        self.clientIdentifier = clientIdentifier

    def _loadData(self, data):
        self._data = data
        self.id = plexapi.utils.cast(int, data.attrib.get('id'))
        self.version = plexapi.utils.cast(int, data.attrib.get('version'))
        self.rootTitle = data.attrib.get('rootTitle')
        self.title = data.attrib.get('title')
        self.metadataType = data.attrib.get('metadataType')
        self.contentType = data.attrib.get('contentType')
        self.machineIdentifier = data.find('Server').get('machineIdentifier')
        self.status = Status(self._server, data.find(Status.TAG))
        self.mediaSettings = MediaSettings(self._server, data.find(MediaSettings.TAG))
        self.policy = Policy(self._server, data.find(Policy.TAG))
        self.location = data.find('Location').attrib.copy()

    def server(self):
        """ Returns :class:`~plexapi.myplex.MyPlexResource` with server of current item.
        """
        server = [s for s in self._server.resources() if s.clientIdentifier == self.machineIdentifier]
        if 0 == len(server):
            raise NotFound('Unable to find server with uuid %s' % self.machineIdentifier)
        return server[0]

    def getMedia(self):
        """ Returns list of :class:`~plexapi.base.Playable` which belong to this sync item.
        """
        server = self.server().connect()
        key = '/sync/items/%s' % self.id
        return server.fetchItems(key)

    def markDownloaded(self, media):
        """ Mark the file as downloaded (by the nature of Plex it will be marked as downloaded within
            any SyncItem where it presented).

            Parameters:
                media (base.Playable): the media to be marked as downloaded
        """
        url = '/sync/%s/item/%s/downloaded' % (self.clientIdentifier, media.ratingKey)
        media._server.query(url, method=requests.put)


class SyncList(PlexObject):
    """ Represents a Mobile Sync state, specific for single client, within one SyncList may be presented
        items from different servers.

        Attributes:
            clientId (str): an identifier of the client
            items (List<:class:`~plexapi.sync.SyncItem`>): list of registered items to sync
    """
    key = 'https://plex.tv/devices/{clientId}/sync_items'
    TAG = 'SyncList'

    def _loadData(self, data):
        self._data = data
        self.clientId = data.attrib.get('clientIdentifier')
        self.items = []

        for elem in data:
            if elem.tag == 'SyncItems':
                for sync_item in elem:
                    item = SyncItem(self._server, sync_item, clientIdentifier=self.clientId)
                    self.items.append(item)


class Status(PlexObject):
    """ Represents a current status of specific :class:`~plexapi.sync.SyncItem`.

        Attributes:
            failureCode: unknown, never got one yet
            failure: unknown
            state (str): server-side status of the item, can be `completed`, `pending`, empty, and probably something else
            itemsCount (int): total items count
            itemsCompleteCount (int): count of transcoded and/or downloaded items
            itemsDownloadedCount (int): count of downloaded items
            itemsReadyCount (int): count of transcoded items, which can be downloaded
            totalSize (int): total size in bytes of complete items
            itemsSuccessfulCount (int): unknown, in my experience it always was equal to `itemsCompleteCount`
    """
    TAG = 'Status'

    def _loadData(self, data):
        self._data = data
        self.failureCode = data.attrib.get('failureCode')
        self.failure = data.attrib.get('failure')
        self.state = data.attrib.get('state')
        self.itemsCount = plexapi.utils.cast(int, data.attrib.get('itemsCount'))
        self.itemsCompleteCount = plexapi.utils.cast(int, data.attrib.get('itemsCompleteCount'))
        self.totalSize = plexapi.utils.cast(int, data.attrib.get('totalSize'))
        self.itemsDownloadedCount = plexapi.utils.cast(int, data.attrib.get('itemsDownloadedCount'))
        self.itemsReadyCount = plexapi.utils.cast(int, data.attrib.get('itemsReadyCount'))
        self.itemsSuccessfulCount = plexapi.utils.cast(int, data.attrib.get('itemsSuccessfulCount'))

    def __repr__(self):
        return '<%s>:%s' % (self.__class__.__name__, dict(
            itemsCount=self.itemsCount,
            itemsCompleteCount=self.itemsCompleteCount,
            itemsDownloadedCount=self.itemsDownloadedCount,
            itemsReadyCount=self.itemsReadyCount,
            itemsSuccessfulCount=self.itemsSuccessfulCount
        ))


class MediaSettings(PlexObject):
    """ Transcoding settings used for all media within :class:`~plexapi.sync.SyncItem`.

        Attributes:
            audioBoost (int): unknown
            maxVideoBitrate (int): unknown
            musicBitrate (int): unknown
            photoQuality (int): unknown
            photoResolution (str): maximum photo resolution, formatted as WxH (e.g. `1920x1080`)
            videoResolution (str): maximum video resolution, formatted as WxH (e.g. `1280x720`)
            subtitleSize (int): unknown
            videoQuality (int): unknown
    """
    TAG = 'MediaSettings'

    def _loadData(self, data):
        self._data = data
        self.audioBoost = plexapi.utils.cast(int, data.attrib.get('audioBoost'))
        self.maxVideoBitrate = plexapi.utils.cast(int, data.attrib.get('maxVideoBitrate'))
        self.musicBitrate = plexapi.utils.cast(int, data.attrib.get('musicBitrate'))
        self.photoQuality = plexapi.utils.cast(int, data.attrib.get('photoQuality'))
        self.photoResolution = data.attrib.get('photoResolution')
        self.videoResolution = data.attrib.get('videoResolution')
        self.subtitleSize = plexapi.utils.cast(int, data.attrib.get('subtitleSize'))
        self.videoQuality = plexapi.utils.cast(int, data.attrib.get('videoQuality'))


class Policy(PlexObject):
    """ Policy of syncing the media.

        Attributes:
            scope (str): can be `count` or `all`
            value (int): valid only when `scope=count`, means amount of media to sync
            unwatched (bool): True means disallow to sync watched media
    """
    TAG = 'Policy'

    def _loadData(self, data):
        self._data = data
        self.scope = data.attrib.get('scope')
        self.value = plexapi.utils.cast(int, data.attrib.get('value'))
        self.unwatched = plexapi.utils.cast(bool, data.attrib.get('unwatched'))
