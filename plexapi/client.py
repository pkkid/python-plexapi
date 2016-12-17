# -*- coding: utf-8 -*-
"""
PlexAPI Client
To understand how this works, read this page:
https://github.com/plexinc/plex-media-player/wiki/Remote-control-API
"""

import requests
from requests.status_codes import _codes as codes
from plexapi import BASE_HEADERS, TIMEOUT, log, utils
from plexapi.exceptions import BadRequest, NotFound, Unsupported
from xml.etree import ElementTree


class PlexClient(object):
    """Main class for interacting with a client.

    Attributes:
        baseurl (str): http adress for the client
        device (None): Description
        deviceClass (sting): pc, phone
        machineIdentifier (str): uuid fx 5471D9EA-1467-4051-9BE7-FCBDF490ACE3
        model (TYPE): Description
        platform (TYPE): Description
        platformVersion (TYPE): Description
        product (str): plex for ios
        protocol (str): plex
        protocolCapabilities (list): List of what client can do
        protocolVersion (str): 1
        server (plexapi.server.Plexserver): PMS your connected to
        session (None or requests.Session): Add your own session object to cache stuff
        state (None): Description
        title (str): fx Johns Iphone
        token (str): X-Plex-Token, using for authenication with PMS
        vendor (str): Description
        version (str): fx. 4.6
    """

    def __init__(self, baseurl, token=None, session=None, server=None, data=None):
        """Kick shit off.

        Args:
            baseurl (sting): fx http://10.0.0.99:1111222
            token (None, optional): X-Plex-Token, using for authenication with PMS
            session (None, optional): requests.Session() or your own session
            server (None, optional): PlexServer
            data (None, optional): XML response from PMS as Element
                                   or uses connect to get it
        """
        self.baseurl = baseurl.strip('/')
        self.token = token
        self.session = session or requests.Session()
        self.server = server
        self._loadData(data) if data is not None else self.connect()
        self._proxyThroughServer = False
        self._commandId = 0

    def _loadData(self, data):
        """Sets attrs to the class.

        Args:
            data (Element): XML response from PMS as a Element
        """
        self.deviceClass = data.attrib.get('deviceClass')
        self.machineIdentifier = data.attrib.get('machineIdentifier')
        self.product = data.attrib.get('product')
        self.protocol = data.attrib.get('protocol')
        self.protocolCapabilities = data.attrib.get(
            'protocolCapabilities', '').split(',')
        self.protocolVersion = data.attrib.get('protocolVersion')
        self.platform = data.attrib.get('platform')
        self.platformVersion = data.attrib.get('platformVersion')
        self.title = data.attrib.get('title') or data.attrib.get('name')
        # active session details
        self.device = data.attrib.get('device')
        self.model = data.attrib.get('model')
        self.state = data.attrib.get('state')
        self.vendor = data.attrib.get('vendor')
        self.version = data.attrib.get('version')

    def connect(self):
        """Connect"""
        try:
            data = self.query('/resources')[0]
            self._loadData(data)
        except Exception as err:
            log.error('%s: %s', self.baseurl, err)
            raise NotFound('No client found at: %s' % self.baseurl)

    def headers(self):
        """Default headers

        Returns:
            dict: default headers
        """
        headers = BASE_HEADERS
        if self.token:
            headers['X-Plex-Token'] = self.token
        return headers

    def proxyThroughServer(self, value=True):
        """Connect to the client via the server.

        Args:
            value (bool, optional): Description

        Raises:
            Unsupported: Cannot use client proxy with unknown server.
        """
        if value is True and not self.server:
            raise Unsupported('Cannot use client proxy with unknown server.')
        self._proxyThroughServer = value

    def query(self, path, method=None, headers=None, **kwargs):
        """Used to fetch relative paths to pms.

        Args:
            path (str): Relative path
            method (None, optional): requests.post etc
            headers (None, optional): Set headers manually
            **kwargs (TYPE): Passord to the http request used for filter, sorting.

        Returns:
            Element

        Raises:
            BadRequest: Http error and code
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
        """Send a command to the client

        Args:
            command (str): See the commands listed below
            proxy (None, optional): Description
            **params (dict): Description

        Returns:
            Element

        Raises:
            Unsupported: Unsupported clients
        """
        command = command.strip('/')
        controller = command.split('/')[0]
        if controller not in self.protocolCapabilities:
            raise Unsupported(
                'Client %s does not support the %s controller.' % (self.title, controller))
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
        """Return a full url

        Args:
            path (str): Relative path

        Returns:
            string: full path to PMS
        """
        if self.token:
            delim = '&' if '?' in path else '?'
            return '%s%s%sX-Plex-Token=%s' % (self.baseurl, path, delim, self.token)
        return '%s%s' % (self.baseurl, path)

    # Navigation Commands
    # These commands navigate around the user-interface.
    def contextMenu(self):
        """Open the context menu on the client."""
        self.sendCommand('navigation/contextMenu')

    def goBack(self):
        """One step back"""
        self.sendCommand('navigation/back')

    def goToHome(self):
        """Jump to home screen."""
        self.sendCommand('navigation/home')

    def goToMusic(self):
        """Jump to music."""
        self.sendCommand('navigation/music')

    def moveDown(self):
        """One step down."""
        self.sendCommand('navigation/moveDown')

    def moveLeft(self):
        self.sendCommand('navigation/moveLeft')

    def moveRight(self):
        self.sendCommand('navigation/moveRight')

    def moveUp(self):
        self.sendCommand('navigation/moveUp')

    def nextLetter(self):
        """Jump to the next letter in the alphabeth."""
        self.sendCommand('navigation/nextLetter')

    def pageDown(self):
        self.sendCommand('navigation/pageDown')

    def pageUp(self):
        self.sendCommand('navigation/pageUp')

    def previousLetter(self):
        self.sendCommand('navigation/previousLetter')

    def select(self):
        self.sendCommand('navigation/select')

    def toggleOSD(self):
        self.sendCommand('navigation/toggleOSD')

    def goToMedia(self, media, **params):
        """Go to a media on the client.

        Args:
            media (str): movie, music, photo
            **params (TYPE): Description # todo

        Raises:
            Unsupported: Description
        """
        if not self.server:
            raise Unsupported(
                'A server must be specified before using this command.')
        server_url = media.server.baseurl.split(':')
        self.sendCommand('mirror/details', **dict({
            'machineIdentifier': self.server.machineIdentifier,
            'address': server_url[1].strip('/'),
            'port': server_url[-1],
            'key': media.key,
        }, **params))

    # Playback Commands
    # Most of the playback commands take a mandatory mtype {'music','photo','video'} argument,
    # to specify which media type to apply the command to, (except for playMedia). This
    # is in case there are multiple things happening (e.g. music in the background, photo
    # slideshow in the foreground).

    def pause(self, mtype):
        """Pause playback

        Args:
            mtype (str): music, photo, video
        """
        self.sendCommand('playback/pause', type=mtype)

    def play(self, mtype):
        """Start playback

        Args:
            mtype (str): music, photo, video
        """
        self.sendCommand('playback/play', type=mtype)

    def refreshPlayQueue(self, playQueueID, mtype=None):
        """Summary

        Args:
            playQueueID (TYPE): Description
            mtype (None, optional): photo, video, music

        """
        self.sendCommand(
            'playback/refreshPlayQueue', playQueueID=playQueueID, type=mtype)

    def seekTo(self, offset, mtype=None):
        """Seek to a time in a plaback.

        Args:
            offset (int): in milliseconds
            mtype (None, optional): photo, video, music

        """
        self.sendCommand('playback/seekTo', offset=offset, type=mtype)

    def skipNext(self, mtype=None):
        """Skip to next

        Args:
            mtype (None, string, optional): photo, video, music
        """
        self.sendCommand('playback/skipNext', type=mtype)

    def skipPrevious(self, mtype=None):
        """Skip to previous

        Args:
            mtype (None, optional): Description
        """
        self.sendCommand('playback/skipPrevious', type=mtype)

    def skipTo(self, key, mtype=None):
        """Jump to

        Args:
            key (TYPE): # what is this
            mtype (None, optional): photo, video, music

        Returns:
            TYPE: Description
        """
        # skips to item with matching key
        self.sendCommand('playback/skipTo', key=key, type=mtype)

    def stepBack(self, mtype=None):
        """

        Args:
            mtype (None, optional): photo, video, music
        """
        self.sendCommand('playback/stepBack', type=mtype)

    def stepForward(self, mtype):
        """Summary

        Args:
            mtype (TYPE): Description

        Returns:
            TYPE: Description
        """
        self.sendCommand('playback/stepForward', type=mtype)

    def stop(self, mtype):
        """Stop playback

        Args:
            mtype (str): video, music, photo

        """
        self.sendCommand('playback/stop', type=mtype)

    def setRepeat(self, repeat, mtype):
        """Summary

        Args:
            repeat (int): 0=off, 1=repeatone, 2=repeatall
            mtype (TYPE): video, music, photo
        """
        self.setParameters(repeat=repeat, mtype=mtype)

    def setShuffle(self, shuffle, mtype):
        """Set shuffle

        Args:
            shuffle (int): 0=off, 1=on
            mtype (TYPE): Description
        """
        self.setParameters(shuffle=shuffle, mtype=mtype)

    def setVolume(self, volume, mtype):
        """Change volume

        Args:
            volume (int): 0-100
            mtype (TYPE): Description
        """
        self.setParameters(volume=volume, mtype=mtype)

    def setAudioStream(self, audioStreamID, mtype):
        """Select a audio stream

        Args:
            audioStreamID (TYPE): Description
            mtype (str): video, music, photo
        """
        self.setStreams(audioStreamID=audioStreamID, mtype=mtype)

    def setSubtitleStream(self, subtitleStreamID, mtype):
        """Select a subtitle

        Args:
            subtitleStreamID (TYPE): Description
            mtype (str): video, music, photo
        """
        self.setStreams(subtitleStreamID=subtitleStreamID, mtype=mtype)

    def setVideoStream(self, videoStreamID, mtype):
        """Summary

        Args:
            videoStreamID (TYPE): Description
            mtype (str): video, music, photo

        """
        self.setStreams(videoStreamID=videoStreamID, mtype=mtype)

    def playMedia(self, media, **params):
        """Start playback on a media item.

        Args:
            media (str): movie, music, photo
            **params (TYPE): Description

        Raises:
            Unsupported: Description
        """
        if not self.server:
            raise Unsupported(
                'A server must be specified before using this command.')
        server_url = media.server.baseurl.split(':')
        playqueue = self.server.createPlayQueue(media)
        self.sendCommand('playback/playMedia', **dict({
            'machineIdentifier': self.server.machineIdentifier,
            'address': server_url[1].strip('/'),
            'port': server_url[-1],
            'key': media.key,
            'containerKey': '/playQueues/%s?window=100&own=1' % playqueue.playQueueID,
        }, **params))

    def setParameters(self, volume=None, shuffle=None, repeat=None, mtype=None):
        """Set params for the client

        Args:
            volume (None, optional): 0-100
            shuffle (None, optional): 0=off, 1=on
            repeat (None, optional): 0=off, 1=repeatone, 2=repeatall
            mtype (None, optional): music,photo,video
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

    def setStreams(self, audioStreamID=None, subtitleStreamID=None,
                   videoStreamID=None, mtype=None):
        """Select streams.

        Args:
            audioStreamID (None, optional): Description
            subtitleStreamID (None, optional): Description
            videoStreamID (None, optional): Description
            mtype (None, optional): music,photo,video
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

    # Timeline Commands
    def timeline(self):
        """Timeline"""
        return self.sendCommand('timeline/poll', **{'wait': 1, 'commandID': 4})

    def isPlayingMedia(self, includePaused=False):
        """Check timeline if anything is playing

        Args:
            includePaused (bool, optional): Should paused be included

        Returns:
            bool
        """
        for mediatype in self.timeline():
            if mediatype.get('state') == 'playing':
                return True
            if includePaused and mediatype.get('state') == 'paused':
                return True
        return False
