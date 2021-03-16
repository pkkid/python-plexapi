# -*- coding: utf-8 -*-
import os
from typing import List
from urllib.parse import quote_plus, urlencode
from datetime import datetime
import requests

from plexapi import media, utils, settings, library
from plexapi.base import PlexObject, Playable, PlexPartialObject
from plexapi.exceptions import BadRequest, NotFound
from plexapi.media import Session
from plexapi.video import Video
from requests.status_codes import _codes as codes


@utils.registerPlexObject
class IPTVChannel(Video):
    """ Represents a single IPTVChannel."""

    TAG = 'Directory'
    TYPE = 'channel'
    METADATA_TYPE = 'channel'

    def _loadData(self, data):
        self._data = data
        self.art = data.attrib.get('art')
        self.guid = data.attrib.get('id')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.type = data.attrib.get('type')
        self.items = self.findItems(data)


@utils.registerPlexObject
class Recording(Video):
    """ Represents a single Recording."""

    TAG = 'MediaSubscription'

    def _loadData(self, data):
        self._data = data
        self.key = data.attrib.key('key')
        self.type = data.attrib.key('type')
        self.targetLibrarySectionId = data.attrib.get('targetLibrarySectionId')
        self.createdAt = utils.toDatetime(data.attrib.get('createdAt'))
        self.title = data.attrib.get('title')
        self.items = self.findItems(data)

    def delete(self):
        self._server.query(key='/media/subscription/' + self.key, method=self._server._session.delete)


@utils.registerPlexObject
class ScheduledRecording(Video):
    """ Represents a single ScheduledRecording."""

    TAG = 'MediaGrabOperation'

    def _loadData(self, data):
        self._data = data
        self.mediaSubscriptionID = data.attrib.get('mediaSubscriptionID')
        self.mediaIndex = data.attrib.get('mediaIndex')
        self.key = data.attrib.key('key')
        self.grabberIdentifier = data.attrib.get('grabberIdentifier')
        self.grabberProtocol = data.attrib.get('grabberProtocol')
        self.deviceID = data.attrib.get('deviceID')
        self.status = data.attrib.get('status')
        self.provider = data.attrib.get('provider')
        self.items = self.findItems(data)


@utils.registerPlexObject
class Setting(PlexObject):
    """ Represents a single DVRDevice Setting."""

    TAG = 'Setting'

    def _loadData(self, data):
        self._data = data
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
        self.items = self.findItems(data)


@utils.registerPlexObject
class DVRChannel(PlexObject):
    """ Represents a single DVRDevice DVRChannel."""

    TAG = 'ChannelMapping'

    def _loadData(self, data):
        self._data = data
        self.channelKey = data.attrib.get('channelKey')
        self.deviceIdentifier = data.attrib.get('deviceIdentifier')
        self.enabled = utils.cast(int, data.attrib.get('enabled'))
        self.lineupIdentifier = data.attrib.get('lineupIdentifier')
        self.items = self.findItems(data)


@utils.registerPlexObject
class DVRDevice(PlexObject):
    """ Represents a single DVRDevice."""

    TAG = 'Device'

    def _loadData(self, data):
        self._data = data
        self.parentID = data.attrib.get('parentID')
        self.key = data.attrib.get('key', '')
        self.uuid = data.attrib.get('uuid')
        self.uri = data.attrib.get('uri')
        self.protocol = data.attrib.get('protocol')
        self.status = data.attrib.get('status')
        self.state = data.attrib.get('state')
        self.lastSeenAt = utils.toDatetime(data.attrib.get('lastSeenAt'))
        self.make = data.attrib.get('make')
        self.model = data.attrib.get('model')
        self.modelNumber = data.attrib.get('modelNumber')
        self.source = data.attrib.get('source')
        self.sources = data.attrib.get('sources')
        self.thumb = data.attrib.get('thumb')
        self.tuners = utils.cast(int, data.attrib.get('tuners'))
        self.items = self.findItems(data)


