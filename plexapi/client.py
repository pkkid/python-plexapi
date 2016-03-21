# -*- coding: utf-8 -*-
"""
PlexAPI Client
https://github.com/plexinc/plex-media-player/wiki/Remote-control-API
"""
import requests
from requests.status_codes import _codes as codes
from plexapi import TIMEOUT, log, utils
from plexapi.exceptions import BadRequest
from xml.etree import ElementTree

SERVER = 'server'
CLIENT = 'client'


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
        self._sendCommandsTo = CLIENT

    def sendCommandsTo(self, value):
        self._sendCommandsTo = value

    def sendCommand(self, command, args=None, sendTo=None):
        sendTo = sendTo or self._sendCommandsTo
        if sendTo == CLIENT:
            return self.sendClientCommand(command, args)
        return self.sendServerCommand(command, args)

    def sendClientCommand(self, command, args=None):
        args = args or {}
        args.update({
            'X-Plex-Target-Client-Identifier': self.machineIdentifier,
            'X-Plex-Device-Name': self.name,
            'X-Plex-Client-Identifier': self.server.machineIdentifier,
            'type': 'video',  # TODO: Make this with any media type or passed in as an arg
        })
        url = '%s%s' % (self.url(command), utils.joinArgs(args))
        log.info('GET %s', url)
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code != requests.codes.ok:
            codename = codes.get(response.status_code)[0]
            raise BadRequest('(%s) %s' % (response.status_code, codename))
        data = response.text.encode('utf8')
        return ElementTree.fromstring(data) if data else None

    def sendServerCommand(self, command, args=None):
        # TODO: Rip this out, server is throwing exceptions, maybe deprecated?
        path = '/system/players/%s/%s%s' % (self.address, command, utils.joinArgs(args))
        self.server.query(path)

    def url(self, path):
        return 'http://%s:%s/player/%s' % (self.address, self.port, path.lstrip('/'))

    # Navigation Commands
    def moveUp(self): self.sendCommand('navigation/moveUp')
    def moveDown(self): self.sendCommand('navigation/moveDown')
    def moveLeft(self): self.sendCommand('navigation/moveLeft')
    def moveRight(self): self.sendCommand('navigation/moveRight')
    def pageUp(self): self.sendCommand('navigation/pageUp')
    def pageDown(self): self.sendCommand('navigation/pageDown')
    def nextLetter(self): self.sendCommand('navigation/nextLetter')
    def previousLetter(self): self.sendCommand('navigation/previousLetter')
    def select(self): self.sendCommand('navigation/select')
    def back(self): self.sendCommand('navigation/back')
    def contextMenu(self): self.sendCommand('navigation/contextMenu')
    def toggleOSD(self): self.sendCommand('navigation/toggleOSD')

    # Playback Commands
    def play(self): self.sendCommand('playback/play')
    def pause(self): self.sendCommand('playback/pause')
    def stop(self): self.sendCommand('playback/stop')
    def stepForward(self): self.sendCommand('playback/stepForward')
    def bigStepForward(self): self.sendCommand('playback/bigStepForward')
    def stepBack(self): self.sendCommand('playback/stepBack')
    def bigStepBack(self): self.sendCommand('playback/bigStepBack')
    def skipNext(self): self.sendCommand('playback/skipNext')
    def skipPrevious(self): self.sendCommand('playback/skipPrevious')

    def playMedia(self, video, viewOffset=0):
        playqueue = self.server.createPlayQueue(video)
        self.sendCommand('playback/playMedia', {
            'machineIdentifier': self.server.machineIdentifier,
            'containerKey': '/playQueues/%s?window=100&own=1' % playqueue.playQueueID,
            'key': video.key,
            'offset': 0,
        })

    def timeline(self):
        params = {'wait':1, 'commandID':4}
        return self.server.query('timeline/poll', params=params)

    def isPlayingMedia(self):
        # http://192.168.1.31:32500/player/timeline/poll?commandID=4&wait=1&X-Plex-Target-Client-Identifier=198D670A-DE1B-4BF2-BE55-10B4D98E1532&X-Plex-Device-Name=iphone-mike&X-Plex-Client-Identifier=792f0ff5fa644d63ff1e6ea8b130dade08716cb1
        timeline = self.timeline()
        for media_type in timeline:
            if media_type.get('state') == 'playing':
                return True
        return False
