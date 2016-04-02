# -*- coding: utf-8 -*-
"""
PlexAPI MyPlex
"""
import plexapi, requests
from plexapi import TIMEOUT, log, utils
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.client import PlexClient
from plexapi.server import PlexServer
from plexapi.utils import cast, toDatetime
from requests.status_codes import _codes as codes
from xml.etree import ElementTree

MYPLEX_SIGNIN = 'https://my.plexapp.com/users/sign_in.xml'
MYPLEX_DEVICES = 'https://plex.tv/devices.xml'
MYPLEX_RESOURCES = 'https://plex.tv/api/resources?includeHttps=1'


class MyPlexUser(object):

    def __init__(self, data, initpath=None):
        self.initpath = initpath
        self.email = data.attrib.get('email')
        self.id = data.attrib.get('id')
        self.thumb = data.attrib.get('thumb')
        self.username = data.attrib.get('username')
        self.title = data.attrib.get('title')
        self.cloudSyncDevice = data.attrib.get('cloudSyncDevice')
        self.authenticationToken = data.attrib.get('authenticationToken')
        self.queueEmail = data.attrib.get('queueEmail')
        self.queueUid = data.attrib.get('queueUid')

    def devices(self):
        return _listItems(MYPLEX_DEVICES, self.authenticationToken, MyPlexDevice)
        
    def device(self, name):
        return _findItem(self.devices(), name)

    def resources(self):
        return _listItems(MYPLEX_RESOURCES, self.authenticationToken, MyPlexResource)

    def resource(self, name):
        return _findItem(self.resources(), name)

    @classmethod
    def signin(cls, username, password):
        if 'X-Plex-Token' in plexapi.BASE_HEADERS:
            del plexapi.BASE_HEADERS['X-Plex-Token']
        auth = (username, password)
        log.info('POST %s', MYPLEX_SIGNIN)
        response = requests.post(MYPLEX_SIGNIN, headers=plexapi.BASE_HEADERS, auth=auth, timeout=TIMEOUT)
        if response.status_code != requests.codes.created:
            codename = codes.get(response.status_code)[0]
            if response.status_code == 401:
                raise Unauthorized('(%s) %s' % (response.status_code, codename))
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = ElementTree.fromstring(response.text.encode('utf8'))
        return cls(data)


class MyPlexAccount(object):

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

    def resources(self):
        return _listItems(MYPLEX_RESOURCES, self.authToken, MyPlexResource)

    def resource(self, name):
        return _findItem(self.resources(), name)


class MyPlexResource(object):

    def __init__(self, data):
        self.name = data.attrib.get('name')
        self.accessToken = data.attrib.get('accessToken')
        self.product = data.attrib.get('product')
        self.productVersion = data.attrib.get('productVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.device = data.attrib.get('device')
        self.clientIdentifier = data.attrib.get('clientIdentifier')
        self.createdAt = toDatetime(data.attrib.get('createdAt'))
        self.lastSeenAt = toDatetime(data.attrib.get('lastSeenAt'))
        self.provides = data.attrib.get('provides')
        self.owned = cast(bool, data.attrib.get('owned'))
        self.home = cast(bool, data.attrib.get('home'))
        self.synced = cast(bool, data.attrib.get('synced'))
        self.presence = cast(bool, data.attrib.get('presence'))
        self.connections = [ResourceConnection(elem) for elem in data if elem.tag == 'Connection']

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name.encode('utf8'))

    def connect(self, ssl=None):
        # Sort connections from (https, local) to (http, remote)
        # Only check non-local connections unless we own the resource
        forcelocal = lambda c: self.owned or c.local
        connections = sorted(self.connections, key=lambda c:c.local, reverse=True)
        https = [c.uri for c in self.connections if forcelocal(c)]
        http = [c.httpuri for c in self.connections if forcelocal(c)]
        connections = https + http
        # Try connecting to all known resource connections in parellel, but
        # only return the first server (in order) that provides a response.
        listargs = [[c] for c in connections]
        results = utils.threaded(self._connect, listargs)
        # At this point we have a list of result tuples containing (url, token, PlexServer)
        # or (url, token, None) in the case a connection could not be established.
        for url, token, result in results:
            okerr = 'OK' if result else 'ERR'
            log.info('Testing resource connection: %s?X-Plex-Token=%s %s', url, token, okerr)
        results = list(filter(None, [r[2] for r in results if r]))
        if not results:
            raise NotFound('Unable to connect to resource: %s' % self.name)
        log.info('Connecting to server: %s?X-Plex-Token=%s', results[0].baseurl, results[0].token)
        return results[0]

    def _connect(self, url, results, i):
        try:
            results[i] = (url, self.accessToken, PlexServer(url, self.accessToken))
        except NotFound:
            results[i] = (url, self.accessToken, None)


class ResourceConnection(object):

    def __init__(self, data):
        self.protocol = data.attrib.get('protocol')
        self.address = data.attrib.get('address')
        self.port = cast(int, data.attrib.get('port'))
        self.uri = data.attrib.get('uri')
        self.local = cast(bool, data.attrib.get('local'))
        self.httpuri = 'http://%s:%s' % (self.address, self.port)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.uri.encode('utf8'))


class MyPlexDevice(object):

    def __init__(self, data):
        self.name = data.attrib.get('name')
        self.publicAddress = data.attrib.get('publicAddress')
        self.product = data.attrib.get('product')
        self.productVersion = data.attrib.get('productVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.device = data.attrib.get('device')
        self.model = data.attrib.get('model')
        self.vendor = data.attrib.get('vendor')
        self.provides = data.attrib.get('provides').split(',')
        self.clientIdentifier = data.attrib.get('clientIdentifier')
        self.version = data.attrib.get('version')
        self.id = data.attrib.get('id')
        self.token = data.attrib.get('token')
        self.screenResolution = data.attrib.get('screenResolution')
        self.screenDensity = data.attrib.get('screenDensity')
        self.connections = [connection.attrib.get('uri') for connection in data.iter('Connection')]

    def __repr__(self):
        return '<%s:%s:%s>' % (self.__class__.__name__, self.name.encode('utf8'), self.product.encode('utf8'))

    def connect(self, ssl=None):
        # Try connecting to all known resource connections in parellel, but
        # only return the first server (in order) that provides a response.
        listargs = [[c] for c in self.connections]
        results = utils.threaded(self._connect, listargs)
        # At this point we have a list of result tuples containing (url, token, PlexServer)
        # or (url, token, None) in the case a connection could not be established.
        for url, token, result in results:
            okerr = 'OK' if result else 'ERR'
            log.info('Testing device connection: %s?X-Plex-Token=%s %s', url, token, okerr)
        results = list(filter(None, [r[2] for r in results if r]))
        if not results:
            raise NotFound('Unable to connect to resource: %s' % self.name)
        log.info('Connecting to server: %s?X-Plex-Token=%s', results[0].baseurl, results[0].token)
        return results[0]

    def _connect(self, url, results, i):
        try:
            results[i] = (url, self.token, PlexClient(url, self.token))
        except NotFound as err:
            print(err)
            results[i] = (url, self.token, None)


def _findItem(items, name):
    for item in items:
        if name.lower() == item.name.lower():
            return item
    raise NotFound('Unable to find item: %s' % name)


def _listItems(url, token, cls):
    headers = plexapi.BASE_HEADERS
    headers['X-Plex-Token'] = token
    log.info('GET %s?X-Plex-Token=%s', url, token)
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    data = ElementTree.fromstring(response.text.encode('utf8'))
    return [cls(elem) for elem in data]
