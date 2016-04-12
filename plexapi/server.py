# -*- coding: utf-8 -*-
"""
PlexServer
"""
import requests
from requests.status_codes import _codes as codes
from plexapi import BASE_HEADERS, TIMEOUT
from plexapi import log, utils
from plexapi import audio, video, photo, playlist  # noqa; required
from plexapi.compat import quote
from plexapi.client import PlexClient
from plexapi.exceptions import BadRequest, NotFound
from plexapi.library import Library
from plexapi.playlist import Playlist
from plexapi.playqueue import PlayQueue
from xml.etree import ElementTree

DEFAULT_BASEURL = 'http://localhost:32400'


class PlexServer(object):

    def __init__(self, baseurl=None, token=None, session=None):
        self.baseurl = baseurl or DEFAULT_BASEURL
        self.token = token
        self.session = session or requests.Session()
        data = self._connect()
        self.friendlyName = data.attrib.get('friendlyName')
        self.machineIdentifier = data.attrib.get('machineIdentifier')
        self.myPlex = bool(data.attrib.get('myPlex'))
        self.myPlexMappingState = data.attrib.get('myPlexMappingState')
        self.myPlexSigninState = data.attrib.get('myPlexSigninState')
        self.myPlexSubscription = data.attrib.get('myPlexSubscription')
        self.myPlexUsername = data.attrib.get('myPlexUsername')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.transcoderActiveVideoSessions = int(data.attrib.get('transcoderActiveVideoSessions', 0))
        self.updatedAt = int(data.attrib.get('updatedAt', 0))
        self.version = data.attrib.get('version')
        self._library = None  # cached library

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.baseurl)

    def _connect(self):
        try:
            return self.query('/')
        except Exception as err:
            log.error('%s: %s', self.baseurl, err)
            raise NotFound('No server found at: %s' % self.baseurl)

    @property
    def library(self):
        if not self._library:
            self._library = Library(self, self.query('/library/'))
        return self._library

    def account(self):
        data = self.query('/myplex/account')
        return Account(self, data)

    def clients(self):
        items = []
        for elem in self.query('/clients'):
            baseurl = 'http://%s:%s' % (elem.attrib['address'], elem.attrib['port'])
            items.append(PlexClient(baseurl, server=self, data=elem))
        return items

    def client(self, name):
        for elem in self.query('/clients'):
            if elem.attrib.get('name').lower() == name.lower():
                baseurl = 'http://%s:%s' % (elem.attrib['address'], elem.attrib['port'])
                return PlexClient(baseurl, server=self, data=elem)
        raise NotFound('Unknown client name: %s' % name)

    def createPlaylist(self, title, items):
        return Playlist.create(self, title, items)

    def createPlayQueue(self, item):
        return PlayQueue.create(self, item)

    def headers(self):
        headers = BASE_HEADERS
        if self.token:
            headers['X-Plex-Token'] = self.token
        return headers
        
    def history(self):
        return utils.listItems(self, '/status/sessions/history/all')
        
    def playlists(self):
        # TODO: Add sort and type options?
        # /playlists/all?type=15&sort=titleSort%3Aasc&playlistType=video&smart=0
        return utils.listItems(self, '/playlists')
        
    def playlist(self, title=None):  # noqa
        for item in self.playlists():
            if item.title == title:
                return item
        raise NotFound('Invalid playlist title: %s' % title)

    def query(self, path, method=None, headers=None, **kwargs):
        url = self.url(path)
        method = method or self.session.get
        log.info('%s %s', method.__name__.upper(), url)
        headers = dict(self.headers(), **(headers or {}))
        response = method(url, headers=headers, timeout=TIMEOUT, **kwargs)
        if response.status_code not in [200, 201]:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None
        
    def search(self, query, mediatype=None):
        """ Searching within a library section is much more powerful. """
        items = utils.listItems(self, '/search?query=%s' % quote(query))
        if mediatype:
            return [item for item in items if item.type == mediatype]
        return items

    def sessions(self):
        return utils.listItems(self, '/status/sessions')

    def url(self, path):
        if self.token:
            delim = '&' if '?' in path else '?'
            return '%s%s%sX-Plex-Token=%s' % (self.baseurl, path, delim, self.token)
        return '%s%s' % (self.baseurl, path)


# This is the locally cached MyPlex account information. The properties provided don't match
# the myplex.MyPlexAccount object very well. I believe this is here because access to myplex
# is not required to get basic plex information.
class Account(object):

    def __init__(self, server, data):
        self.authToken = data.attrib.get('authToken')
        self.username = data.attrib.get('username')
        self.mappingState = data.attrib.get('mappingState')
        self.mappingError = data.attrib.get('mappingError')
        self.mappingErrorMessage = data.attrib.get('mappingErrorMessage')
        self.signInState = data.attrib.get('signInState')
        self.publicAddress = data.attrib.get('publicAddress')
        self.publicPort = data.attrib.get('publicPort')
        self.privateAddress = data.attrib.get('privateAddress')
        self.privatePort = data.attrib.get('privatePort')
        self.subscriptionFeatures = data.attrib.get('subscriptionFeatures')
        self.subscriptionActive = data.attrib.get('subscriptionActive')
        self.subscriptionState = data.attrib.get('subscriptionState')
