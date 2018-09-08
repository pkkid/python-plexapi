from plexapi.base import PlexObject
from plexapi.exceptions import BadRequest
from plexapi.library import Hub


class MediaProvider(PlexObject):
    def _loadData(self, data):
        self._data = data

        self.baseURL = data.attrib.get('baseURL')
        self.title = data.attrib.get('title')
        self.icon = data.attrib.get('icon')
        self.token = data.attrib.get('token')
        self.identifier = data.attrib.get('identifier')

    def load(self):
        url = self.baseURL + '/hubs/sections/home?excludeFields=summary&count=16&includeEmpty=1&includeFeaturedTags=1' \
                             '&excludePlaylists=1&onlyTransient=1'
        self._hubs = self.fetchItems(url, Hub)
        return self._hubs

    def hub(self, title):
        for hub in self.hubs():
            if hub.title == title:
                return hub
        raise BadRequest('Unable to find requested hub')

    def hubs(self):
        if not hasattr(self, '_hubs'):
            self.load()

        return self._hubs
