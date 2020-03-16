# -*- coding: utf-8 -*-
from plexapi import X_PLEX_CONTAINER_SIZE, log, utils
from plexapi.base import PlexObject
from plexapi.compat import unquote, urlencode, quote_plus
from plexapi.media import MediaTag
from plexapi.exceptions import BadRequest, NotFound


class LiveTV(PlexObject):
    def _loadData(self, data):
        self._data = data
        self.cloudKey = None
        self.identifier = data.attrib.get('identifier')
        self.size = data.attrib.get('size')

    def cloudKey(self):
        if not self.cloudKey:
            res = self._server.query(key='/tv.plex.providers.epg.cloud')
            if res:
                self.cloudKey = res.attrib.get('title')
        return self.cloudKey

    def hubs(self):
        res = self._server.query(key='/{}/hubs/discover'.format(self.cloudKey()))
        if res:
            return [Hub(item) for item in res.attrib.get('Hub')]
        return []

    def hub(self, identifier=None):
        hubs = self.hubs()
        for hub in hubs:
            if hub.identifier == identifier:
                return hub
        return None

    def dvrSchedule(self):
        res = self._server.query(key='/media/subscriptions/scheduled')
        if res:
            return DVRSchedule(res.attrib.get('MediaContainer'))
        return None

    def dvrItems(self):
        res = self._server.query(key='/media/subscriptions')
        if res:
            return [DVRItem(item) for item in res.attrib.get('MediaSubscription')]
        return []

    def dvrItem(self, title=None):
        items = self.dvrItems()
        for item in items:
            if item.title == title:
                return item
        return None

    def homepageItems(self):
        res = self._server.query(key='/hubs')
        if res:
            return [Hub(item) for item in res.attrib.get('Hub')]
        return []

    def homepageItem(self, title=None):
        items = self.homepageItems()
        for item in items:
            if item.title == title:
                return item
        return None

    def liveTVSessions(self):
        res = self._server.query(key='/livetv/sessions')
        if res:
            return [TVSession(item) for item in res.attrib.get('Metadata')]
        return []

    def liveTVSession(self, key=None):
        items = self.liveTVSessions()
        for item in items:
            if item.key == key:
                return item
        return None

    def dvrs(self):
        res = self._server.query(key='/livetv/dvrs')
        if res:
            return [DVR(item) for item in res.attrib.get('Dvr')]
        return []

    def dvr(self, title=None):
        items = self.dvrs()
        for item in items:
            if item.title == title:
                return item
        return None


class Hub:
    def __init__(self, data):
        self.data = data
        self.key = data.attrib.get('hubKey')
        self.title = data.attrib.get('title')
        self.type = data.attrib.get('type')
        self.identifier = data.attrib.get('hubIdentifier')
        self.context = data.attrib.get('context')
        self.size = data.attrib.get('size')
        self.more = data.attrib.get('more')
        self.promoted = data.attrib.get('promoted')
        if data.attrib.get('Metadata'):
            self.items = [MediaItem(item) for item in self.data.attrib.get('Metadata')]


class DVR:
    def __init__(self, data):
        self.data = data
        self.key = data.attrib.get('key')
        self.uuid = data.attrib.get('uuid')
        self.language = data.attrib.get('language')
        self.lineupURL = data.attrib.get('lineup')
        self.title = data.attrib.get('lineupTitle')
        self.country = data.attrib.get('country')
        self.refreshTime = data.attrib.get('refreshedAt')
        self.epgIdentifier = data.attrib.get('epgIdentifier')
        self.device = [Device(device) for device in data.attrib.get('Device')]


class DVRSchedule:
    def __init__(self, data):
        self.data = data
        self.count = data.attrib.get('size')
        if data.attrib.get('MediaGrabOperation'):
            self.items = [DVRItem(item) for item in data.attrib.get('MediaGrabOperation')]


class DVRItem:
    def __init__(self, data):
        self.data = data
        self.type = data.attrib.get('type')
        self.targetLibrarySectionID = data.attrib.get('targetLibrarySectionID')
        self.created = data.attrib.get('createdAt')
        self.title = data.attrib.get('title')
        self.mediaSubscriptionID = data.attrib.get('mediaSubscriptionID')
        self.mediaIndex = data.attrib.get('mediaIndex')
        self.key = data.attrib.get('key')
        self.grabberIdentifier = data.attrib.get('grabberIdentifier')
        self.grabberProtocol = data.attrib.get('grabberProtocol')
        self.deviceID = data.attrib.get('deviceID')
        self.status = data.attrib.get('status')
        self.provider = data.attrib.get('provider')
        if data.attrib.get('Video'):
            self.video = Video(data.attrib.get('Video'))

    def delete(self):
        self._server.query(key='/media/subscription/{}'.format(self.mediaSubscriptionID), method=self._server._session.delete)


