# -*- coding: utf-8 -*-
import requests
from requests.status_codes import _codes as codes
from plexapi import BASE_HEADERS, CONFIG, TIMEOUT
from plexapi import log, logfilter, utils
from plexapi.alert import AlertListener
from plexapi.base import PlexObject
from plexapi.client import PlexClient
from plexapi.compat import ElementTree, urlencode
from plexapi.exceptions import BadRequest, NotFound
from plexapi.library import Library, Hub
from plexapi.settings import Settings
from plexapi.playlist import Playlist
from plexapi.playqueue import PlayQueue
from plexapi.utils import cast

# Need these imports to populate utils.PLEXOBJECTS
from plexapi import (audio as _audio, video as _video,
    photo as _photo, media as _media, playlist as _playlist)


class PlexServer(PlexObject):
    """ This is the main entry point to interacting with a Plex server. It allows you to
        list connected clients, browse your library sections and perform actions such as
        emptying trash. If you do not know the auth token required to access your Plex
        server, or simply want to access your server with your username and password, you
        can also create an PlexServer instance from :class:`~plexapi.myplex.MyPlexAccount`.

        Parameters:
            baseurl (str): Base url for to access the Plex Media Server (default: 'http://localhost:32400').
            token (str): Required Plex authentication token to access the server.
            session (requests.Session, optional): Use your own session object if you want to
                cache the http responses from PMS

        Attributes:
            allowCameraUpload (bool): True if server allows camera upload.
            allowChannelAccess (bool): True if server allows channel access (iTunes?).
            allowMediaDeletion (bool): True is server allows media to be deleted.
            allowSharing (bool): True is server allows sharing.
            allowSync (bool): True is server allows sync.
            backgroundProcessing (bool): Unknown
            baseurl (str): Base url for the Plex Media Server to access.
            certificate (bool): True if server has an HTTPS certificate.
            companionProxy (bool): Unknown
            diagnostics (bool): Unknown
            eventStream (bool): Unknown
            friendlyName (str): Human friendly name for this server.
            hubSearch (bool): True if `Hub Search <https://www.plex.tv/blog
                /seek-plex-shall-find-leveling-web-app/>`_ is enabled. I believe this
                is enabled for everyone
            machineIdentifier (str): Unique ID for this server (looks like an md5).
            multiuser (bool): True if `multiusers <https://support.plex.tv/hc/en-us/articles
                /200250367-Multi-User-Support>`_ are enabled.
            myPlex (bool): Unknown (True if logged into myPlex?).
            myPlexMappingState (str): Unknown (ex: mapped).
            myPlexSigninState (str): Unknown (ex: ok).
            myPlexSubscription (str): True if you have a myPlex subscription.
            myPlexUsername (str): Email address if signed into myPlex (user@example.com)
            ownerFeatures (bool): List of features allowed by the server owner. This may be based
                on your PlexPass subscription. Features include: camera_upload, cloudsync,
                content_filter, dvr, hardware_transcoding, home, lyrics, music_videos, pass,
                photo_autotags, premium_music_metadata, session_bandwidth_restrictions, sync,
                trailers, webhooks (and maybe more).
            photoAutoTag (bool): True if photo `auto-tagging <https://support.plex.tv/hc/en-us
                /articles/234976627-Auto-Tagging-of-Photos>`_ is enabled.
            platform (str): Platform the server is hosted on (ex: Linux)
            platformVersion (str): Platform version (ex: '6.1 (Build 7601)', '4.4.0-59-generic').
            pluginHost (bool): Unknown
            readOnlyLibraries (bool): Unknown
            requestParametersInCookie (bool): Unknown
            session (Session): Requests session used for object caching.
            streamingBrainVersion (bool): Current `Streaming Brain <https://www.plex.tv/blog
                /mcstreamy-brain-take-world-two-easy-steps/>`_ version.
            sync (bool): True if `syncing to a device <https://support.plex.tv/hc/en-us/articles
                /201053678-Sync-Media-to-a-Device>`_ is enabled.
            token (str): Plex authentication token to access the server.
            transcoderActiveVideoSessions (int): Number of active video transcoding sessions.
            transcoderAudio (bool): True if audio transcoding audio is available.
            transcoderLyrics (bool): True if audio transcoding lyrics is available.
            transcoderPhoto (bool): True if audio transcoding photos is available.
            transcoderSubtitles (bool): True if audio transcoding subtitles is available.
            transcoderVideo (bool): True if audio transcoding video is available.
            transcoderVideoBitrates (bool): List of video bitrates.
            transcoderVideoQualities (bool): List of video qualities.
            transcoderVideoResolutions (bool): List of video resolutions.
            updatedAt (int): Datetime the server was updated.
            updater (bool): Unknown
            version (str): Current Plex version (ex: 1.3.2.3112-1751929)
            voiceSearch (bool): True if voice search is enabled. (is this Google Voice search?)
    """
    key = '/'

    def __init__(self, baseurl=None, token=None, session=None):
        self._baseurl = baseurl or CONFIG.get('auth.server_baseurl', 'http://localhost:32400')
        self._token = logfilter.add_secret(token or CONFIG.get('auth.server_token'))
        self._session = session or requests.Session()
        self._library = None   # cached library
        self._settings = None   # cached settings
        super(PlexServer, self).__init__(self, self.query(self.key), self.key)

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self._data = data
        self.allowCameraUpload = cast(bool, data.attrib.get('allowCameraUpload'))
        self.allowChannelAccess = cast(bool, data.attrib.get('allowChannelAccess'))
        self.allowMediaDeletion = cast(bool, data.attrib.get('allowMediaDeletion'))
        self.allowSharing = cast(bool, data.attrib.get('allowSharing'))
        self.allowSync = cast(bool, data.attrib.get('allowSync'))
        self.backgroundProcessing = cast(bool, data.attrib.get('backgroundProcessing'))
        self.certificate = cast(bool, data.attrib.get('certificate'))
        self.companionProxy = cast(bool, data.attrib.get('companionProxy'))
        self.diagnostics = utils.toList(data.attrib.get('diagnostics'))
        self.eventStream = cast(bool, data.attrib.get('eventStream'))
        self.friendlyName = data.attrib.get('friendlyName')
        self.hubSearch = cast(bool, data.attrib.get('hubSearch'))
        self.machineIdentifier = data.attrib.get('machineIdentifier')
        self.multiuser = cast(bool, data.attrib.get('multiuser'))
        self.myPlex = cast(bool, data.attrib.get('myPlex'))
        self.myPlexMappingState = data.attrib.get('myPlexMappingState')
        self.myPlexSigninState = data.attrib.get('myPlexSigninState')
        self.myPlexSubscription = data.attrib.get('myPlexSubscription')
        self.myPlexUsername = data.attrib.get('myPlexUsername')
        self.ownerFeatures = utils.toList(data.attrib.get('ownerFeatures'))
        self.photoAutoTag = cast(bool, data.attrib.get('photoAutoTag'))
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.pluginHost = cast(bool, data.attrib.get('pluginHost'))
        self.readOnlyLibraries = cast(int, data.attrib.get('readOnlyLibraries'))
        self.requestParametersInCookie = cast(bool, data.attrib.get('requestParametersInCookie'))
        self.streamingBrainVersion = data.attrib.get('streamingBrainVersion')
        self.sync = cast(bool, data.attrib.get('sync'))
        self.transcoderActiveVideoSessions = int(data.attrib.get('transcoderActiveVideoSessions', 0))
        self.transcoderAudio = cast(bool, data.attrib.get('transcoderAudio'))
        self.transcoderLyrics = cast(bool, data.attrib.get('transcoderLyrics'))
        self.transcoderPhoto = cast(bool, data.attrib.get('transcoderPhoto'))
        self.transcoderSubtitles = cast(bool, data.attrib.get('transcoderSubtitles'))
        self.transcoderVideo = cast(bool, data.attrib.get('transcoderVideo'))
        self.transcoderVideoBitrates = utils.toList(data.attrib.get('transcoderVideoBitrates'))
        self.transcoderVideoQualities = utils.toList(data.attrib.get('transcoderVideoQualities'))
        self.transcoderVideoResolutions = utils.toList(data.attrib.get('transcoderVideoResolutions'))
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt'))
        self.updater = cast(bool, data.attrib.get('updater'))
        self.version = data.attrib.get('version')
        self.voiceSearch = cast(bool, data.attrib.get('voiceSearch'))

    def _headers(self, **kwargs):
        """ Returns dict containing base headers for all requests to the server. """
        headers = BASE_HEADERS.copy()
        if self._token:
            headers['X-Plex-Token'] = self._token
        headers.update(kwargs)
        return headers

    @property
    def library(self):
        """ Library to browse or search your media. """
        if not self._library:
            data = self.query(Library.key)
            self._library = Library(self, data)
        return self._library

    @property
    def settings(self):
        """ Returns a list of all server settings. """
        if not self._settings:
            data = self.query(Settings.key)
            self._settings = Settings(self, data)
        return self._settings

    def account(self):
        """ Returns the :class:`~plexapi.server.Account` object this server belongs to. """
        data = self.query(Account.key)
        return Account(self, data)

    def clients(self):
        """ Returns a list of all :class:`~plexapi.client.PlexClient` objects
            connected  to this server.
        """
        items = []
        for elem in self.query('/clients'):
            baseurl = 'http://%s:%s' % (elem.attrib['host'], elem.attrib['port'])
            items.append(PlexClient(baseurl, server=self, data=elem))
        return items

    def client(self, name):
        """ Returns the :class:`~plexapi.client.PlexClient` that matches the specified name.

            Parameters:
                name (str): Name of the client to return.

            Raises:
                :class:`~plexapi.exceptions.NotFound`: Unknown client name
        """
        for elem in self.query('/clients'):
            if elem.attrib.get('name').lower() == name.lower():
                baseurl = 'http://%s:%s' % (elem.attrib['host'], elem.attrib['port'])
                return PlexClient(baseurl, server=self, data=elem)
        raise NotFound('Unknown client name: %s' % name)

    def createPlaylist(self, title, items):
        """ Creates and returns a new :class:`~plexapi.playlist.Playlist`.

            Parameters:
                title (str): Title of the playlist to be created.
                items (list<Media>): List of media items to include in the playlist.
        """
        return Playlist.create(self, title, items)

    def createPlayQueue(self, item, **kwargs):
        """ Creates and returns a new :class:`~plexapi.playqueue.PlayQueue`.

            Parameters:
                item (Media or Playlist): Media or playlist to add to PlayQueue.
                kwargs (dict): See `~plexapi.playerque.PlayQueue.create`.
        """
        return PlayQueue.create(self, item, **kwargs)

    def history(self):
        """ Returns a list of media items from watched history. """
        return self.fetchItems('/status/sessions/history/all')

    def playlists(self):
        """ Returns a list of all :class:`~plexapi.playlist.Playlist` objects saved on the server. """
        # TODO: Add sort and type options?
        # /playlists/all?type=15&sort=titleSort%3Aasc&playlistType=video&smart=0
        return self.fetchItems('/playlists')

    def playlist(self, title):
        """ Returns the :class:`~plexapi.client.Playlist` that matches the specified title.

            Parameters:
                title (str): Title of the playlist to return.

            Raises:
                :class:`~plexapi.exceptions.NotFound`: Invalid playlist title
        """
        return self.fetchItem('/playlists', title=title)

    def query(self, key, method=None, headers=None, **kwargs):
        """ Main method used to handle HTTPS requests to the Plex server. This method helps
            by encoding the response to utf-8 and parsing the returned XML into and
            ElementTree object. Returns None if no data exists in the response.
        """
        url = self.url(key)
        method = method or self._session.get
        log.debug('%s %s', method.__name__.upper(), url)
        headers = self._headers(**headers or {})
        response = method(url, headers=headers, timeout=TIMEOUT, **kwargs)
        if response.status_code not in (200, 201):
            codename = codes.get(response.status_code)[0]
            log.warn('BadRequest (%s) %s %s' % (response.status_code, codename, response.url))
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None

    def search(self, query, mediatype=None, limit=None):
        """ Returns a list of media items or filter categories from the resulting
            `Hub Search <https://www.plex.tv/blog/seek-plex-shall-find-leveling-web-app/>`_
            against all items in your Plex library. This searches genres, actors, directors,
            playlists, as well as all the obvious media titles. It performs spell-checking
            against your search terms (because KUROSAWA is hard to spell). It also provides
            contextual search results. So for example, if you search for 'Pernice', it’ll
            return 'Pernice Brothers' as the artist result, but we’ll also go ahead and
            return your most-listened to albums and tracks from the artist. If you type
            'Arnold' you’ll get a result for the actor, but also the most recently added
            movies he’s in.

            Parameters:
                query (str): Query to use when searching your library.
                mediatype (str): Optionally limit your search to the specified media type.
                limit (int): Optionally limit to the specified number of results per Hub.
        """
        results = []
        params = {'query': query}
        if mediatype:
            params['section'] = utils.SEARCHTYPES[mediatype]
        if limit:
            params['limit'] = limit
        key = '/hubs/search?%s' % urlencode(params)
        for hub in self.fetchItems(key, Hub):
            results += hub.items
        return results

    def sessions(self):
        """ Returns a list of all active session (currently playing) media objects. """
        return self.fetchItems('/status/sessions')

    def startAlertListener(self, callback=None):
        """ Creates a websocket connection to the Plex Server to optionally recieve
            notifications. These often include messages from Plex about media scans
            as well as updates to currently running Transcode Sessions.

            NOTE: You need websocket-client installed in order to use this feature.
            >> pip install websocket-client

            Parameters:
                callback (func): Callback function to call on recieved messages.

            raises:
                :class:`~plexapi.exception.Unsupported`: Websocket-client not installed.
        """
        notifier = AlertListener(self, callback)
        notifier.start()
        return notifier

    def transcodeImage(self, media, height, width, opacity=100, saturation=100):
        """ Returns the URL for a transcoded image from the specified media object.
            Returns None if no media specified (needed if user tries to pass thumb
            or art directly).

            Parameters:
                height (int): Height to transcode the image to.
                width (int): Width to transcode the image to.
                opacity (int): Opacity of the resulting image (possibly deprecated).
                saturation (int): Saturating of the resulting image.
        """
        if media:
            transcode_url = '/photo/:/transcode?height=%s&width=%s&opacity=%s&saturation=%s&url=%s' % (
                height, width, opacity, saturation, media)
            return self.url(transcode_url)

    def url(self, key):
        """ Build a URL string with proper token argument. """
        if self._token:
            delim = '&' if '?' in key else '?'
            return '%s%s%sX-Plex-Token=%s' % (self._baseurl, key, delim, self._token)
        return '%s%s' % (self._baseurl, key)