@utils.registerPlexObject
class DVR(DVRDevice):
    """ Represents a single DVR."""

    TAG = 'Dvr'

    def _loadData(self, data):
        self._data = data
        self.key = utils.cast(int, data.attrib.get('key'))
        self.uuid = data.attrib.get('uuid')
        self.language = data.attrib.get('language')
        self.lineupURL = data.attrib.get('lineup')
        self.title = data.attrib.get('lineupTitle')
        self.country = data.attrib.get('country')
        self.refreshTime = utils.toDatetime(data.attrib.get('refreshedAt'))
        self.epgIdentifier = data.attrib.get('epgIdentifier')
        self.items = self.findItems(data)


class LiveTV(PlexObject):
    def __init__(self, server, data, session=None, token=None):
        self._token = token
        self._session = session or requests.Session()
        self._server = server
        self._dvrs = []  # cached DVR objects
        super().__init__(server, data)

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self._data = data
        self.cloud_key = data.attrib.get('machineIdentifier')

    def _get_cloud_key(self):
        url = self._server.url(key='/tv.plex.providers.epg.cloud', includeToken=True)
        data = self._session.get(url=url).json()
        if data and data.get('MediaContainer') and data['MediaContainer'].get('Directory')\
                and len(data['MediaContainer']['Directory']) > 1:
            self.cloud_key = data.get('MediaContainer').get('Directory')[1].get('title')
            return self.cloud_key
        return None

    @property
    def dvrs(self) -> List[DVR]:
        """ Returns a list of :class:`~plexapi.livetv.DVR` objects available to your server.
        """
        if not self._dvrs:
            self._dvrs = self.fetchItems('/livetv/dvrs')
        return self._dvrs

    @property
    def sessions(self) -> List[Session]:
        """ Returns a list of all active live tv session (currently playing) media objects.
        """
        return self.fetchItems('/livetv/sessions')

    @property
    def directories(self):
        """ Returns a list of all :class:`~plexapi.livetv.Directory` objects available to your server.
        """
        return self._server.fetchItems(self.cloud_key + '/hubs/discover')

    def _guide_items(self, grid_type: int, beginsAt: datetime = None, endsAt: datetime = None):
        key = '%s/grid?type=%s' % (self.cloud_key, grid_type)
        if beginsAt:
            key += '&beginsAt%3C=%s' % utils.datetimeToEpoch(beginsAt)  # %3C is <, so <=
        if endsAt:
            key += '&endsAt%3E=%s' % utils.datetimeToEpoch(endsAt)  # %3E is >, so >=
        return self._server.fetchItems(key)

    def movies(self, beginsAt: datetime = None, endsAt: datetime = None):
        """ Returns a list of all :class:`~plexapi.video.Movie` items on the guide.

            Parameters:
                grid_type (int): 1 for movies, 4 for shows
                beginsAt (datetime): Limit results to beginning after UNIX timestamp (epoch).
                endsAt (datetime): Limit results to ending before UNIX timestamp (epoch).
        """
        return self._guide_items(grid_type=1, beginsAt=beginsAt, endsAt=endsAt)

    def shows(self, beginsAt: datetime = None, endsAt: datetime = None):
        """ Returns a list of all :class:`~plexapi.video.Show` items on the guide.

            Parameters:
                beginsAt (datetime): Limit results to beginning after UNIX timestamp (epoch).
                endsAt (datetime): Limit results to ending before UNIX timestamp (epoch).
        """
        return self._guide_items(grid_type=4, beginsAt=beginsAt, endsAt=endsAt)

    def guide(self, beginsAt: datetime = None, endsAt: datetime = None):
        """ Returns a list of all media items on the guide. Items may be any of
            :class:`~plexapi.video.Movie`, :class:`~plexapi.video.Show`.

            Parameters:
                beginsAt (datetime): Limit results to beginning after UNIX timestamp (epoch).
                endsAt (datetime): Limit results to ending before UNIX timestamp (epoch).
        """
        all_movies = self.movies(beginsAt, endsAt)
        return all_movies
        # Potential show endpoint currently hanging, do not use
        # all_shows = self.shows(beginsAt, endsAt)
        # return all_movies + all_shows

    @property
    def recordings(self):
        return self.fetchItems('/media/subscriptions/scheduled')

    @property
    def scheduled(self):
        return self.fetchItems('/media/subscriptions')
