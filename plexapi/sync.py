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
from plexapi.exceptions import NotFound, BadRequest
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
        self.status = Status(**data.find('Status').attrib)
        self.mediaSettings = MediaSettings(**data.find('MediaSettings').attrib)
        self.policy = Policy(**data.find('Policy').attrib)
        self.location = data.find('Location').attrib.get('uri', '')

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


class Status(object):
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

    def __init__(self, itemsCount, itemsCompleteCount, state, totalSize, itemsDownloadedCount, itemsReadyCount,
                 itemsSuccessfulCount, failureCode, failure):
        self.itemsDownloadedCount = plexapi.utils.cast(int, itemsDownloadedCount)
        self.totalSize = plexapi.utils.cast(int, totalSize)
        self.itemsReadyCount = plexapi.utils.cast(int, itemsReadyCount)
        self.failureCode = failureCode
        self.failure = failure
        self.itemsSuccessfulCount = plexapi.utils.cast(int, itemsSuccessfulCount)
        self.state = state
        self.itemsCompleteCount = plexapi.utils.cast(int, itemsCompleteCount)
        self.itemsCount = plexapi.utils.cast(int, itemsCount)


def __repr__(self):
        return '<%s>:%s' % (self.__class__.__name__, dict(
            itemsCount=self.itemsCount,
            itemsCompleteCount=self.itemsCompleteCount,
            itemsDownloadedCount=self.itemsDownloadedCount,
            itemsReadyCount=self.itemsReadyCount,
            itemsSuccessfulCount=self.itemsSuccessfulCount
        ))


class MediaSettings(object):
    """ Transcoding settings used for all media within :class:`~plexapi.sync.SyncItem`.

        Attributes:
            audioBoost (int): unknown
            maxVideoBitrate (str): unknown, may be empty
            musicBitrate (int): unknown
            photoQuality (int): unknown
            photoResolution (str): maximum photo resolution, formatted as WxH (e.g. `1920x1080`)
            videoResolution (str): maximum video resolution, formatted as WxH (e.g. `1280x720`, may be empty)
            subtitleSize (str): unknown, usually equals to 0, but sometimes empty string
            videoQuality (int): unknown
    """

    def __init__(self, maxVideoBitrate, videoQuality, videoResolution, audioBoost=100, musicBitrate=192,
                 photoQuality=74, photoResolution='1920x1080', subtitleSize=''):
        self.audioBoost = plexapi.utils.cast(int, audioBoost)
        self.maxVideoBitrate = plexapi.utils.cast(int, maxVideoBitrate)
        self.musicBitrate = plexapi.utils.cast(int, musicBitrate)
        self.photoQuality = plexapi.utils.cast(int, photoQuality)
        self.photoResolution = photoResolution
        self.videoResolution = videoResolution
        self.subtitleSize = subtitleSize
        self.videoQuality = plexapi.utils.cast(int, videoQuality)

    @staticmethod
    def create(video_quality):
        """ Create a :class:`~MediaSettings` object, based on provided video quality value

        Raises:
             :class:`plexapi.exceptions.BadRequest` when provided unknown video quality
        """
        if video_quality == VIDEO_QUALITY_ORIGINAL:
            return MediaSettings('', '', '')
        elif video_quality < len(VIDEO_QUALITIES['bitrate']):
            return MediaSettings(VIDEO_QUALITIES['bitrate'][video_quality],
                                 VIDEO_QUALITIES['videoQuality'][video_quality],
                                 VIDEO_QUALITIES['videoResolution'][video_quality])
        else:
            raise BadRequest('Unexpected video quality')


class Policy(object):
    """ Policy of syncing the media.

        Attributes:
            scope (str): can be `count` or `all`
            value (int): valid only when `scope=count`, means amount of media to sync
            unwatched (bool): True means disallow to sync watched media
    """

    def __init__(self, scope, unwatched, value=0):
        self.scope = scope
        self.unwatched = plexapi.utils.cast(bool, unwatched)
        self.value = plexapi.utils.cast(int, value)


VIDEO_QUALITIES = {
    'bitrate': [64, 96, 208, 320, 720, 1500, 2e3, 3e3, 4e3, 8e3, 1e4, 12e3, 2e4],
    'videoResolution': ["220x128", "220x128", "284x160", "420x240", "576x320", "720x480", "1280x720", "1280x720", "1280x720", "1920x1080", "1920x1080", "1920x1080", "1920x1080"],
    'videoQuality': [10, 20, 30, 30, 40, 60, 60, 75, 100, 60, 75, 90, 100],
}

VIDEO_QUALITY_0_2_MBPS = 2
VIDEO_QUALITY_0_3_MBPS = 3
VIDEO_QUALITY_0_7_MBPS = 4
VIDEO_QUALITY_1_5_MBPS_480p = 5
VIDEO_QUALITY_2_MBPS_720p = 6
VIDEO_QUALITY_3_MBPS_720p = 7
VIDEO_QUALITY_4_MBPS_720p = 8
VIDEO_QUALITY_8_MBPS_1080p = 9
VIDEO_QUALITY_10_MBPS_1080p = 10
VIDEO_QUALITY_12_MBPS_1080p = 11
VIDEO_QUALITY_20_MBPS_1080p = 12
VIDEO_QUALITY_ORIGINAL = -1