class Account(PlexObject):
    """ Contains the locally cached MyPlex account information. The properties provided don't
        match the :class:`~plexapi.myplex.MyPlexAccount` object very well. I believe this exists
        because access to myplex is not required to get basic plex information. I can't imagine
        object is terribly useful except unless you were needed this information while offline.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this account is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).

        Attributes:
            authToken (str): Plex authentication token to access the server.
            mappingError (str): Unknown
            mappingErrorMessage (str): Unknown
            mappingState (str): Unknown
            privateAddress (str): Local IP address of the Plex server.
            privatePort (str): Local port of the Plex server.
            publicAddress (str): Public IP address of the Plex server.
            publicPort (str): Public port of the Plex server.
            signInState (str): Signin state for this account (ex: ok).
            subscriptionActive (str): True if the account subscription is active.
            subscriptionFeatures (str): List of features allowed by the server for this account.
                This may be based on your PlexPass subscription. Features include: camera_upload,
                cloudsync, content_filter, dvr, hardware_transcoding, home, lyrics, music_videos,
                pass, photo_autotags, premium_music_metadata, session_bandwidth_restrictions,
                sync, trailers, webhooks' (and maybe more).
            subscriptionState (str): 'Active' if this subscription is active.
            username (str): Plex account username (user@example.com).
    """
    key = '/myplex/account'

    def _loadData(self, data):
        self._data = data
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
        self.subscriptionFeatures = utils.toList(data.attrib.get('subscriptionFeatures'))
        self.subscriptionActive = cast(bool, data.attrib.get('subscriptionActive'))
        self.subscriptionState = data.attrib.get('subscriptionState')
