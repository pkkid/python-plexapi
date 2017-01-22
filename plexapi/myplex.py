# -*- coding: utf-8 -*-
import plexapi, requests
from plexapi import TIMEOUT, log, utils
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.client import PlexClient
from plexapi.compat import ElementTree
from plexapi.server import PlexServer
from requests.status_codes import _codes as codes


class MyPlexAccount(object):
    """ MyPlex account and profile information. The easiest way to build
        this object is by calling the staticmethod :func:`~myplex.MyPlexAccount.signin`
        with your username and password. This object represents the data found Account on
        the myplex.tv servers at the url https://plex.tv/users/account.

        Attributes:
            authenticationToken (str): <Unknown>
            certificateVersion (str): <Unknown>
            cloudSyncDevice (str): 
            email (str): Your current Plex email address.
            entitlements (List<str>): List of devices your allowed to use with this account.
            guest (bool): <Unknown>
            home (bool): <Unknown>
            homeSize (int): <Unknown>
            id (str): Your Plex account ID.
            locale (str): Your Plex locale
            mailing_list_status (str): Your current mailing list status.
            maxHomeSize (int): <Unknown>
            queueEmail (str): Email address to add items to your `Watch Later` queue.
            queueUid (str): <Unknown>
            restricted (bool): <Unknown>
            roles: (List<str>) Lit of account roles. Plexpass membership listed here.
            scrobbleTypes (str): Description
            secure (bool): Description
            subscriptionActive (bool): True if your subsctiption is active.
            subscriptionFeatures: (List<str>) List of features allowed on your subscription.
            subscriptionPlan (str): Name of subscription plan.
            subscriptionStatus (str): String representation of `subscriptionActive`.
            thumb (str): URL of your account thumbnail.
            title (str): <Unknown> - Looks like an alias for `username`.
            username (str): Your account username.
            uuid (str): <Unknown>
    """
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

    def device(self, name):
        """ Returns the :class:`~myplex.MyPlexDevice` that matched the name specified.
            
            Attributes:
                name (str): Name to match against.
        """
        return _findItem(self.devices(), name)

    def devices(self):
        """ Returns a list of all :class:`~myplex.MyPlexDevice` objects connected to the server. """
        return _listItems(MyPlexDevice.BASEURL, self.authenticationToken, MyPlexDevice)

    def resources(self):
        """Resources.

        Returns:
            List: of MyPlexResource
        """
        return _listItems(MyPlexResource.BASEURL, self.authenticationToken, MyPlexResource)

    def resource(self, name):
        """Find resource ny name.

        Args:
            name (str): to find

        Returns:
            class: MyPlexResource
        """
        return _findItem(self.resources(), name)

    def users(self):
        """List of users.

        Returns:
            List: of MyPlexuser
        """
        return _listItems(MyPlexUser.BASEURL, self.authenticationToken, MyPlexUser)

    def user(self, email):
        """Find a user by email.

        Args:
            email (str): Username to match against.

        Returns:
            class: User
        """
        return _findItem(self.users(), email, ['username', 'email'])

    @classmethod
    def signin(cls, username, password):
        """Summary

        Args:
            username (str): username
            password (str): password

        Returns:
            class: MyPlexAccount

        Raises:
            BadRequest: (HTTPCODE) http codename
            Unauthorized: (HTTPCODE) http codename
        """
        if 'X-Plex-Token' in plexapi.BASE_HEADERS:
            del plexapi.BASE_HEADERS['X-Plex-Token']
        auth = (username, password)
        log.info('POST %s', cls.SIGNIN)
        response = requests.post(
            cls.SIGNIN, headers=plexapi.BASE_HEADERS, auth=auth, timeout=TIMEOUT)
        if response.status_code != requests.codes.created:
            codename = codes.get(response.status_code)[0]
            if response.status_code == 401:
                raise Unauthorized('(%s) %s' %
                                   (response.status_code, codename))
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = ElementTree.fromstring(response.text.encode('utf8'))
        return cls(data, cls.SIGNIN)


