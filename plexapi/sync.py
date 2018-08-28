# -*- coding: utf-8 -*-
import requests
import plexapi
from plexapi.exceptions import NotFound
from plexapi.base import PlexObject

"""
You can work with Mobile Sync on other devices straight away, but if you'd like to use your app as sync-target you
need to init some variables.

Example:
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
    to explicitly specify that your app supports `sync-target`
"""


class SyncItem(PlexObject):
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
        self.machineIdentifier = data.find('Server').get('machineIdentifier')
        self.status = Status(self._server, data.find('Status'))
        self.MediaSettings = data.find('MediaSettings').attrib.copy()
        self.policy = data.find('Policy').attrib.copy()
        self.location = data.find('Location').attrib.copy()

    def server(self):
        server = [s for s in self._server.resources() if s.clientIdentifier == self.machineIdentifier]
        if 0 == len(server):
            raise NotFound('Unable to find server with uuid %s' % self.machineIdentifier)
        return server[0]

    def getMedia(self):
        server = self.server().connect()
        key = '/sync/items/%s' % self.id
        return server.fetchItems(key)

    def markDownloaded(self, media):
        """
        Mark the file as downloaded within current SyncItem

        :param media:
        :type media: base.Playable
        """
        url = '/sync/%s/item/%s/downloaded' % (self.clientIdentifier, media.ratingKey)
        media._server.query(url, method=requests.put)


class SyncList(PlexObject):
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
        return str(dict(
            itemsCount=self.itemsCount,
            itemsCompleteCount=self.itemsCompleteCount,
            itemsDownloadedCount=self.itemsDownloadedCount,
            itemsReadyCount=self.itemsReadyCount,
            itemsSuccessfulCount=self.itemsSuccessfulCount
        ))
