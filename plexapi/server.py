"""
PlexServer
"""
import requests, urllib
from requests.status_codes import _codes as codes
from plexapi import BASE_HEADERS, TIMEOUT
from plexapi import log, video
from plexapi.client import Client
from plexapi.exceptions import BadRequest, NotFound
from plexapi.library import Library
from plexapi.myplex import MyPlexAccount
from plexapi.playqueue import PlayQueue
from xml.etree import ElementTree

TOTAL_QUERIES = 0


class PlexServer(object):
    
    def __init__(self, address='localhost', port=32400, token=None):
        self.address = self._cleanAddress(address)
        self.port = port
        self.token = token
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
        self.transcoderActiveVideoSessions = int(data.attrib.get('transcoderActiveVideoSessions'))
        self.updatedAt = int(data.attrib.get('updatedAt'))
        self.version = data.attrib.get('version')

    def __repr__(self):
        return '<%s:%s:%s>' % (self.__class__.__name__, self.address, self.port)

    def _cleanAddress(self, address):
        address = address.lower().strip('/')
        if address.startswith('http://'):
            address = address[8:]
        return address

    def _connect(self):
        try:
            return self.query('/')
        except Exception, err:
            log.error('%s:%s: %s', self.address, self.port, err)
            raise NotFound('No server found at: %s:%s' % (self.address, self.port))

    @property
    def library(self):
        return Library(self, self.query('/library/'))

    def account(self):
        data = self.query('/myplex/account')
        return MyPlexAccount(self, data)

    def clients(self):
        items = []
        for elem in self.query('/clients'):
            items.append(Client(self, elem))
        return items

    def client(self, name):
        for elem in self.query('/clients'):
            if elem.attrib.get('name').lower() == name.lower():
                return Client(self, elem)
        raise NotFound('Unknown client name: %s' % name)

    def createPlayQueue(self, video):
        return PlayQueue.create(self, video)

    def headers(self):
        headers = BASE_HEADERS
        if self.token:
            headers['X-Plex-Token'] = self.token
        return headers

    def query(self, path, method=requests.get):
        global TOTAL_QUERIES; TOTAL_QUERIES += 1
        url = self.url(path)
        log.info('%s %s%s', method.__name__.upper(), url, '?X-Plex-Token=%s' % self.token if self.token else '')
        response = method(url, headers=self.headers(), timeout=TIMEOUT)
        if response.status_code not in [200, 201]:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None

    def search(self, query, videotype=None):
        query = urllib.quote(query)
        items = video.list_items(self, '/search?query=%s' % query)
        if videotype:
            return [item for item in items if item.type == videotype]
        return items

    def url(self, path):
        return 'http://%s:%s/%s' % (self.address, self.port, path.lstrip('/'))