# Not to be confused with the MyPlexAccount, this represents
# non-signed in users such as friends and linked accounts.
class MyPlexUser(object):
    """Class to other users.

    Attributes:
        allowCameraUpload (bool): True if this user can upload images
        allowChannels (bool): True if this user has access to channels
        allowSync (bool): True if this user can sync
        BASEURL (str): Description
        email (str): user@gmail.com
        filterAll (str): Description
        filterMovies (str): Description
        filterMusic (str): Description
        filterPhotos (str): Description
        filterTelevision (str): Description
        home (bool):
        id (int): 1337
        protected (False): Is this if ssl? check it
        recommendationsPlaylistId (str): Description
        restricted (str): fx 0
        thumb (str): Link to the users avatar
        title (str): Hellowlol
        username (str): Hellowlol
    """
    BASEURL = 'https://plex.tv/api/users/'

    def __init__(self, data, initpath=None):
        """Summary

        Args:
            data (Element): XML repsonse as Element
            initpath (None, optional): Relative url str
        """
        self.allowCameraUpload = utils.cast(
            bool, data.attrib.get('allowCameraUpload'))
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
        self.recommendationsPlaylistId = data.attrib.get(
            'recommendationsPlaylistId')
        self.restricted = data.attrib.get('restricted')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.username = data.attrib.get('username')

    def __repr__(self):
        """Pretty repr."""
        return '<%s:%s:%s>' % (self.__class__.__name__, self.id, self.username)


class MyPlexResource(object):
    """Summary

    Attributes:
        accessToken (str): This resource accesstoken.
        BASEURL (TYPE): Description
        clientIdentifier (str): 1f2fe128794fd...
        connections (list): of ResourceConnection
        createdAt (datetime): Description
        device (str): pc
        home (None): Dunno wtf this can me
        lastSeenAt (datetime): Description
        name (str): Pretty name fx S-PC
        owned (bool): True if this is your own.
        platform (str): Windows
        platformVersion (str): fx. 6.1 (Build 7601)
        presence (bool): True if online
        product (str): Plex Media Server
        productVersion (str): 1.3.3.3148-b38628e
        provides (str): fx server
        synced (bool): Description
    """
    BASEURL = 'https://plex.tv/api/resources?includeHttps=1'

    def __init__(self, data):
        """Summary

        Args:
            data (Element): XML response as Element
        """
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
        self.connections = [ResourceConnection(
            elem) for elem in data if elem.tag == 'Connection']

    def __repr__(self):
        """Pretty repr."""
        return '<%s:%s>' % (self.__class__.__name__, self.name.encode('utf8'))

    def connect(self, ssl=None):
        """Connect.

        Args:
            ssl (None, optional): Use ssl.

        Returns:
            class: Plexserver

        Raises:
            NotFound: Unable to connect to resource: name
        """

        # Sort connections from (https, local) to (http, remote)
        # Only check non-local connections unless we own the resource
        forcelocal = lambda c: self.owned or c.local
        connections = sorted(
            self.connections, key=lambda c: c.local, reverse=True)
        https = [c.uri for c in self.connections if forcelocal(c)]
        http = [c.httpuri for c in self.connections if forcelocal(c)]
        connections = https + http
        # Try connecting to all known resource connections in parellel, but
        # only return the first server (in order) that provides a response.
        listargs = [[c] for c in connections]
        results = utils.threaded(self._connect, listargs)
        # At this point we have a list of result tuples containing (url, token, PlexServer)
        # or (url, token, None) in the case a connection could not be
        # established.
        for url, token, result in results:
            okerr = 'OK' if result else 'ERR'
            log.info(
                'Testing resource connection: %s?X-Plex-Token=%s %s', url, token, okerr)

        results = [r[2] for r in results if r and r is not None]
        if not results:
            raise NotFound('Unable to connect to resource: %s' % self.name)
        log.info('Connecting to server: %s?X-Plex-Token=%s',
                 results[0].baseurl, results[0].token)

        return results[0]

    def _connect(self, url, results, i):
        """Connect.

        Args:
            url (str): url to the resource
            results (TYPE): Description
            i (TYPE): Description

        Returns:
            TYPE: Description
        """
        try:
            results[i] = (url, self.accessToken,
                          PlexServer(url, self.accessToken))
        except NotFound:
            results[i] = (url, self.accessToken, None)


