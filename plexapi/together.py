# -*- coding: utf-8 -*-
import requests

from plexapi import utils


class RoomUser:
    """ Represents a single RoomUser."""

    def __init__(self, data):
        self._data = data
        self.id = data.get('id')
        self.subscription = data.get('subscription')
        self.thumbUri = data.get('thumb')
        self.username = data.get('title')
        self.uuid = data.get('uuid')


class Room:
    """ Represents a single Room."""

    def __init__(self, data):
        self._data = data
        self.endsAt = utils.toDatetime(data.get('endsAt'))
        self.id = data.get('id')
        self.sourceUri = data.get('sourceUri')
        self.startsAt = utils.toDatetime(data.get('startsAt'))
        self.syncplayHost = data.get('syncplayHost')
        self.syncplayPort = data.get('syncplayPort')
        self.title = data.get('title')
        self.users = [RoomUser(user) for user in data.get('users', [])]
        self.updatedAt = utils.toDatetime(data.get('updatedAt'))
        self.source = data.get('source')


class Together:
    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self._token = token

    @property
    def rooms(self):
        rooms = []
        res = requests.get(self.endpoint + 'rooms', headers={'X-Plex-Token': self._token})
        if res:
            data = res.json()
            for room in data.get('rooms', []):
                rooms.append(Room(room))
        return rooms
