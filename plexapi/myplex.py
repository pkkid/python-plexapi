"""
PlexAPI MyPlex
"""
import plexapi, requests
from requests.status_codes import _codes as codes
from threading import Thread
from xml.etree import ElementTree
from plexapi import TIMEOUT, log
from plexapi.exceptions import BadRequest, NotFound
from plexapi.utils import cast, toDatetime, Connection
from plexapi.sync import SyncItem


class MyPlexUser:
    """ Logs into my.plexapp.com to fetch account and token information. This
        useful to get a token if not on the local network.
    """
    SIGNIN = 'https://my.plexapp.com/users/sign_in.xml'

    def __init__(self, username, password):
        data = self._signin(username, password)
        self.email = data.attrib.get('email')
        self.id = data.attrib.get('id')
        self.thumb = data.attrib.get('thumb')
        self.username = data.attrib.get('username')
        self.title = data.attrib.get('title')
        self.cloudSyncDevice = data.attrib.get('cloudSyncDevice')
        self.authenticationToken = data.attrib.get('authenticationToken')
        self.queueEmail = data.attrib.get('queueEmail')
        self.queueUid = data.attrib.get('queueUid')

    def _signin(self, username, password):
        auth = (username, password)
        log.info('POST %s', self.SIGNIN)
        response = requests.post(self.SIGNIN, headers=plexapi.BASE_HEADERS, auth=auth, timeout=TIMEOUT)
        if response.status_code != requests.codes.created:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data)

    def servers(self):
        return MyPlexServer.fetchServers(self.authenticationToken)

    def getServer(self, nameOrSourceTitle):
        search = nameOrSourceTitle.lower()
        for server in self.servers():
            if server.name and search == server.name.lower(): return server
            if server.sourceTitle and search == server.sourceTitle.lower(): return server
        raise NotFound('Unable to find server: %s' % nameOrSourceTitle)

    def devices(self):
        return MyPlexDevice.fetchDevices(self.authenticationToken)

    def getDevice(self, nameOrClientIdentifier):
        search = nameOrClientIdentifier.lower()
        for device in self.devices():
            device_name = device.name.lower()
            device_cid = device.clientIdentifier.lower()
            if search in (device_name, device_cid):
                return device
        raise NotFound('Unable to find device: %s' % nameOrClientIdentifier)

    def syncDevices(self):
        return filter(lambda x: 'sync-target' in x.provides, self.devices())


class MyPlexAccount:
    """ Represents myPlex account if you already have a connection to a server. """

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

    def servers(self):
        return MyPlexServer.fetchServers(self.authToken)

    def getServer(self, nameOrSourceTitle):
        for server in self.servers():
            if nameOrSourceTitle.lower() in [server.name.lower(), server.sourceTitle.lower()]:
                return server
        raise NotFound('Unable to find server: %s' % nameOrSourceTitle)


