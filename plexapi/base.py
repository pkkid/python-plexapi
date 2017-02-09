# -*- coding: utf-8 -*-
import re
from plexapi import log, utils
from plexapi.compat import urlencode
from plexapi.exceptions import BadRequest, NotFound
from plexapi.exceptions import UnknownType, Unsupported

OPERATORS = {
    'exact': lambda v,q: v == q,
    'iexact': lambda v,q: v.lower() == q.lower(),
    'contains': lambda v,q: q in v,
    'icontains': lambda v,q: q.lower() in v.lower(),
    'in': lambda v,q: v in q,
    'gt': lambda v,q: v > q,
    'gte': lambda v,q: v >= q,
    'lt': lambda v,q: v < q,
    'lte': lambda v,q: v <= q,
    'startswith': lambda v,q: v.startswith(q),
    'istartswith': lambda v,q: v.lower().startswith(q),
    'endswith': lambda v,q: v.endswith(q),
    'iendswith': lambda v,q: v.lower().endswith(q),
    'ismissing': None,  # special case in _checkAttrs
    'regex': lambda v,q: re.match(q, v),
    'iregex': lambda v,q: re.match(q, v, flags=re.IGNORECASE),
}


class PlexObject(object):
    """ Base class for all Plex objects.
        TODO: Finish documenting this.
    """
    key = None

    def __init__(self, root, data, initpath=None):
        self._server = root                       # Root MyPlexAccount or PlexServer
        self._data = data                       # XML data needed to build object
        self._initpath = initpath or self.key   # Request path used to fetch data
        self._loadData(data)

    def __repr__(self):
        return '<%s>' % ':'.join([p for p in [
            self.__class__.__name__,
            self.__firstattr('_baseurl', 'key', 'id', 'playQueueID', 'uri'),
            self.__firstattr('title', 'name', 'username', 'product', 'tag')
        ] if p])

    def __setattr__(self, attr, value):
        if value is not None or attr.startswith('_') or attr not in self.__dict__:
            self.__dict__[attr] = value

    def __firstattr(self, *attrs):
        for attr in attrs:
            value = self.__dict__.get(attr)
            if value:
                value = str(value).replace(' ','-')
                value = value.replace('/library/metadata/','')
                value = value.replace('/children','')
                return value[:20]

    def _buildItem(self, elem, cls=None, initpath=None, bytag=False):
        """ Factory function to build objects based on registered LIBRARY_TYPES. """
        initpath = initpath or self._initpath
        libtype = elem.tag if bytag else elem.attrib.get('type')
        if libtype == 'photo' and elem.tag == 'Directory':
            libtype = 'photoalbum'
        if cls and libtype == cls.TYPE:
            return cls(self._server, elem, initpath)
        if libtype in utils.LIBRARY_TYPES:
            cls = utils.LIBRARY_TYPES[libtype]
            return cls(self._server, elem, initpath)
        raise UnknownType("Unknown library type <%s type='%s'../>" % (elem.tag, libtype))

    def _buildItemOrNone(self, elem, cls=None, initpath=None, bytag=False):
        """ Calls :func:`~plexapi.base.PlexObject._buildItem()` but returns
            None if elem is an unknown type.
        """
        try:
            return self._buildItem(elem, cls, initpath, bytag)
        except UnknownType:
            return None

    def _buildItems(self, data, cls=None, initpath=None, bytag=False):
        """ Build and return a list of items (optionally filtered by tag).

            Parameters:
                data (ElementTree): XML data to search for items.
                cls (:class:`plexapi.base.PlexObject`): Optionally specify the PlexObject
                    to be built. If not specified _buildItem will be called and the best
                    guess item will be built.
        """
        items = []
        for elem in data:
            items.append(self._buildItemOrNone(elem, cls, initpath, bytag))
        return [item for item in items if item]

    def fetchItem(self, key, cls=None, bytag=False, tag=None, **kwargs):
        """ Load the specified key to find and build the first item with the
            specified tag and attrs. If no tag or attrs are specified then
            the first item in the result set is returned.

            Parameters:
                key (str or int): Path in Plex to fetch items from. If an int is passed
                    in, the key will be translated to /library/metadata/<key>. This allows
                    fetching an item only knowing its key-id.
                cls (:class:`~plexapi.base.PlexObject`): If you know the class of the
                    items to be fetched, passing this in will help the parser ensure 
                    it only returns those items. By default we convert the xml elements
                    to the best guess PlexObjects based on the type attr or tag.
                bytag (bool): Setting this to True tells the build-items function to guess
                    the PlexObject to build from the tag (instead of the type attr).
                tag (str): Only fetch items with the specified tag.
                **kwargs (dict): Optionally add attribute filters on the items to fetch. For
                    example, passing in viewCount=0 will only return matching items. Filtering
                    is done before the Python objects are built to help keep things speedy.
                    Note: Because some attribute names are already used as arguments to this
                    function, such as 'tag', you may still reference the attr tag byappending
                    an underscore. For example, passing in _tag='foobar' will return all items
                    where tag='foobar'. Also Note: Case very much matters when specifying kwargs
                    -- Optionally, operators can be specified by append it
                    to the end of the attribute name for more complex lookups. For example,
                    passing in viewCount__gte=0 will return all items where viewCount >= 0.
                    Available operations include:

                    * __exact: Value matches specified arg.
                    * __iexact: Case insensative value matches specified arg.
                    * __contains: Value contains specified arg.
                    * __icontains: Case insensative value contains specified arg.
                    * __in: Value is in a specified list or tuple.
                    * __gt: Value is greater than specified arg.
                    * __gte: Value is greater than or equal to specified arg.
                    * __lt: Value is less than specified arg.
                    * __lte: Value is less than or equal to specified arg.
                    * __startswith: Value starts with specified arg.
                    * __istartswith: Case insensative value starts with specified arg.
                    * __endswith: Value ends with specified arg.
                    * __iendswith: Case insensative value ends with specified arg.
                    * __ismissing (bool): Value is or is not present in the attrs.
                    * __regex: Value matches the specified regular expression.
                    * __iregex: Case insensative value matches the specified regular expression.
        """
        if isinstance(key, int):
            key = '/library/metadata/%s' % key
        for elem in self._server.query(key):
            if tag and elem.tag != tag or not self._checkAttrs(elem, **kwargs):
                continue
            return self._buildItem(elem, cls, key, bytag)
        raise NotFound('Unable to find elem: tag=%s, attrs=%s' % (tag, kwargs))

    def fetchItems(self, key, cls=None, bytag=False, tag=None, **kwargs):
        """ Load the specified key to find and build all items with the specified tag
            and attrs. See :func:`~plexapi.base.PlexObject.fetchItem` for more details
            on how this is used.
        """
        items = []
        for elem in self._server.query(key):
            if tag and elem.tag != tag or not self._checkAttrs(elem, **kwargs):
                continue
            items.append(self._buildItemOrNone(elem, cls, key, bytag))
        return [item for item in items if item]

    def reload(self, safe=False):
        """ Reload the data for this object from self.key. """
        if not self.key:
            if safe: return None
            raise Unsupported('Cannot reload an object not built from a URL.')
        self._initpath = self.key
        data = self._server.query(self.key)
        self._loadData(data[0])
        return self

    def _checkAttrs(self, elem, **kwargs):
        for kwarg, query in kwargs.items():
            # strip underscore from special cased attrs
            if kwarg in ('_key', '_cls', '_tag'):
                kwarg = kwarg[1:]
            # extract the kwarg operator if present
            op, operator = 'exact', OPERATORS['exact']
            if '__' in kwarg:
                kwarg, op = kwarg.rsplit('__', 1)
                if op not in OPERATORS:
                    raise BadRequest('Invalid filter operator: __%s' % op)
                operator = OPERATORS[op]
            # get value from elem and check ismissing operator
            value = elem.attrib.get(kwarg)
            log.debug("Checking %s.%s__%s=%s (value=%s)", elem.tag, kwarg, op,
                str(query)[:20], str(value)[:20])
            if op == 'ismissing':
                if query not in (True, False):
                    raise BadRequest('Value when using __ismissing must be in (True, False).')
                if (query is True and value) or (query is False and not value):
                    return False
            # special case query=None,0,'' to include missing attr
            if op == 'exact' and query in (None, 0, '') and value is None:
                return True
            # return if attr were looking for is missing
            if not value:
                return False
            # cast value to the same type as query
            if isinstance(query, int): value = int(value)
            if isinstance(query, float): value = float(value)
            if isinstance(query, bool): value = bool(int(value))
            # perform the comparison
            if not operator(value, query):
                return False
        return True

    def _loadData(self, data):
        raise NotImplementedError('Abstract method not implemented.')


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

    def __getattribute__(self, attr):
        # Dragons inside.. :-/
        value = utils.getattributeOrNone(PlexPartialObject, self, attr)
        # Check a few cases where we dont want to reload
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
        return utils.getattributeOrNone(PlexPartialObject, self, attr)

    def analyze(self):
        """ Tell Plex Media Server to performs analysis on it this item to gather
            information. Analysis includes:

            * Gather Media Properties: All of the media you add to a Library has
                properties that are useful to know–whether it's a video file, a
                music track, or one of your photos (container, codec, resolution, etc).
            * Generate Default Artwork: Artwork will automatically be grabbed from a
                video file. A background image will be pulled out as well as a
                smaller image to be used for poster/thumbnail type purposes.
            * Generate Video Preview Thumbnails: Video preview thumbnails are created,
                if you have that feature enabled. Video preview thumbnails allow
                graphical seeking in some Apps. It's also used in the Plex Web App Now
                Playing screen to show a graphical representation of where playback
                is. Video preview thumbnails creation is a CPU-intensive process akin
                to transcoding the file.
        """
        key = '/%s/analyze' % self.key.lstrip('/')
        self._server.query(key, method=self._server._session.put)

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

    def refresh(self):
        """ Refreshing a Library or individual item causes the metadata for the item to be
            refreshed, even if it already has metadata. You can think of refreshing as
            "update metadata for the requested item even if it already has some". You should
            refresh a Library or individual item if:

            * You've changed the Library Metadata Agent.
            * You've added "Local Media Assets" (such as artwork, theme music, external
                subtitle files, etc.)
            * You want to freshen the item posters, summary, etc.
            * There's a problem with the poster image that's been downloaded.
            * Items are missing posters or other downloaded information. This is possible if
                the refresh process is interrupted (the Server is turned off, internet
                connection dies, etc).
        """
        key = '%s/refresh' % self.key
        self._server.query(key, method=self._server._session.put)

    def section(self):
        """ Returns the :class:`~plexapi.library.LibrarySection` this item belongs to. """
        return self._server.library.sectionByID(self.librarySectionID)


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
        self.player = utils.findPlayer(self._server, data)
        self.transcodeSession = utils.findTranscodeSession(self._server, data)
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
        return self._server.url('/%s/:/transcode/universal/start.m3u8?%s' %
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
                download_url = self._server.url('%s?download=1' % location.key)
            filepath = utils.download(download_url, filename=filename,
                savepath=savepath, session=self._server._session)
            if filepath:
                filepaths.append(filepath)
        return filepaths
