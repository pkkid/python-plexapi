# -*- coding: utf-8 -*-
import re
from plexapi import log, utils
from plexapi.compat import urlencode
from plexapi.exceptions import NotFound, UnknownType, Unsupported


class Playable(object):
    """ This is a general place to store functions specific to media that is Playable.
        Things were getting mixed up a bit when dealing with Shows, Season, Artists,
        Albums which are all not playable.

        Attributes:
            player (:class:`~plexapi.client.PlexClient`): Client object playing this item (for active sessions).
            playlistItemID (int): Playlist item ID (only populated for :class:`~plexapi.playlist.Playlist` items).
            sessionKey (int): Active session key.
            transcodeSession (:class:`~plexapi.media.TranscodeSession`): Transcode Session object
                if item is being transcoded (None otherwise).
            username (str): Username of the person playing this item (for active sessions).
            viewedAt (datetime): Datetime item was last viewed (history).
    """
    def _loadData(self, data):
        # Load data for active sessions (/status/sessions)
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey'))
        self.username = utils.findUsername(data)
        self.player = utils.findPlayer(self._root, data)
        self.transcodeSession = utils.findTranscodeSession(self._root, data)
        # Load data for history details (/status/sessions/history/all)
        self.viewedAt = utils.toDatetime(data.attrib.get('viewedAt'))
        # Load data for playlist items
        self.playlistItemID = utils.cast(int, data.attrib.get('playlistItemID'))

    def getStreamURL(self, **params):
        """ Returns a stream url that may be used by external applications such as VLC.

            Parameters:
                **params (dict): optional parameters to manipulate the playback when accessing
                    the stream. A few known parameters include: maxVideoBitrate, videoResolution
                    offset, copyts, protocol, mediaIndex, platform.

            Raises:
                Unsupported: When the item doesn't support fetching a stream URL.
        """
        if self.TYPE not in ('movie', 'episode', 'track'):
            raise Unsupported('Fetching stream URL for %s is unsupported.' % self.TYPE)
        mvb = params.get('maxVideoBitrate')
        vr = params.get('videoResolution', '')
        params = {
            'path': self.key,
            'offset': params.get('offset', 0),
            'copyts': params.get('copyts', 1),
            'protocol': params.get('protocol'),
            'mediaIndex': params.get('mediaIndex', 0),
            'X-Plex-Platform': params.get('platform', 'Chrome'),
            'maxVideoBitrate': max(mvb, 64) if mvb else None,
            'videoResolution': vr if re.match('^\d+x\d+$', vr) else None
        }
        # remove None values
        params = {k: v for k, v in params.items() if v is not None}
        streamtype = 'audio' if self.TYPE in ('track', 'album') else 'video'
        # sort the keys since the randomness fucks with my tests..
        sorted_params = sorted(params.items(), key=lambda val: val[0])
        return self._root.url('/%s/:/transcode/universal/start.m3u8?%s' %
            (streamtype, urlencode(sorted_params)))

    def iterParts(self):
        """ Iterates over the parts of this media item. """
        for item in self.media:
            for part in item.parts:
                yield part

    def play(self, client):
        """ Start playback on the specified client.

            Parameters:
                client (:class:`~plexapi.client.PlexClient`): Client to start playing on.
        """
        client.playMedia(self)

    def download(self, savepath=None, keep_orginal_name=False, **kwargs):
        """ Downloads this items media to the specified location. Returns a list of
            filepaths that have been saved to disk.
            
            Parameters:
                savepath (str): Title of the track to return.
                keep_orginal_name (bool): Set True to keep the original filename as stored in
                    the Plex server. False will create a new filename with the format
                    "<Atrist> - <Album> <Track>".
                kwargs (dict): If specified, a :func:`~plexapi.audio.Track.getStreamURL()` will
                    be returned and the additional arguments passed in will be sent to that
                    function. If kwargs is not specified, the media items will be downloaded
                    and saved to disk.
        """
        filepaths = []
        locations = [i for i in self.iterParts() if i]
        for location in locations:
            filename = location.file
            if keep_orginal_name is False:
                filename = '%s.%s' % (self._prettyfilename(), location.container)
            # So this seems to be a alot slower but allows transcode.
            if kwargs:
                download_url = self.getStreamURL(**kwargs)
            else:
                download_url = self._root.url('%s?download=1' % location.key)
            filepath = utils.download(download_url, filename=filename,
                savepath=savepath, session=self._root.session)
            if filepath:
                filepaths.append(filepath)
        return filepaths