class TVSession:
    def __init__(self, data):
        self.data = data
        self.ratingKey = data.attrib.get('ratingKey')
        self.guid = data.attrib.get('guid')
        self.type = data.attrib.get('type')
        self.title = data.attrib.get('title')
        self.summary = data.attrib.get('title')
        self.ratingCount = data.attrib.get('ratingCount')
        self.year = data.attrib.get('year')
        self.added = data.attrib.get('addedAt')
        self.genuineMediaAnalysis = data.attrib.get('genuineMediaAnalysis')
        self.grandparentThumb = data.attrib.get('grandparentThumb')
        self.grandparentTitle = data.attrib.get('grandparentTitle')
        self.key = data.attrib.get('key')
        self.live = data.attrib.get('live')
        self.parentIndex = data.attrib.get('parentIndex')
        self.media = [MediaItem(item) for item in data.attrib.get('Media')]


class Device:
    def __init__(self, data):
        self.data = data
        self.parentID = data.attrib.get('parentID')
        self.key = data.attrib.get('key')
        self.uuid = data.attrib.get('uuid')
        self.uri = data.attrib.get('uri')
        self.protocol = data.attrib.get('protocol')
        self.status = data.attrib.get('status')
        self.state = data.attrib.get('state')
        self.lastSeen = data.attrib.get('lastSeenAt')
        self.make = data.attrib.get('make')
        self.model = data.attrib.get('model')
        self.modelNumber = data.attrib.get('modelNumber')
        self.source = data.attrib.get('source')
        self.sources = data.attrib.get('sources')
        self.thumb = data.attrib.get('thumb')
        self.tuners = data.attrib.get('tuners')
        if data.attrib.get('Channels'):
            self.channels = [Channel(channel) for channel in data.attrib.get('Channels')]
        if data.attrib.get('Setting'):
            self.settings = [Setting(setting) for setting in data.attrib.get('Setting')]


class Channel:
    def __init__(self, data):
        self.data = data
        self.deviceId = data.attrib.get('deviceIdentifier')
        self.enabled = data.attrib.get('enabled')
        self.lineupId = data.attrib.get('lineupIdentifier')


class Setting:
    def __init__(self, data):
        self.data = data
        self.id = data.attrib.get('id')
        self.label = data.attrib.get('label')
        self.summary = data.attrib.get('summary')
        self.type = data.attrib.get('type')
        self.default = data.attrib.get('default')
        self.value = data.attrib.get('value')
        self.hidden = data.attrib.get('hidden')
        self.advanced = data.attrib.get('advanced')
        self.group = data.attrib.get('group')
        self.enumValues = data.attrib.get('enumValues')


class MediaFile:
    def __init__(self, data):
        self.data = data
        self.id = data.attrib.get('id')
        self.duration = data.attrib.get('duration')
        self.audioChannels = data.attrib.get('audioChannels')
        self.videoResolution = data.attrib.get('videoResolution')
        self.channelCallSign = data.attrib.get('channelCallSign')
        self.channelIdentifier = data.attrib.get('channelIdentifier')
        self.channelThumb = data.attrib.get('channelThumb')
        self.channelTitle = data.attrib.get('channelTitle')
        self.protocol = data.attrib.get('protocol')
        self.begins = data.attrib.get('beginsAt')
        self.ends = data.attrib.get('endsAt')
        self.onAir = data.attrib.get('onAir')
        self.channelID = data.attrib.get('channelID')
        self.origin = data.attrib.get('origin')
        self.uuid = data.attrib.get('uuid')
        self.container = data.attrib.get('container')
        self.startOffsetSeconds = data.attrib.get('startOffsetSeconds')
        self.endOffsetSeconds = data.attrib.get('endOffsetSeconds')
        self.premiere = data.attrib.get('premiere')


class MediaItem:
    def __init__(self, data):
        self.data = data
        self.ratingKey = data.attrib.get('ratingKey')
        self.key = data.attrib.get('key')
        self.skipParent = data.attrib.get('skipParent')
        self.guid = data.attrib.get('guid')
        self.parentGuid = data.attrib.get('parentGuid')
        self.grandparentGuid = data.attrib.get('grandparentGuid')
        self.type = data.attrib.get('type')
        self.title = data.attrib.get('title')
        self.grandparentKey = data.attrib.get('grandparentKey')
        self.grandparentTitle = data.attrib.get('grandparentTitle')
        self.parentTitle = data.attrib.get('parentTitle')
        self.summary = data.attrib.get('summary')
        self.parentIndex = data.attrib.get('parentIndex')
        self.year = data.attrib.get('year')
        self.grandparentThumb = data.attrib.get('grandparentThumb')
        self.duration = data.attrib.get('duration')
        self.originallyAvailable = data.attrib.get('originallyAvailableAt')
        self.added = data.attrib.get('addedAt')
        self.onAir = data.attrib.get('onAir')
        if data.attrib.get('Media'):
            self.media = [MediaFile(item) for item in data.attrib.get('Media')]
        if data.attrib.get('Genre'):
            self.genres = [Genre(item) for item in data.attrib.get('Genre')]


class Genre:
    def __init__(self, data):
        self.data = data
        self.filter = data.attrib.get('filter')
        self.id = data.attrib.get('id')
        self.tag = data.attrib.get('tag')
