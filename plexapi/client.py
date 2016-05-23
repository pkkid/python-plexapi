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

    def __init__(self, baseurl, token=None, session=None, server=None, data=None):
        self.baseurl = baseurl.strip('/')
        self.token = token
        self.session = session or requests.Session()
        self.server = server
        self._loadData(data) if data is not None else self.connect()
        self._proxyThroughServer = False
        self._commandId = 0

    def _loadData(self, data):
        self.deviceClass = data.attrib.get('deviceClass')
        self.machineIdentifier = data.attrib.get('machineIdentifier')
        self.product = data.attrib.get('product')
        self.protocol = data.attrib.get('protocol')
        self.protocolCapabilities = data.attrib.get('protocolCapabilities', '').split(',')
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
        try:
            data = self.query('/resources')[0]
            self._loadData(data)
        except Exception as err:
            log.error('%s: %s', self.baseurl, err)
            raise NotFound('No client found at: %s' % self.baseurl)
        
    def headers(self):
        headers = BASE_HEADERS
        if self.token:
            headers['X-Plex-Token'] = self.token
        return headers

    def proxyThroughServer(self, value=True):
        if value is True and not self.server:
            raise Unsupported('Cannot use client proxy with unknown server.')
        self._proxyThroughServer = value

    def query(self, path, method=None, headers=None, **kwargs):
        url = self.url(path)
        method = method or self.session.get
        log.info('%s %s', method.__name__.upper(), url)
        headers = dict(self.headers(), **(headers or {}))
        response = method(url, headers=headers, timeout=TIMEOUT, **kwargs)
        if response.status_code not in [200, 201]:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None

    def sendCommand(self, command, proxy=None, **params):
        command = command.strip('/')
        controller = command.split('/')[0]
        if controller not in self.protocolCapabilities:
            raise Unsupported('Client %s does not support the %s controller.' % (self.title, controller))
        path = '/player/%s%s' % (command, utils.joinArgs(params))
        headers = {'X-Plex-Target-Client-Identifier':self.machineIdentifier}
        self._commandId += 1; params['commandID'] = self._commandId
        proxy = self._proxyThroughServer if proxy is None else proxy
        if proxy:
            return self.server.query(path, headers=headers)
        path = '/player/%s%s' % (command, utils.joinArgs(params))
        return self.query(path, headers=headers)
        
    def url(self, path):
        if self.token:
            delim = '&' if '?' in path else '?'
            return '%s%s%sX-Plex-Token=%s' % (self.baseurl, path, delim, self.token)
        return '%s%s' % (self.baseurl, path)

    # Navigation Commands
    # These commands navigate around the user-interface.
    def contextMenu(self): self.sendCommand('navigation/contextMenu')
    def goBack(self): self.sendCommand('navigation/back')
    def goToHome(self): self.sendCommand('navigation/home')
    def goToMusic(self): self.sendCommand('navigation/music')
    def moveDown(self): self.sendCommand('navigation/moveDown')
    def moveLeft(self): self.sendCommand('navigation/moveLeft')
    def moveRight(self): self.sendCommand('navigation/moveRight')
    def moveUp(self): self.sendCommand('navigation/moveUp')
    def nextLetter(self): self.sendCommand('navigation/nextLetter')
    def pageDown(self): self.sendCommand('navigation/pageDown')
    def pageUp(self): self.sendCommand('navigation/pageUp')
    def previousLetter(self): self.sendCommand('navigation/previousLetter')
    def select(self): self.sendCommand('navigation/select')
    def toggleOSD(self): self.sendCommand('navigation/toggleOSD')

    def goToMedia(self, media, **params):
        if not self.server:
            raise Unsupported('A server must be specified before using this command.')
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
    def pause(self, mtype): self.sendCommand('playback/pause', type=mtype)
    def play(self, mtype): self.sendCommand('playback/play', type=mtype)
    def refreshPlayQueue(self, playQueueID, mtype=None): self.sendCommand('playback/refreshPlayQueue', playQueueID=playQueueID, type=mtype)
    def seekTo(self, offset, mtype=None): self.sendCommand('playback/seekTo', offset=offset, type=mtype)  # offset in milliseconds
    def skipNext(self, mtype=None): self.sendCommand('playback/skipNext', type=mtype)
    def skipPrevious(self, mtype=None): self.sendCommand('playback/skipPrevious', type=mtype)
    def skipTo(self, key, mtype=None): self.sendCommand('playback/skipTo', key=key, type=mtype)  # skips to item with matching key
    def stepBack(self, mtype=None): self.sendCommand('playback/stepBack', type=mtype)
    def stepForward(self, mtype): self.sendCommand('playback/stepForward', type=mtype)
    def stop(self, mtype): self.sendCommand('playback/stop', type=mtype)
    def setRepeat(self, repeat, mtype): self.setParameters(repeat=repeat, mtype=mtype)      # 0=off, 1=repeatone, 2=repeatall
    def setShuffle(self, shuffle, mtype): self.setParameters(shuffle=shuffle, mtype=mtype)  # 0=off, 1=on
    def setVolume(self, volume, mtype): self.setParameters(volume=volume, mtype=mtype)      # 0-100
    def setAudioStream(self, audioStreamID, mtype): self.setStreams(audioStreamID=audioStreamID, mtype=mtype)
    def setSubtitleStream(self, subtitleStreamID, mtype): self.setStreams(subtitleStreamID=subtitleStreamID, mtype=mtype)
    def setVideoStream(self, videoStreamID, mtype): self.setStreams(videoStreamID=videoStreamID, mtype=mtype)
    
    def playMedia(self, media, **params):
        if not self.server:
            raise Unsupported('A server must be specified before using this command.')
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
        params = {}
        if repeat is not None: params['repeat'] = repeat        # 0=off, 1=repeatone, 2=repeatall
        if shuffle is not None: params['shuffle'] = shuffle     # 0=off, 1=on
        if volume is not None: params['volume'] = volume        # 0-100
        if mtype is not None: params['type'] = mtype            # music,photo,video
        self.sendCommand('playback/setParameters', **params)
        
    def setStreams(self, audioStreamID=None, subtitleStreamID=None, videoStreamID=None, mtype=None):
        params = {}
        if audioStreamID is not None: params['audioStreamID'] = audioStreamID
        if subtitleStreamID is not None: params['subtitleStreamID'] = subtitleStreamID
        if videoStreamID is not None: params['videoStreamID'] = videoStreamID
        if mtype is not None: params['type'] = mtype  # music,photo,video
        self.sendCommand('playback/setStreams', **params)
        
    # Timeline Commands
    def timeline(self):
        return self.sendCommand('timeline/poll', **{'wait':1, 'commandID':4})

    def isPlayingMedia(self, includePaused=False):
        for mediatype in self.timeline():
            if mediatype.get('state') == 'playing':
                return True
            if includePaused and mediatype.get('state') == 'paused':
                return True
        return False
