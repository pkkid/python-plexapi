# -*- coding: utf-8 -*-
import requests
from requests.status_codes import _codes as codes
from plexapi import BASE_HEADERS, TIMEOUT, log, utils
from plexapi.exceptions import BadRequest, NotFound, Unsupported
from xml.etree import ElementTree


class PlexClient(object):
    """ Main class for interacting with a Plex client. This class can connect
        directly to the client and control it or proxy commands through your
        Plex Server. To better understand the Plex client API's read this page:
        https://github.com/plexinc/plex-media-player/wiki/Remote-control-API

        Parameters:
            baseurl (str): HTTP URL to connect dirrectly to this client.
            token (str): X-Plex-Token used for authenication (optional).
            session (:class:`~requests.Session`): requests.Session object if you want more control (optional).
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).

        Attributes:
            baseurl (str): HTTP address of the client
            device (str): Best guess on the type of device this is (PS, iPhone, Linux, etc).
            deviceClass (str): Device class (pc, phone, etc).
            machineIdentifier (str): Unique ID for this device.
            model (str): Unknown
            platform (str): Unknown
            platformVersion (str): Description
            product (str): Client Product (Plex for iOS, etc).
            protocol (str): Always seems ot be 'plex'.
            protocolCapabilities (list<str>): List of client capabilities (navigation, playback,
                timeline, mirror, playqueues).
            protocolVersion (str): Protocol version (1, future proofing?)
            server (:class:`~plexapi.server.PlexServer`): Server this client is connected to.
            session (:class:`~requests.Session`): Session object used for connection.
            state (str): Unknown
            title (str): Name of this client (Johns iPhone, etc).
            token (str): X-Plex-Token used for authenication
            vendor (str): Unknown
            version (str): Device version (4.6.1, etc).
            _proxyThroughServer (bool): Set to True after calling
                :func:`~plexapi.client.PlexClient.proxyThroughServer()` (default False).
    """
    def __init__(self, baseurl, token=None, session=None, server=None, data=None):
        self.baseurl = baseurl.strip('/')
        self.token = token
        self.server = server
        # session > server.session > requests.Session
        _server_session = server.session if server else None
        self.session = session or _server_session or requests.Session()
        self._loadData(data) if data is not None else self.connect()
        self._proxyThroughServer = False
        self._commandId = 0

    def _loadData(self, data):
        """ Load attribute values from Plex XML response. """
        self._data = data
        self.deviceClass = data.attrib.get('deviceClass')
        self.machineIdentifier = data.attrib.get('machineIdentifier')
        self.product = data.attrib.get('product')
        self.protocol = data.attrib.get('protocol')
        self.protocolCapabilities = data.attrib.get('protocolCapabilities', '').split(',')
        self.protocolVersion = data.attrib.get('protocolVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.title = data.attrib.get('title') or data.attrib.get('name')
        # Active session details
        self.device = data.attrib.get('device')
        self.model = data.attrib.get('model')
        self.state = data.attrib.get('state')
        self.vendor = data.attrib.get('vendor')
        self.version = data.attrib.get('version')

    def connect(self):
        """ Connects to the client and reloads all class attributes.
            
            Raises:
                :class:`~plexapi.exceptions.NotFound`: No client found at the specified url.
        """
        try:
            data = self.query('/resources')[0]
            self._loadData(data)
        except Exception as err:
            log.error('%s: %s', self.baseurl, err)
            raise NotFound('No client found at: %s' % self.baseurl)

    def headers(self):
        """ Returns a dict of all default headers for Client requests. """
        headers = BASE_HEADERS
        if self.token:
            headers['X-Plex-Token'] = self.token
        return headers

    def proxyThroughServer(self, value=True):
        """ Tells this PlexClient instance to proxy all future commands through the PlexServer.
            Useful if you do not wish to connect directly to the Client device itself. 

            Parameters:
                value (bool): Enable or disable proxying (optional, default True).

            Raises:
                :class:`~plexapi.exceptions.Unsupported`: Cannot use client proxy with unknown server.
        """
        if value is True and not self.server:
            raise Unsupported('Cannot use client proxy with unknown server.')
        self._proxyThroughServer = value

    def query(self, path, method=None, headers=None, **kwargs):
        """ Returns an ElementTree object containing the response
            from the specified request path.

            Parameters:
                path (str): Relative path to query.
                method (func): `self.session.get` or `self.session.post`
                headers (dict): Additional headers to include or override in the request.
                **kwargs (TYPE): Additional arguments to inclde in the request.<method> call.

            Raises:
                :class:`~plexapi.exceptions.BadRequest`: When the response is not in [200, 201]
        """
        url = self.url(path)
        method = method or self.session.get
        log.info('%s %s', method.__name__.upper(), url)
        headers = dict(self.headers(), **(headers or {})) # remove hack
        response = method(url, headers=headers, timeout=TIMEOUT, **kwargs)
        if response.status_code not in [200, 201]:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None

    def sendCommand(self, command, proxy=None, **params):
        """ Convenience wrapper around :func:`~plexapi.client.PlexClient.query()` to more easily
            send simple commands to the client. Returns an ElementTree object containing
            the response.

            Parameters:
                command (str): Command to be sent in for format '<controller>/<command>'.
                proxy (bool): Set True to proxy this command through the PlexServer.
                **params (dict): Additional GET parameters to include with the command.

            Raises:
                :class:`~plexapi.exceptions.Unsupported`: When we detect the client doesn't support this capability.
        """
        command = command.strip('/')
        controller = command.split('/')[0]
        if controller not in self.protocolCapabilities:
            raise Unsupported('Client %s does not support the %s controller.' %
                (self.title, controller))
        path = '/player/%s%s' % (command, utils.joinArgs(params))
        headers = {'X-Plex-Target-Client-Identifier': self.machineIdentifier}
        self._commandId += 1
        params['commandID'] = self._commandId
        proxy = self._proxyThroughServer if proxy is None else proxy
        if proxy:
            return self.server.query(path, headers=headers)
        path = '/player/%s%s' % (command, utils.joinArgs(params))
        return self.query(path, headers=headers)

    def url(self, path):
        """ Given a path, this retuns the full PlexClient the PlexServer URL to request.

            Parameters:
                path (str): Relative path to be converted.
        """
        if self.token:
            delim = '&' if '?' in path else '?'
            return '%s%s%sX-Plex-Token=%s' % (self.baseurl, path, delim, self.token)
        return '%s%s' % (self.baseurl, path)

    #---------------------
    # Navigation Commands
    # These commands navigate around the user-interface.
    def contextMenu(self):
        """ Open the context menu on the client. """
        self.sendCommand('navigation/contextMenu')

    def goBack(self):
        """ Navigate back one position. """
        self.sendCommand('navigation/back')

    def goToHome(self):
        """ Go directly to the home screen. """
        self.sendCommand('navigation/home')

    def goToMusic(self):
        """ Go directly to the playing music panel. """
        self.sendCommand('navigation/music')

    def moveDown(self):
        """ Move selection down a position. """
        self.sendCommand('navigation/moveDown')

    def moveLeft(self):
        """ Move selection left a position. """
        self.sendCommand('navigation/moveLeft')

    def moveRight(self):
        """ Move selection right a position. """
        self.sendCommand('navigation/moveRight')

    def moveUp(self):
        """ Move selection up a position. """
        self.sendCommand('navigation/moveUp')

    def nextLetter(self):
        """ Jump to next letter in the alphabet. """
        self.sendCommand('navigation/nextLetter')

    def pageDown(self):
        """ Move selection down a full page. """
        self.sendCommand('navigation/pageDown')

    def pageUp(self):
        """ Move selection up a full page. """
        self.sendCommand('navigation/pageUp')

    def previousLetter(self):
        """ Jump to previous letter in the alphabet. """
        self.sendCommand('navigation/previousLetter')

    def select(self):
        """ Select element at the current position. """
        self.sendCommand('navigation/select')

    def toggleOSD(self):
        """ Toggle the on screen display during playback. """
        self.sendCommand('navigation/toggleOSD')

    def goToMedia(self, media, **params):
        """ Navigate directly to the specified media page.

            Parameters:
                media (:class:`~plexapi.media.Media`): Media object to navigate to.
                **params (dict): Additional GET parameters to include with the command.

            Raises:
                :class:`~plexapi.exceptions.Unsupported`: When no PlexServer specified in this object.
        """
        if not self.server:
            raise Unsupported('A server must be specified before using this command.')
        server_url = media.server.baseurl.split(':')
        self.sendCommand('mirror/details', **dict({
            'machineIdentifier': self.server.machineIdentifier,
            'address': server_url[1].strip('/'),
            'port': server_url[-1],
            'key': media.key,
        }, **params))

    #-------------------
    # Playback Commands
    # Most of the playback commands take a mandatory mtype {'music','photo','video'} argument,
    # to specify which media type to apply the command to, (except for playMedia). This
    # is in case there are multiple things happening (e.g. music in the background, photo
    # slideshow in the foreground).
    def pause(self, mtype):
        """ Pause the currently playing media type.

            Parameters:
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/pause', type=mtype)

    def play(self, mtype):
        """ Start playback for the specified media type.

            Parameters:
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/play', type=mtype)

    def refreshPlayQueue(self, playQueueID, mtype=None):
        """ Refresh the specified Playqueue.

            Parameters:
                playQueueID (str): Playqueue ID.
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand(
            'playback/refreshPlayQueue', playQueueID=playQueueID, type=mtype)

    def seekTo(self, offset, mtype=None):
        """ Seek to the specified offset (ms) during playback.

            Parameters:
                offset (int): Position to seek to (milliseconds).
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/seekTo', offset=offset, type=mtype)

    def skipNext(self, mtype=None):
        """ Skip to the next playback item.

            Parameters:
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/skipNext', type=mtype)

    def skipPrevious(self, mtype=None):
        """ Skip to previous playback item.

            Parameters:
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/skipPrevious', type=mtype)

    def skipTo(self, key, mtype=None):
        """ Skip to the playback item with the specified key.

            Parameters:
                key (str): Key of the media item to skip to.
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/skipTo', key=key, type=mtype)

    def stepBack(self, mtype=None):
        """ Step backward a chunk of time in the current playback item.

            Parameters:
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/stepBack', type=mtype)

    def stepForward(self, mtype):
        """ Step forward a chunk of time in the current playback item.

            Parameters:
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/stepForward', type=mtype)

    def stop(self, mtype):
        """ Stop the currently playing item.

            Parameters:
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.sendCommand('playback/stop', type=mtype)

    def setRepeat(self, repeat, mtype):
        """ Enable repeat for the specified playback items.

            Parameters:
                repeat (int): Repeat mode (0=off, 1=repeatone, 2=repeatall).
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.setParameters(repeat=repeat, mtype=mtype)

    def setShuffle(self, shuffle, mtype):
        """ Enable shuffle for the specified playback items.

            Parameters:
                shuffle (int): Shuffle mode (0=off, 1=on)
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.setParameters(shuffle=shuffle, mtype=mtype)

    def setVolume(self, volume, mtype):
        """ Enable volume for the current playback item.

            Parameters:
                volume (int): Volume level (0-100).
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.setParameters(volume=volume, mtype=mtype)

    def setAudioStream(self, audioStreamID, mtype):
        """ Select the audio stream for the current playback item (only video).

            Parameters:
                audioStreamID (str): ID of the audio stream from the media object.
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.setStreams(audioStreamID=audioStreamID, mtype=mtype)

    def setSubtitleStream(self, subtitleStreamID, mtype):
        """ Select the subtitle stream for the current playback item (only video).

            Parameters:
                subtitleStreamID (str): ID of the subtitle stream from the media object.
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.setStreams(subtitleStreamID=subtitleStreamID, mtype=mtype)

    def setVideoStream(self, videoStreamID, mtype):
        """ Select the video stream for the current playback item (only video).

            Parameters:
                videoStreamID (str): ID of the video stream from the media object.
                mtype (str): Media type to take action against (music, photo, video).
        """
        self.setStreams(videoStreamID=videoStreamID, mtype=mtype)

    def playMedia(self, media, offset=0, **params):
        """ Start playback of the specified media item. See also:
            
            Parameters:
                media (:class:`~plexapi.media.Media`): Media item to be played back (movie, music, photo).
                offset (int): Number of milliseconds at which to start playing with zero representing
                    the beginning (default 0).
                **params (dict): Optional additional parameters to include in the playback request. See
                    also: https://github.com/plexinc/plex-media-player/wiki/Remote-control-API#modified-commands

            Raises:
                :class:`~plexapi.exceptions.Unsupported`: When no PlexServer specified in this object.
        """
        if not self.server:
            raise Unsupported('A server must be specified before using this command.')
        server_url = media.server.baseurl.split(':')
        playqueue = self.server.createPlayQueue(media)
        self.sendCommand('playback/playMedia', **dict({
            'machineIdentifier': self.server.machineIdentifier,
            'address': server_url[1].strip('/'),
            'port': server_url[-1],
            'offset': offset,
            'key': media.key,
            'containerKey': '/playQueues/%s?window=100&own=1' % playqueue.playQueueID,
        }, **params))

    def setParameters(self, volume=None, shuffle=None, repeat=None, mtype=None):
        """ Set multiple playback parameters at once.

            Parameters:
                volume (int): Volume level (0-100; optional).
                shuffle (int): Shuffle mode (0=off, 1=on; optional).
                repeat (int): Repeat mode (0=off, 1=repeatone, 2=repeatall; optional).
                mtype (str): Media type to take action against (optional music, photo, video).
        """
        params = {}
        if repeat is not None:
            params['repeat'] = repeat
        if shuffle is not None:
            params['shuffle'] = shuffle
        if volume is not None:
            params['volume'] = volume
        if mtype is not None:
            params['type'] = mtype
        self.sendCommand('playback/setParameters', **params)

    def setStreams(self, audioStreamID=None, subtitleStreamID=None, videoStreamID=None, mtype=None):
        """ Select multiple playback streams at once.

            Parameters:
                audioStreamID (str): ID of the audio stream from the media object.
                subtitleStreamID (str): ID of the subtitle stream from the media object.
                videoStreamID (str): ID of the video stream from the media object.
                mtype (str): Media type to take action against (optional music, photo, video).
        """
        params = {}
        if audioStreamID is not None:
            params['audioStreamID'] = audioStreamID
        if subtitleStreamID is not None:
            params['subtitleStreamID'] = subtitleStreamID
        if videoStreamID is not None:
            params['videoStreamID'] = videoStreamID
        if mtype is not None:
            params['type'] = mtype
        self.sendCommand('playback/setStreams', **params)

    #-------------------
    # Timeline Commands
    def timeline(self):
        """ Poll the current timeline and return the XML response. """
        return self.sendCommand('timeline/poll', **{'wait': 1, 'commandID': 4})

    def isPlayingMedia(self, includePaused=False):
        """ Returns True if any media is currently playing.

            Parameters:
                includePaused (bool): Set True to treat currently paused items
                    as playing (optional; default True).
        """
        for mediatype in self.timeline():
            if mediatype.get('state') == 'playing':
                return True
            if includePaused and mediatype.get('state') == 'paused':
                return True
        return False
