# -*- coding: utf-8 -*-
"""
PlexAPI MyPlex
"""
import plexapi, requests
from plexapi import TIMEOUT, log, utils
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.client import PlexClient
from plexapi.server import PlexServer
from requests.status_codes import _codes as codes
from xml.etree import ElementTree


# Your personal MyPlex account and profile information
class MyPlexAccount(object):
    BASEURL = 'https://plex.tv/users/account'
    SIGNIN = 'https://my.plexapp.com/users/sign_in.xml'
    
    def __init__(self, data, initpath=None):
        self.authenticationToken = data.attrib.get('authenticationToken')
        self.certificateVersion = data.attrib.get('certificateVersion')
        self.cloudSyncDevice = data.attrib.get('cloudSyncDevice')
        self.email = data.attrib.get('email')
        self.guest = utils.cast(bool, data.attrib.get('guest'))
        self.home = utils.cast(bool, data.attrib.get('home'))
        self.homeSize = utils.cast(int, data.attrib.get('homeSize'))
        self.id = data.attrib.get('id')
        self.locale = data.attrib.get('locale')
        self.mailing_list_status = data.attrib.get('mailing_list_status')
        self.maxHomeSize = utils.cast(int, data.attrib.get('maxHomeSize'))
        self.queueEmail = data.attrib.get('queueEmail')
        self.queueUid = data.attrib.get('queueUid')
        self.restricted = utils.cast(bool, data.attrib.get('restricted'))
        self.scrobbleTypes = data.attrib.get('scrobbleTypes')
        self.secure = utils.cast(bool, data.attrib.get('secure'))
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.username = data.attrib.get('username')
        self.uuid = data.attrib.get('uuid')
        
        # TODO: Complete these items!
        self.subscriptionActive = None  # renamed on server
        self.subscriptionStatus = None  # renamed on server
        self.subscriptionPlan = None  # renmaed on server
        self.subscriptionFeatures = None  # renamed on server
        self.roles = None
        self.entitlements = None
        
    def __repr__(self):
        return '<%s:%s:%s>' % (self.__class__.__name__, self.id, self.username.encode('utf8'))

    def devices(self):
        return _listItems(MyPlexDevice.BASEURL, self.authenticationToken, MyPlexDevice)
        
    def device(self, name):
        return _findItem(self.devices(), name)

    def resources(self):
        return _listItems(MyPlexResource.BASEURL, self.authenticationToken, MyPlexResource)

    def resource(self, name):
        return _findItem(self.resources(), name)
        
    def users(self):
        return _listItems(MyPlexUser.BASEURL, self.authenticationToken, MyPlexUser)
        
    def user(self, email):
        return _findItem(self.users(), email, ['username', 'email'])

    @classmethod
    def signin(cls, username, password):
        if 'X-Plex-Token' in plexapi.BASE_HEADERS:
            del plexapi.BASE_HEADERS['X-Plex-Token']
        auth = (username, password)
        log.info('POST %s', cls.SIGNIN)
        response = requests.post(cls.SIGNIN, headers=plexapi.BASE_HEADERS, auth=auth, timeout=TIMEOUT)
        if response.status_code != requests.codes.created:
            codename = codes.get(response.status_code)[0]
            if response.status_code == 401:
                raise Unauthorized('(%s) %s' % (response.status_code, codename))
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = ElementTree.fromstring(response.text.encode('utf8'))
        return cls(data, cls.SIGNIN)


# Not to be confused with the MyPlexAccount, this represents 
# non-signed in users such as friends and linked accounts.
class MyPlexUser(object):
    BASEURL = 'https://plex.tv/api/users/'
    
    def __init__(self, data, initpath=None):
        self.allowCameraUpload = utils.cast(bool, data.attrib.get('allowCameraUpload'))
        self.allowChannels = utils.cast(bool, data.attrib.get('allowChannels'))
        self.allowSync = utils.cast(bool, data.attrib.get('allowSync'))
        self.email = data.attrib.get('email')
        self.filterAll = data.attrib.get('filterAll')
        self.filterMovies = data.attrib.get('filterMovies')
        self.filterMusic = data.attrib.get('filterMusic')
        self.filterPhotos = data.attrib.get('filterPhotos')
        self.filterTelevision = data.attrib.get('filterTelevision')
        self.home = utils.cast(bool, data.attrib.get('home'))
        self.id = utils.cast(int, data.attrib.get('id'))
        self.protected = utils.cast(bool, data.attrib.get('protected'))
        self.recommendationsPlaylistId = data.attrib.get('recommendationsPlaylistId')
        self.restricted = data.attrib.get('restricted')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.username = data.attrib.get('username')
        
    def __repr__(self):
        return '<%s:%s:%s>' % (self.__class__.__name__, self.id, self.username)
    

class MyPlexResource(object):
    BASEURL = 'https://plex.tv/api/resources?includeHttps=1'

    def __init__(self, data):
        self.name = data.attrib.get('name')
        self.accessToken = data.attrib.get('accessToken')
        self.product = data.attrib.get('product')
        self.productVersion = data.attrib.get('productVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.device = data.attrib.get('device')
        self.clientIdentifier = data.attrib.get('clientIdentifier')
        self.createdAt = utils.toDatetime(data.attrib.get('createdAt'))
        self.lastSeenAt = utils.toDatetime(data.attrib.get('lastSeenAt'))
        self.provides = data.attrib.get('provides')
        self.owned = utils.cast(bool, data.attrib.get('owned'))
        self.home = utils.cast(bool, data.attrib.get('home'))
        self.synced = utils.cast(bool, data.attrib.get('synced'))
        self.presence = utils.cast(bool, data.attrib.get('presence'))
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
        self.port = utils.cast(int, data.attrib.get('port'))
        self.uri = data.attrib.get('uri')
        self.local = utils.cast(bool, data.attrib.get('local'))
        self.httpuri = 'http://%s:%s' % (self.address, self.port)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.uri.encode('utf8'))


class MyPlexDevice(object):
    BASEURL = 'https://plex.tv/devices.xml'

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
        self.provides = data.attrib.get('provides')
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


def _findItem(items, value, attrs=None):
    attrs = attrs or ['name']
    for item in items:
        for attr in attrs:
            if value.lower() == getattr(item, attr).lower():
                return item
    raise NotFound('Unable to find item %s' % value)


def _listItems(url, token, cls):
    headers = plexapi.BASE_HEADERS
    headers['X-Plex-Token'] = token
    log.info('GET %s?X-Plex-Token=%s', url, token)
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    data = ElementTree.fromstring(response.text.encode('utf8'))
    return [cls(elem) for elem in data]