class MyPlexServer:
    SERVERS = 'https://plex.tv/pms/servers.xml?includeLite=1'

    def __init__(self, data):
        self.accessToken = data.attrib.get('accessToken')
        self.name = data.attrib.get('name')
        self.address = data.attrib.get('address')
        self.port = cast(int, data.attrib.get('port'))
        self.version = data.attrib.get('version')
        self.scheme = data.attrib.get('scheme')
        self.host = data.attrib.get('host')
        self.localAddresses = data.attrib.get('localAddresses', '').split(',')
        self.machineIdentifier = data.attrib.get('machineIdentifier')
        self.createdAt = toDatetime(data.attrib.get('createdAt'))
        self.updatedAt = toDatetime(data.attrib.get('updatedAt'))
        self.owned = cast(bool, data.attrib.get('owned'))
        self.synced = cast(bool, data.attrib.get('synced'))
        self.sourceTitle = data.attrib.get('sourceTitle', '')
        self.ownerId = cast(int, data.attrib.get('ownerId'))
        self.home = data.attrib.get('home')

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name.encode('utf8'))

    def connect(self):
        # Create a list of addresses to try connecting to.
        # TODO: setup local addresses before external
        devices = MyPlexDevice.fetchDevices(self.accessToken)
        devices = filter(lambda x: x.clientIdentifier == self.machineIdentifier, devices)
        addresses = []
        if len(devices) == 1:
            addresses += devices[0].connections
        else:
            addresses.append(Connection(self.address, self.port))
            if self.owned:
                for local in self.localAddresses:
                    addresses.append(Connection(local, self.port))
        # Attempt to connect to all known addresses in parellel to save time, but
        # only return the first server (in order) that provides a response.
        threads = [None] * len(addresses)
        results = [None] * len(addresses)
        for i in range(len(addresses)):
            args = (addresses[i], results, i)
            threads[i] = Thread(target=self._connect, args=args)
            threads[i].start()
        for thread in threads:
            thread.join()
        results = filter(None, results)
        if results: return results[0]
        raise NotFound('Unable to connect to server: %s' % self.name)

    def _connect(self, address, results, i):
        from plexapi.server import PlexServer
        try:
            results[i] = PlexServer(address.addr, address.port, self.accessToken)
        except NotFound:
            results[i] = None

    @classmethod
    def fetchServers(cls, token):
        headers = plexapi.BASE_HEADERS
        headers['X-Plex-Token'] = token
        log.info('GET %s?X-Plex-Token=%s', cls.SERVERS, token)
        response = requests.get(cls.SERVERS, headers=headers, timeout=TIMEOUT)
        data = ElementTree.fromstring(response.text.encode('utf8'))
        return [MyPlexServer(elem) for elem in data]


class MyPlexDevice(object):
    DEVICES = 'https://my.plexapp.com/devices.xml'

    def __init__(self, data):
        self.name = data.attrib.get('name')
        self.publicAddress = data.attrib.get('publicAddress')
        self.product = data.attrib.get('product')
        self.productVersion = data.attrib.get('productVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.devices = data.attrib.get('device')                    # Whats going on here..
        self.model = data.attrib.get('model')
        self.vendor = data.attrib.get('vendor')
        self.provides = data.attrib.get('provides').split(',')
        self.clientIdentifier = data.attrib.get('clientIdentifier')
        self.version = data.attrib.get('version')
        self.id = cast(int, data.attrib.get('id'))
        self.token = data.attrib.get('token')
        self.createdAt = toDatetime(data.attrib.get('createdAt'))
        self.lastSeenAt = toDatetime(data.attrib.get('lastSeenAt'))
        self.screenResolution = data.attrib.get('screenResolution')
        self.screenDensity = data.attrib.get('screenDensity')
        self.connections = [Connection.from_xml(elem) for elem in data.iterfind('Connection')]
        self.syncList = [elem.attrib.copy() for elem in data.iterfind('SyncList')]
        self._syncItemsUrl = 'https://plex.tv/devices/{0}/sync_items.xml'.format(self.clientIdentifier)

    def syncItems(self):
        headers = plexapi.BASE_HEADERS
        headers['X-Plex-Token'] = self.token
        response = requests.get(self._syncItemsUrl, headers=headers, timeout=TIMEOUT)
        data = ElementTree.fromstring(response.text.encode('utf8'))
        servers = MyPlexServer.fetchServers(self.token)
        return [SyncItem(self, elem, servers) for elem in data.find('SyncItems').iterfind('SyncItem')]

    def __repr__(self):
        return '<{0}:{1}>'.format(self.__class__.__name__, self.name)

    @classmethod
    def fetchDevices(cls, token):
        headers = plexapi.BASE_HEADERS
        headers['X-Plex-Token'] = token
        response = requests.get(MyPlexDevice.DEVICES, headers=headers, timeout=TIMEOUT)
        data = ElementTree.fromstring(response.text.encode('utf8'))
        return [MyPlexDevice(elem) for elem in data]


if __name__ == '__main__':
    import sys
    myplex = MyPlexUser(sys.argv[1], sys.argv[2])
    server = myplex.getServer(sys.argv[3]).connect()
    print server.library.section("Movies").all()
