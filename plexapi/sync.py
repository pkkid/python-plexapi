"""
PlexAPI Sync
"""
import requests
from plexapi.exceptions import NotFound
from plexapi.video import list_items
from plexapi.utils import cast


class SyncItem(object):
    def __init__(self, device, data, servers=None):
        self.device = device
        self.servers = servers
        self.id = cast(int, data.attrib.get('id'))
        self.version = cast(int, data.attrib.get('version'))
        self.rootTitle = data.attrib.get('rootTitle')
        self.title = data.attrib.get('title')
        self.metadataType = data.attrib.get('metadataType')
        self.machineIdentifier = data.find('Server').get('machineIdentifier')
        self.status = data.find('Status').attrib.copy()
        self.MediaSettings = data.find('MediaSettings').attrib.copy()
        self.policy = data.find('Policy').attrib.copy()
        self.location = data.find('Location').attrib.copy()

    def __repr__(self):
        return '<{0}:{1}>'.format(self.__class__.__name__, self.id)

    def server(self):
        server = list(filter(lambda x: x.machineIdentifier == self.machineIdentifier, self.servers))
        if 0 == len(server):
            raise NotFound('Unable to find server with uuid %s' % self.machineIdentifier)

        return server[0]

    def getMedia(self):
        server = self.server().connect()
        items = list_items(server, '/sync/items/{0}'.format(self.id))
        return items

    def markAsDone(self, sync_id):
        server = self.server().connect()
        uri = '/sync/{0}/{1}/files/{2}/downloaded'.format(self.device.clientIdentifier, server.machineIdentifier, sync_id)
        server.query(uri, method=requests.put)
