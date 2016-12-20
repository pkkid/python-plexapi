# -*- coding: utf-8 -*-

"""
PlexServer
"""

from xml.etree import ElementTree

import requests
from requests.status_codes import _codes as codes

from plexapi import BASE_HEADERS, TIMEOUT
from plexapi import log, utils
from plexapi import audio, video, photo, playlist  # noqa; required # why is this needed?
from plexapi.client import PlexClient
from plexapi.compat import quote
from plexapi.exceptions import BadRequest, NotFound
from plexapi.library import Library
from plexapi.playlist import Playlist
from plexapi.playqueue import PlayQueue


class PlexServer(object):
    """Main class to interact with plexapi.

    Examples:
             >>>> plex = PlexServer(token=12345)
             >>>> for client in plex.clients():
             >>>>     print(client.title)

     Note:
         See test/example.py for more examples

    Attributes:
        baseurl (string): Base url for PMS
        friendlyName (string): Pretty name for PMS
        machineIdentifier (string): uuid for PMS
        myPlex (TYPE): Description
        myPlexMappingState (TYPE): Description
        myPlexSigninState (TYPE): Description
        myPlexSubscription (TYPE): Description
        myPlexUsername (string): Description
        platform (string): Description
        platformVersion (string): Description
        session (requests.Session, optinal): Add your own session object for caching
        token (string): X-Plex-Token, using for authenication with PMS
        transcoderActiveVideoSessions (int): How any active video sessions
        updatedAt (int): Last updated at
        version (TYPE): Description

    """

    def __init__(self, baseurl='http://localhost:32400', token=None, session=None):
        """
        Args:
            baseurl (string): Base url for PMS
            token (string): X-Plex-Token, using for authenication with PMS
            session (requests.Session, optional): Use your own session object if you want
                                                  to cache the http responses from PMS
        """
        self.baseurl = baseurl
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
        """Make repr prettier."""
        return '<%s:%s>' % (self.__class__.__name__, self.baseurl)

    def _connect(self):
        """Used for fetching the attributes for __init__."""
        try:
            return self.query('/')
        except Exception as err:
            log.error('%s: %s', self.baseurl, err)
            raise NotFound('No server found at: %s' % self.baseurl)

    @property
    def library(self):
        """Library to browse or search your media."""
        if not self._library:
            self._library = Library(self, self.query('/library/'))
        return self._library

    def account(self):
        data = self.query('/myplex/account')
        return Account(self, data)

    def clients(self):
        """Query PMS for all clients connected to PMS

        Returns:
            list: of Plexclient connnected to PMS

        """
        items = []
        for elem in self.query('/clients'):
            baseurl = 'http://%s:%s' % (elem.attrib['address'],
                                        elem.attrib['port'])
            items.append(PlexClient(baseurl, server=self, data=elem))
        return items

    def client(self, name):
        """Querys PMS for all clients connected to PMS

        Returns:
            Plexclient

        Args:
            name (string): client title, John's Iphone

        Raises:
            NotFound: Unknown client name Betty

        """
        for elem in self.query('/clients'):
            if elem.attrib.get('name').lower() == name.lower():
                baseurl = 'http://%s:%s' % (
                    elem.attrib['address'], elem.attrib['port'])
                return PlexClient(baseurl, server=self, data=elem)
        raise NotFound('Unknown client name: %s' % name)

    def createPlaylist(self, title, items):
        """Create a playlist

           Returns:
                Playlist
        """
        return Playlist.create(self, title, items)

    def createPlayQueue(self, item):
        return PlayQueue.create(self, item)

    def headers(self):
        """Headers given to PMS."""
        headers = BASE_HEADERS
        if self.token:
            headers['X-Plex-Token'] = self.token
        return headers

    def history(self):
        """List watched history.
        """
        return utils.listItems(self, '/status/sessions/history/all')

    def playlists(self):
        # TODO: Add sort and type options?
        # /playlists/all?type=15&sort=titleSort%3Aasc&playlistType=video&smart=0
        return utils.listItems(self, '/playlists')

    def playlist(self, title):  # noqa
        """Returns a playlist with a given name or raise NotFound.

        Args:
            title (string): title of the playlist

        Raises:
            NotFound: Description
        """
        for item in self.playlists():
            if item.title == title:
                return item
        raise NotFound('Invalid playlist title: %s' % title)

    def query(self, path, method=None, headers=None, **kwargs):
        """Main method used to handle http connection to PMS.
           encodes the response to utf-8 and parses the xml returned
           from PMS

        Args:
            path (sting): relative path to PMS, fx /search?query=HELLO
            method (None, optional): requests.method, fx requests.put
            headers (None, optional): Headers that will be passed to PMS
            **kwargs (dict): Used for filter and sorting.

        Raises:
            BadRequest: Description

        Returns:
            xml.etree.ElementTree.Element or None
        """
        url = self.url(path)
        method = method or self.session.get
        log.info('%s %s', method.__name__.upper(), url)
        h = self.headers().copy()
        if headers:
            h.update(headers)
        response = method(url, headers=h, timeout=TIMEOUT, **kwargs)
        if response.status_code not in [200, 201]:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None

    def search(self, query, mediatype=None):
        """Searching within a library section is much more powerful.

        Args:
            query (string): Search string
            mediatype (string, optional): Limit your search to a media type.

        Returns:
            List
        """
        items = utils.listItems(self, '/search?query=%s' % quote(query))
        if mediatype:
            return [item for item in items if item.type == mediatype]
        return items

    def sessions(self):
        """List all active sessions."""
        return utils.listItems(self, '/status/sessions')

    def url(self, path):
        """Build a full for PMS."""
        if self.token:
            delim = '&' if '?' in path else '?'
            return '%s%s%sX-Plex-Token=%s' % (self.baseurl, path, delim, self.token)
        return '%s%s' % (self.baseurl, path)

    def transcodeImage(self, media, height, width, opacity=100, saturation=100):
        """Transcode a image.

           Args:
                height (int): height off image
                width (int): width off image
                opacity (int): Dont seems to be in use anymore # check it
                saturation (int): transparency

            Returns:
                transcoded_image_url or None

        """
        # check for NA incase any tries to pass thumb, or art directly.
        if media:
            transcode_url = '/photo/:/transcode?height=%s&width=%s&opacity=%s&saturation=%s&url=%s' % (
                            height, width, opacity, saturation, media)

            return self.url(transcode_url)




class Account(object):
    """This is the locally cached MyPlex account information. The properties provided don't match
    the myplex.MyPlexAccount object very well. I believe this is here because access to myplex
    is not required to get basic plex information.

    Attributes:
        authToken (sting): X-Plex-Token, using for authenication with PMS
        mappingError (TYPE): Description
        mappingErrorMessage (TYPE): Description
        mappingState (TYPE): Description
        privateAddress (TYPE): Description
        privatePort (TYPE): Description
        publicAddress (TYPE): Description
        publicPort (TYPE): Description
        signInState (TYPE): Description
        subscriptionActive (TYPE): Description
        subscriptionFeatures (TYPE): Description
        subscriptionState (TYPE): Description
        username (TYPE): Description
    """

    def __init__(self, server, data):
        """Args:
                server (Plexclient):
                data (xml.etree.ElementTree.Element): used to set the class attributes.
        """
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
