# -*- coding: utf-8 -*-
import re
from plexapi import log, utils
from plexapi.compat import urlencode
from plexapi.exceptions import BadRequest, NotFound, UnknownType, Unsupported

OPERATORS = {
    'exact': lambda v, q: v == q,
    'iexact': lambda v, q: v.lower() == q.lower(),
    'contains': lambda v, q: q in v,
    'icontains': lambda v, q: q.lower() in v.lower(),
    'in': lambda v, q: v in q,
    'gt': lambda v, q: v > q,
    'gte': lambda v, q: v >= q,
    'lt': lambda v, q: v < q,
    'lte': lambda v, q: v <= q,
    'startswith': lambda v, q: v.startswith(q),
    'istartswith': lambda v, q: v.lower().startswith(q),
    'endswith': lambda v, q: v.endswith(q),
    'iendswith': lambda v, q: v.lower().endswith(q),
    'exists': lambda v, q: v is not None if q else v is None,
    'regex': lambda v, q: re.match(q, v),
    'iregex': lambda v, q: re.match(q, v, flags=re.IGNORECASE),
}


class PlexObject(object):
    """ Base class for all Plex objects.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).
    """
    TAG = None      # xml element tag
    TYPE = None     # xml element type
    key = None      # plex relative url

    def __init__(self, server, data, initpath=None):
        self._server = server
        self._data = data
        self._initpath = initpath or self.key
        if data is not None:
            self._loadData(data)

    def __repr__(self):
        return '<%s>' % ':'.join([p for p in [
            self.__class__.__name__,
            utils.firstAttr(self, '_baseurl', 'key', 'id', 'playQueueID', 'uri'),
            utils.firstAttr(self, 'title', 'name', 'username', 'product', 'tag')
        ] if p])

    def __setattr__(self, attr, value):
        # dont overwrite an attr with None unless its a private variable
        if value is not None or attr.startswith('_') or attr not in self.__dict__:
            self.__dict__[attr] = value

    def _buildItem(self, elem, cls=None, initpath=None):
        """ Factory function to build objects based on registered PLEXOBJECTS. """
        # cls is specified, build the object and return
        initpath = initpath or self._initpath
        if cls is not None:
            return cls(self._server, elem, initpath)
        # cls is not specified, try looking it up in PLEXOBJECTS
        etype = elem.attrib.get('type', elem.attrib.get('streamType'))
        ehash = '%s.%s' % (elem.tag, etype) if etype else elem.tag
        ecls = utils.PLEXOBJECTS.get(ehash, utils.PLEXOBJECTS.get(elem.tag))
        #log.debug('Building %s as %s', elem.tag, ecls.__name__)
        if ecls is not None:
            return ecls(self._server, elem, initpath)
        raise UnknownType("Unknown library type <%s type='%s'../>" % (elem.tag, etype))

    def _buildItemOrNone(self, elem, cls=None, initpath=None):
        """ Calls :func:`~plexapi.base.PlexObject._buildItem()` but returns
            None if elem is an unknown type.
        """
        try:
            return self._buildItem(elem, cls, initpath)
        except UnknownType:
            return None

    def fetchItem(self, ekey, cls=None, **kwargs):
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
                    with the best guess PlexObjects based on tag and type attrs.
                etag (str): Only fetch items with the specified tag.
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

                    * __contains: Value contains specified arg.
                    * __endswith: Value ends with specified arg.
                    * __exact: Value matches specified arg.
                    * __exists (bool): Value is or is not present in the attrs.
                    * __gt: Value is greater than specified arg.
                    * __gte: Value is greater than or equal to specified arg.
                    * __icontains: Case insensative value contains specified arg.
                    * __iendswith: Case insensative value ends with specified arg.
                    * __iexact: Case insensative value matches specified arg.
                    * __in: Value is in a specified list or tuple.
                    * __iregex: Case insensative value matches the specified regular expression.
                    * __istartswith: Case insensative value starts with specified arg.
                    * __lt: Value is less than specified arg.
                    * __lte: Value is less than or equal to specified arg.
                    * __regex: Value matches the specified regular expression.
                    * __startswith: Value starts with specified arg.
        """
        if isinstance(ekey, int):
            ekey = '/library/metadata/%s' % ekey
        for elem in self._server.query(ekey):
            if self._checkAttrs(elem, **kwargs):
                return self._buildItem(elem, cls, ekey)
        clsname = cls.__name__ if cls else 'None'
        raise NotFound('Unable to find elem: cls=%s, attrs=%s' % (clsname, kwargs))

    def fetchItems(self, ekey, cls=None, **kwargs):
        """ Load the specified key to find and build all items with the specified tag
            and attrs. See :func:`~plexapi.base.PlexObject.fetchItem` for more details
            on how this is used.
        """
        data = self._server.query(ekey)
        return self.findItems(data, cls, ekey, **kwargs)

    def findItems(self, data, cls=None, initpath=None, **kwargs):
        """ Load the specified data to find and build all items with the specified tag
            and attrs. See :func:`~plexapi.base.PlexObject.fetchItem` for more details
            on how this is used.
        """
        # filter on cls attrs if specified
        if cls and cls.TAG and 'tag' not in kwargs:
            kwargs['etag'] = cls.TAG
        if cls and cls.TYPE and 'type' not in kwargs:
            kwargs['type'] = cls.TYPE
        # loop through all data elements to find matches
        items = []
        for elem in data:
            if self._checkAttrs(elem, **kwargs):
                item = self._buildItemOrNone(elem, cls, initpath)
                if item is not None:
                    items.append(item)
        return items

    def listAttrs(self, data, attr, **kwargs):
        results = []
        for elem in data:
            kwargs['%s__exists' % attr] = True
            if self._checkAttrs(elem, **kwargs):
                results.append(elem.attrib.get(attr))
        return results

    def reload(self):
        """ Reload the data for this object from self.key. """
        if not self.key:
            raise Unsupported('Cannot reload an object not built from a URL.')
        self._initpath = self.key
        data = self._server.query(self.key)
        self._loadData(data[0])
        return self

    def _checkAttrs(self, elem, **kwargs):
        attrsFound = {}
        for attr, query in kwargs.items():
            attr, op, operator = self._getAttrOperator(attr)
            values = self._getAttrValue(elem, attr)
            # special case query in (None, 0, '') to include missing attr
            if op == 'exact' and not values and query in (None, 0, ''):
                return True
            # return if attr were looking for is missing
            attrsFound[attr] = False
            for value in values:
                value = self._castAttrValue(op, query, value)
                if operator(value, query):
                    attrsFound[attr] = True
                    break
        #log.debug('Checking %s for %s found: %s', elem.tag, kwargs, attrsFound)
        return all(attrsFound.values())

    def _getAttrOperator(self, attr):
        for op, operator in OPERATORS.items():
            if attr.endswith('__%s' % op):
                attr = attr.rsplit('__', 1)[0]
                return attr, op, operator
        # default to exact match
        return attr, 'exact', OPERATORS['exact']

    def _getAttrValue(self, elem, attrstr, results=None):
        #log.debug('Fetching %s in %s', attrstr, elem.tag)
        parts = attrstr.split('__', 1)
        attr = parts[0]
        attrstr = parts[1] if len(parts) == 2 else None
        if attrstr:
            results = [] if results is None else results
            for child in [c for c in elem if c.tag.lower() == attr.lower()]:
                results += self._getAttrValue(child, attrstr, results)
            return [r for r in results if r is not None]
        # check were looking for the tag
        if attr.lower() == 'etag':
            return [elem.tag]
        # loop through attrs so we can perform case-insensative match
        for _attr, value in elem.attrib.items():
            if attr.lower() == _attr.lower():
                return [value]
        return []

    def _castAttrValue(self, op, query, value):
        if op == 'exists':
            return value
        if isinstance(query, bool):
            return bool(int(value))
        if isinstance(query, int) and '.' in value:
            return float(value)
        if isinstance(query, int):
            return int(value)
        if isinstance(query, float):
            return float(value)
        return value

    def _loadData(self, data):
        raise NotImplementedError('Abstract method not implemented.')

    def delete(self):
        try:
            return self._server.query(self.key, method=self._server._session.delete)
        except BadRequest:
            log.error('Failed to delete %s. This could be because you havnt allowed '
                      'items to be deleted' % self.key)
            raise


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

    def delete(self):
        """Delete a media elemeent. This has to be enabled under settings > server > library in plex webui."""
        try:
            return self._server.query(self.key, method=self._server._session.delete)
        except BadRequest:  # pragma: no cover
            log.error('Failed to delete %s. This could be because you havnt allowed '
                      'items to be deleted' % self.key)
            raise


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
        self.sessionKey = utils.cast(int, data.attrib.get('sessionKey'))            # session
        self.usernames = self.listAttrs(data, 'title', etag='User')                 # session
        self.players = self.findItems(data, etag='Player')                          # session
        self.transcodeSessions = self.findItems(data, etag='TranscodeSession')      # session
        self.viewedAt = utils.toDatetime(data.attrib.get('viewedAt'))               # history
        self.playlistItemID = utils.cast(int, data.attrib.get('playlistItemID'))    # playlist

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