class ResourceConnection(object):
    """ResourceConnection.

    Attributes:
        address (str): Local ip adress
        httpuri (str): Full local address
        local (bool): True if local
        port (int): 32400
        protocol (str): http or https
        uri (str): External adress
    """
    def __init__(self, data):
        """Set attrs.

        Args:
            data (Element): XML response as Element from PMS.
        """
        self.protocol = data.attrib.get('protocol')
        self.address = data.attrib.get('address')
        self.port = utils.cast(int, data.attrib.get('port'))
        self.uri = data.attrib.get('uri')
        self.local = utils.cast(bool, data.attrib.get('local'))
        self.httpuri = 'http://%s:%s' % (self.address, self.port)

    def __repr__(self):
        """Pretty repr."""
        return '<%s:%s>' % (self.__class__.__name__, self.uri.encode('utf8'))


class MyPlexDevice(object):
    """Device connected.

    Attributes:
        BASEURL (str): Plex.tv XML device url
        clientIdentifier (str): 0x685d43d...
        connections (list):
        device (str): fx Windows
        id (str): 123
        model (str):
        name (str): fx Computername
        platform (str): Windows
        platformVersion (str): Fx 8
        product (str): Fx PlexAPI
        productVersion (string): 2.0.2
        provides (str): fx controller
        publicAddress (str): Public ip address
        screenDensity (str): Description
        screenResolution (str): Description
        token (str): Auth token
        vendor (str): Description
        version (str): fx 2.0.2
    """

    BASEURL = 'https://plex.tv/devices.xml'

    def __init__(self, data):
        """Set attrs

        Args:
            data (Element): XML response as Element from PMS
        """
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
        self.connections = [connection.attrib.get(
            'uri') for connection in data.iter('Connection')]

    def __repr__(self):
        """Pretty repr."""
        return '<%s:%s:%s>' % (self.__class__.__name__, self.name.encode('utf8'), self.product.encode('utf8'))

    def connect(self, ssl=None):
        """Connect to the first server.

        Args:
            ssl (None, optional): Use SSL?

        Returns:
            TYPE: Plexserver

        Raises:
            NotFound: Unable to connect to resource: name
        """
        # Try connecting to all known resource connections in parellel, but
        # only return the first server (in order) that provides a response.
        listargs = [[c] for c in self.connections]
        results = utils.threaded(self._connect, listargs)
        # At this point we have a list of result tuples containing (url, token, PlexServer)
        # or (url, token, None) in the case a connection could not be
        # established.
        for url, token, result in results:
            okerr = 'OK' if result else 'ERR'
            log.info('Testing device connection: %s?X-Plex-Token=%s %s',
                     url, token, okerr)
        results = [r[2] for r in results if r and r[2] is not None]
        if not results:
            raise NotFound('Unable to connect to resource: %s' % self.name)
        log.info('Connecting to server: %s?X-Plex-Token=%s',
                 results[0].baseurl, results[0].token)

        return results[0]

    def _connect(self, url, results, i):
        """Summary

        Args:
            url (TYPE): Description
            results (TYPE): Description
            i (TYPE): Description

        Returns:
            TYPE: Description
        """
        try:
            results[i] = (url, self.token, PlexClient(url, self.token))
        except NotFound as err:
            results[i] = (url, self.token, None)


def _findItem(items, value, attrs=None):
    """Simple helper to find something using attrs

    Args:
        items (cls): list of Object to get the attrs from
        value (str): value to match against
        attrs (None, optional): attr to match against value.

    Returns:
        TYPE: Description

    Raises:
        NotFound: Description
    """
    attrs = attrs or ['name']
    for item in items:
        for attr in attrs:
            if value.lower() == getattr(item, attr).lower():
                return item
    raise NotFound('Unable to find item %s' % value)


def _listItems(url, token, cls):
    """Helper that builds list of classes from a XML response.

    Args:
        url (str): Description
        token (str): Description
        cls (class): Class to initate

    Returns:
        List: of classes
    """
    headers = plexapi.BASE_HEADERS
    headers['X-Plex-Token'] = token
    log.info('GET %s?X-Plex-Token=%s', url, token)
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    data = ElementTree.fromstring(response.text.encode('utf8'))
    return [cls(elem) for elem in data]
