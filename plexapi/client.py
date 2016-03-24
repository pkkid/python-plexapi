# -*- coding: utf-8 -*-
"""
PlexAPI Client
To understand how this works, read this page:
https://github.com/plexinc/plex-media-player/wiki/Remote-control-API
"""
import requests
from requests.status_codes import _codes as codes
from plexapi import TIMEOUT, log, utils
from plexapi.exceptions import BadRequest, Unsupported
from xml.etree import ElementTree


class Client(object):

    def __init__(self, server, data):
        self.server = server
        self.name = data.attrib.get('name')
        self.host = data.attrib.get('host')
        self.address = data.attrib.get('address')
        self.port = data.attrib.get('port')
        self.machineIdentifier = data.attrib.get('machineIdentifier')
        self.title = data.attrib.get('title')
        self.version = data.attrib.get('version')
        self.platform = data.attrib.get('platform')
        self.protocol = data.attrib.get('protocol')
        self.product = data.attrib.get('product')
        self.deviceClass = data.attrib.get('deviceClass')
        self.protocolVersion = data.attrib.get('protocolVersion')
        self.protocolCapabilities = data.attrib.get('protocolCapabilities', '').split(',')
        self.state = data.attrib.get('state')
        self._proxyThroughServer = False
        self._commandId = 0

    @property
    def quickName(self):
        return self.name or self.product

    def proxyThroughServer(self, value=True):
        self._proxyThroughServer = value

    def sendCommand(self, command, proxy=None, **params):
        proxy = self._proxyThroughServer if proxy is None else proxy
        if proxy: return self.sendServerCommand(command, **params)
        return self.sendClientCommand(command, **params)

    def sendClientCommand(self, command, **params):
        command = command.strip('/')
        controller = command.split('/')[1]
        if controller not in self.protocolCapabilities:
            raise Unsupported('Client %s does not support the %s controller.' % (self.quickName, controller))
        self._commandId += 1
        params.update({
            'X-Plex-Device-Name': self.name,
            'X-Plex-Client-Identifier': self.server.machineIdentifier,
            'X-Plex-Target-Client-Identifier': self.machineIdentifier,
            'commandID': self._commandId,
        })
        url = 'http://%s:%s/%s%s' % (self.address, self.port, command.lstrip('/'), utils.joinArgs(params))
        log.info('GET %s', url)
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code != requests.codes.ok:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None

    def sendServerCommand(self, command, **params):
        params.update({'commandID': self._commandId})
        path = '/system/players/%s/%s%s' % (self.address, command, utils.joinArgs(params))
        self.server.query(path)

    # Navigation Commands
    # These commands navigate around the user interface.
    def contextMenu(self): self.sendCommand('player/navigation/contextMenu')
    def goBack(self): self.sendCommand('player/navigation/back')
    def goToHome(self): self.sendCommand('/player/navigation/home')
    def goToMusic(self): self.sendCommand('/player/navigation/music')
    def moveDown(self): self.sendCommand('player/navigation/moveDown')
    def moveLeft(self): self.sendCommand('player/navigation/moveLeft')
    def moveRight(self): self.sendCommand('player/navigation/moveRight')
    def moveUp(self): self.sendCommand('player/navigation/moveUp')
    def nextLetter(self): self.sendCommand('player/navigation/nextLetter')
    def pageDown(self): self.sendCommand('player/navigation/pageDown')
    def pageUp(self): self.sendCommand('player/navigation/pageUp')
    def previousLetter(self): self.sendCommand('player/navigation/previousLetter')
    def select(self): self.sendCommand('player/navigation/select')
    def toggleOSD(self): self.sendCommand('player/navigation/toggleOSD')

    def goToMedia(self, media, **params):
        server_uri = media.server.baseuri.split(':')
        self.sendCommand('player/mirror/details', **dict({
            'machineIdentifier': self.server.machineIdentifier,
            'address': server_uri[1].strip('/'),
            'port': server_uri[-1],
            'key': media.key,
        }, **params))

    # Playback Commands
    # most of the playback commands take a mandatory mtype {'music','photo','video'} argument,
    # to specify which media type to apply the command to, (except for playMedia). This
    # is in case there are multiple things happening (e.g. music in the background, photo
    # slideshow in the foreground).
    def pause(self, mtype): self.sendCommand('player/playback/pause', type=mtype)
    def play(self, mtype): self.sendCommand('player/playback/play', type=mtype)
    def refreshPlayQueue(self, playQueueID, mtype=None): self.sendCommand('player/playback/refreshPlayQueue', playQueueID=playQueueID, type=mtype)
    def seekTo(self, offset, mtype=None): self.sendCommand('player/playback/seekTo', offset=offset, type=mtype)  # offset in milliseconds
    def skipNext(self, mtype=None): self.sendCommand('player/playback/skipNext', type=mtype)
    def skipPrevious(self, mtype=None): self.sendCommand('player/playback/skipPrevious', type=mtype)
    def skipTo(self, key, mtype=None): self.sendCommand('player/playback/skipTo', key=key, type=mtype)  # skips to item with matching key
    def stepBack(self, mtype=None): self.sendCommand('player/playback/stepBack', type=mtype)
    def stepForward(self, mtype): self.sendCommand('player/playback/stepForward', type=mtype)
    def stop(self, mtype): self.sendCommand('player/playback/stop', type=mtype)
    def setRepeat(self, repeat, mtype): self.setParameters(repeat=repeat, mtype=mtype)      # 0=off, 1=repeatone, 2=repeatall
    def setShuffle(self, shuffle, mtype): self.setParameters(shuffle=shuffle, mtype=mtype)  # 0=off, 1=on
    def setVolume(self, volume, mtype): self.setParameters(volume=volume, mtype=mtype)      # 0-100
    def setAudioStream(self, audioStreamID, mtype): self.setStreams(audioStreamID=audioStreamID, mtype=mtype)
    def setSubtitleStream(self, subtitleStreamID, mtype): self.setStreams(subtitleStreamID=subtitleStreamID, mtype=mtype)
    def setVideoStream(self, videoStreamID, mtype): self.setStreams(videoStreamID=videoStreamID, mtype=mtype)
    
    def playMedia(self, media, **params):
        server_uri = media.server.baseuri.split(':')
        playqueue = self.server.createPlayQueue(media)
        self.sendCommand('player/playback/playMedia', **dict({
            'machineIdentifier': self.server.machineIdentifier,
            'address': server_uri[1].strip('/'),
            'port': server_uri[-1],
            'key': media.key,
            'containerKey': '/playQueues/%s?window=100&own=1' % playqueue.playQueueID,
        }, **params))
        
    def setParameters(self, volume=None, shuffle=None, repeat=None, mtype=None):
        params = {}
        if repeat is not None: params['repeat'] = repeat        # 0=off, 1=repeatone, 2=repeatall
        if shuffle is not None: params['shuffle'] = shuffle     # 0=off, 1=on
        if volume is not None: params['volume'] = volume        # 0-100
        if mtype is not None: params['type'] = mtype            # music,photo,video
        self.sendCommand('player/playback/setParameters', **params)
        
    def setStreams(self, audioStreamID=None, subtitleStreamID=None, videoStreamID=None, mtype=None):
        # Can possibly send {next,on,off}
        params = {}
        if audioStreamID is not None: params['audioStreamID'] = audioStreamID
        if subtitleStreamID is not None: params['subtitleStreamID'] = subtitleStreamID
        if videoStreamID is not None: params['videoStreamID'] = videoStreamID
        if mtype is not None: params['type'] = mtype  # music,photo,video
        self.sendCommand('player/playback/setStreams', **params)
        
    # Timeline Commands
    def timeline(self):
        self.sendCommand('timeline/poll', **{'wait':1, 'commandID':4})

    def isPlayingMedia(self):
        timeline = self.timeline()
        for media_type in timeline:
            if media_type.get('state') == 'playing':
                return True
        return False