class PlexObject(object):
    """ Base class for all Plex objects.
        TODO: Finish documenting this.
    """
    key = None

    def __init__(self, root, data, initpath=None):
        self._root = root                       # Root MyPlexAccount or PlexServer
        self._data = data                       # XML data needed to build object
        self._initpath = initpath or self.key   # Request path used to fetch data
        self._loadData(data)

    def __setattr__(self, attr, value):
        if value is not None or attr.startswith('_'):
            self.__dict__[attr] = value

    def _buildItem(self, elem, initpath, bytag=False):
        """ Factory function to build objects based on registered LIBRARY_TYPES. """
        libtype = elem.tag if bytag else elem.attrib.get('type')
        if libtype == 'photo' and elem.tag == 'Directory':
            libtype = 'photoalbum'
        if libtype in utils.LIBRARY_TYPES:
            cls = utils.LIBRARY_TYPES[libtype]
            return cls(self._root, elem, initpath)
        raise UnknownType('Unknown library type: %s' % libtype)

    def _buildSubitems(self, data, cls, tag=None, filters=None, *args):
        """ Build and return a list of items (optionally filtered by tag). """
        items = []
        tag = tag or cls.TYPE
        filters = filters or {}
        for elem in data:
            if elem.tag == tag:
                for attr, value in filters.items():
                    if elem.attrib.get(attr) != str(value):
                        continue
                items.append(cls(self._root, elem, self._initpath, *args))
        return items

    def _fetchItem(self, key, title=None, name=None):
        for elem in self._root._query(key):
            if title and elem.attrib.get('title').lower() == title.lower():
                return self._buildItem(elem, key)
            if name and elem.attrib.get('name').lower() == name.lower():
                return self._buildItem(elem, key)
        raise NotFound('Unable to find item: %s' % (title or name))

    def _fetchItems(self, key, libtype=None, bytag=False):
        """ Fetch and build items from the specified key. """
        items = []
        for elem in self._root._query(key):
            try:
                if not libtype or elem.attrib.get('type') == libtype:
                    items.append(self._buildItem(elem, key, bytag))
            except UnknownType:
                pass
        return items

    def _loadData(self, data):
        raise NotImplemented('Abstract method not implemented.')

    def reload(self, safe=False):
        """ Reload the data for this object from self.key. """
        if not self.key:
            if safe: return None
            raise Unsupported('Cannot reload an object not built from a URL.')
        self._initpath = self.key
        data = self._root._query(self.key)
        self._loadData(data[0])


class PlexPartialObject(PlexObject):
    """ Not all objects in the Plex listings return the complete list of elements
        for the object. This object will allow you to assume each object is complete,
        and if the specified value you request is None it will fetch the full object
        automatically and update itself.

        Attributes:
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
    """
    def __eq__(self, other):
        return other is not None and self.key == other.key

    def __repr__(self):
        clsname = self.__class__.__name__
        key = self.key.replace('/library/metadata/', '') if self.key else 'NA'
        title = self.title.replace(' ', '.')[0:20].encode('utf8')
        return '<%s:%s:%s>' % (clsname, key, title)

    def __getattribute__(self, attr):
        # Check a few cases where we dont want to reload
        value = super(PlexPartialObject, self).__getattribute__(attr)
        if attr == 'key' or attr.startswith('_'): return value
        if value not in (None, []): return value
        if self.isFullObject(): return value
        # Log warning that were reloading the object
        clsname = self.__class__.__name__
        title = self.__dict__.get('title', self.__dict__.get('name'))
        objname = "%s '%s'" % (clsname, title) if title else clsname
        log.warn("Reloading %s for attr '%s'" % (objname, attr))
        # Reload and return the value
        self.reload()
        return super(PlexPartialObject, self).__getattribute__(attr)

    def isFullObject(self):
        """ Retruns True if this is already a full object. A full object means all attributes
            were populated from the api path representing only this item. For example, the
            search result for a movie often only contain a portion of the attributes a full
            object (main url) for that movie contain.
        """
        return not self.key or self.key == self._initpath

    def isPartialObject(self):
        """ Returns True if this is not a full object. """
        return not self.isFullObject()
