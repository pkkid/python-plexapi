"""
PlexAPI MyPlex
"""
import plexapi, requests
from plexapi import TIMEOUT, log
from plexapi.exceptions import BadRequest, NotFound
from plexapi.utils import addrToIP, cast, toDatetime
from requests.status_codes import _codes as codes
from threading import Thread
from xml.etree import ElementTree


class MyPlexUser:
    """ Logs into my.plexapp.com to fetch account and token information. This
        useful to get a token if not on the local network.
    """
    SIGNIN = 'https://my.plexapp.com/users/sign_in.xml'

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

    def servers(self):
        return MyPlexServer.fetch_servers(self.authenticationToken)

    def getServer(self, search, port=32400):
        """ Searches server.name, server.sourceTitle and server.host:server.port
            from the list of available for this PlexUser.
        """
        return _findServer(self.servers(), search, port)

    @classmethod
    def signin(cls, username, password):
        auth = (username, password)
        log.info('POST %s', cls.SIGNIN)
        response = requests.post(cls.SIGNIN, headers=plexapi.BASE_HEADERS, auth=auth, timeout=TIMEOUT)
        if response.status_code != requests.codes.created:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = ElementTree.fromstring(response.text.encode('utf8'))
        return cls(data)


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
        return MyPlexServer.fetch_servers(self.authToken)

    def getServer(self, search, port=32400):
        """ Searches server.name, server.sourceTitle and server.host:server.port
            from the list of available for this PlexAccount.
        """
        return _findServer(self.servers(), search, port)


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
        # Try connecting to all known addresses in parellel to save time, but
        # only return the first server (in order) that provides a response.
        addresses = [self.address]
        if self.owned:
            addresses = self.localAddresses + [self.address]
        threads = [None] * len(addresses)
        results = [None] * len(addresses)
        for i in range(len(addresses)):
            args = (addresses[i], results, i)
            threads[i] = Thread(target=self._connect, args=args)
            threads[i].start()
        for thread in threads:
            thread.join()
        results = list(filter(None, results))
        if results:
            log.info('Connecting to server: %s', results[0])
            return results[0]
        raise NotFound('Unable to connect to server: %s' % self.name)

    def _connect(self, address, results, i):
        from plexapi.server import PlexServer
        try:
            results[i] = PlexServer(address, self.port, self.accessToken)
        except NotFound:
            results[i] = None

    @classmethod
    def fetch_servers(cls, token):
        headers = plexapi.BASE_HEADERS
        headers['X-Plex-Token'] = token
        log.info('GET %s?X-Plex-Token=%s', cls.SERVERS, token)
        response = requests.get(cls.SERVERS, headers=headers, timeout=TIMEOUT)
        data = ElementTree.fromstring(response.text.encode('utf8'))
        return [MyPlexServer(elem) for elem in data]


def _findServer(servers, search, port=32400):
    """ Searches server.name, server.sourceTitle and server.host:server.port """
    search = search.lower()
    ipaddr = addrToIP(search)
    log.info('Looking for server: %s (host: %s:%s)', search, ipaddr, port)
    for server in servers:
        serverName = server.name.lower() if server.name else 'NA'
        sourceTitle = server.sourceTitle.lower() if server.sourceTitle else 'NA'
        if (search in [serverName, sourceTitle]) or (server.host == ipaddr and server.port == port):
            log.info('Server found: %s', server)
            return server
    log.info('Unable to find server: %s (host: %s:%s)', search, ipaddr, port)
    raise NotFound('Unable to find server: %s (host: %s:%s)' % (search, ipaddr, port))
