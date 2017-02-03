# -*- coding: utf-8 -*-
import logging, os, re, requests
from datetime import datetime
from threading import Thread
from plexapi.compat import quote, string_type, urlencode
from plexapi.exceptions import NotFound, NotImplementedError, UnknownType, Unsupported

# Search Types - Plex uses these to filter specific media types when searching.
SEARCHTYPES = {'movie': 1, 'show': 2, 'season': 3, 'episode': 4,
    'artist': 8, 'album': 9, 'track': 10, 'photo': 14}
LIBRARY_TYPES = {}


def register_libtype(cls):
    """ Registry of library types we may come across when parsing XML. This allows us to
        define a few helper functions to dynamically convery the XML into objects. See
        buildItem() below for an example.
    """
    LIBRARY_TYPES[cls.TYPE] = cls
    return cls


class _NA(object):
    """ This used to be a simple variable equal to '__NA__'. There has been need to
        compare NA against None in some use cases. This object allows the internals
        of PlexAPI to distinguish between unfetched values and fetched, but non-existent
        values. (NA == None results to True; NA is None results to False)
    """

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, _NA) or other in [None, '__NA__']

    def __nonzero__(self):
        return False

    def __repr__(self):
        return '__NA__'

NA = _NA()  # Keep this for now.


class SecretsFilter(logging.Filter):
    """ Logging filter to hide secrets. """
    def __init__(self, secrets=None):
        self.secrets = secrets or set()

    def add_secret(self, secret):
        self.secrets.add(secret)

    def filter(self, record):
        cleanargs = list(record.args)
        for i in range(len(cleanargs)):
            if isinstance(cleanargs[i], string_type):
                for secret in self.secrets:
                    cleanargs[i] = cleanargs[i].replace(secret, '<hidden>')
        record.args = tuple(cleanargs)
        return True


class PlexPartialObject(object):
    """ Not all objects in the Plex listings return the complete list of elements
        for the object. This object will allow you to assume each object is complete,
        and if the specified value you request is None it will fetch the full object
        automatically and update itself.

        Attributes:
            data (ElementTree): Response from PlexServer used to build this object (optional).
            initpath (str): Relative path requested when retrieving specified `data` (optional).
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
    """
    def __init__(self, data, initpath, server=None):
        self.server = server
        self.initpath = initpath
        self._loadData(data)
        self._reloaded = False

    def __eq__(self, other):
        return other is not None and self.key == other.key

    def __repr__(self):
        clsname = self.__class__.__name__
        key = self.key.replace('/library/metadata/', '') if self.key else 'NA'
        title = self.title.replace(' ', '.')[0:20].encode('utf8')
        return '<%s:%s:%s>' % (clsname, key, title)

    def __getattr__(self, attr):
        # Auto reload self, from the full key (path) when needed.
        if attr == 'key' or self.__dict__.get(attr) or self.isFullObject():
            return self.__dict__.get(attr, NA)
        print('reload because of %s' % attr)
        self.reload()
        return self.__dict__.get(attr, NA)

    def __setattr__(self, attr, value):
        if value != NA or self.isFullObject():
            self.__dict__[attr] = value

    def _loadData(self, data):
        raise NotImplementedError('Abstract method not implemented.')

    def isFullObject(self):
        """ Retruns True if this is already a full object. A full object means all attributes
            were populated from the api path representing only this item. For example, the
            search result for a movie often only contain a portion of the attributes a full
            object (main url) for that movie contain.
        """
        return not self.key or self.key == self.initpath

    def isPartialObject(self):
        """ Returns True if this is NOT a full object. """
        return not self.isFullObject()

    def reload(self):
        """ Reload the data for this object from PlexServer XML. """
        data = self.server.query(self.key)
        self.initpath = self.key
        self._loadData(data[0])
        self._reloaded = True
        return self


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
        self.sessionKey = cast(int, data.attrib.get('sessionKey', NA))
        self.username = findUsername(data)
        self.player = findPlayer(self.server, data)
        self.transcodeSession = findTranscodeSession(self.server, data)
        # Load data for history details (/status/sessions/history/all)
        self.viewedAt = toDatetime(data.attrib.get('viewedAt', NA))
        # Load data for playlist items
        self.playlistItemID = cast(int, data.attrib.get('playlistItemID', NA))

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
        return self.server.url('/%s/:/transcode/universal/start.m3u8?%s' % (streamtype, urlencode(sorted_params)))

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
                download_url = self.server.url('%s?download=1' % location.key)
            filepath = download(download_url, filename=filename, savepath=savepath,
                session=self.server.session)
            if filepath:
                filepaths.append(filepath)
        return filepaths


def buildItem(server, elem, initpath, bytag=False):
    """ Factory function to build the objects used within the PlexAPI.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            elem (ElementTree): XML data needed to build the object.
            initpath (str): Relative path requested when retrieving specified `data` (optional).
            bytag (bool): Creates the object from the name specified by the tag instead of the
                default which builds the object specified by the type attribute. <tag type='foo' />

        Raises:
            UnknownType: Unknown library type.
    """
    libtype = elem.tag if bytag else elem.attrib.get('type')
    if libtype == 'photo' and elem.tag == 'Directory':
        libtype = 'photoalbum'
    if libtype in LIBRARY_TYPES:
        cls = LIBRARY_TYPES[libtype]
        return cls(server, elem, initpath)
    raise UnknownType('Unknown library type: %s' % libtype)


def cast(func, value):
    """ Cast the specified value to the specified type (returned by func). Currently this
        only support int, float, bool. Should be extended if needed.

        Parameters:
            func (func): Calback function to used cast to type (int, bool, float).
            value (any): value to be cast and returned.
    """
    if value not in (None, NA):
        if func == bool:
            return bool(int(value))
        elif func in (int, float):
            try:
                return func(value)
            except ValueError:
                return float('nan')
        return func(value)
    return value


def findKey(server, key):
    """ Finds and builds a object based on ratingKey.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            key (int): ratingKey to find and return.

        Raises:
            NotFound: Unable to find key
    """
    path = '/library/metadata/{0}'.format(key)
    try:
        # Item seems to be the first sub element
        elem = server.query(path)[0]
        return buildItem(server, elem, path)
    except:
        raise NotFound('Unable to find key: %s' % key)


def findItem(server, path, title):
    """ Finds and builds a object based on title.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            path (str): API path that returns item to search title for.
            title (str): Title of the item to find and return.

        Raises:
            NotFound: Unable to find item.
    """
    for elem in server.query(path):
        if elem.attrib.get('title').lower() == title.lower():
            return buildItem(server, elem, path)
    raise NotFound('Unable to find item: %s' % title)


def findLocations(data, single=False):
    """ Returns a list of filepaths from a location tag.

        Parameters:
            data (ElementTree): XML object to search for locations in.
            single (bool): Set True to only return the first location found.
                Return type will be a string if this is set to True.
    """
    locations = []
    for elem in data:
        if elem.tag == 'Location':
            locations.append(elem.attrib.get('path'))
    if single:
        return locations[0] if locations else None
    return locations


def findPlayer(server, data):
    """ Returns the :class:`~plexapi.client.PlexClient` object found in the specified data.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            data (ElementTree): XML data to find Player in.
    """
    elem = data.find('Player')
    if elem is not None:
        from plexapi.client import PlexClient
        baseurl = 'http://%s:%s' % (elem.attrib.get('address'), elem.attrib.get('port'))
        return PlexClient(baseurl, server=server, data=elem)
    return None


def findStreams(media, streamtype):
    """ Returns a list of streams (str) found in media that match the specified streamtype.

        Parameters:
            media (:class:`~plexapi.utils.Playable`): Item to search for streams (show, movie, episode).
            streamtype (str): Streamtype to return (videostream, audiostream, subtitlestream).
    """
    streams = []
    for mediaitem in media:
        for part in mediaitem.parts:
            for stream in part.streams:
                if stream.TYPE == streamtype:
                    streams.append(stream)
    return streams


def findTranscodeSession(server, data):
    """ Returns a :class:`~plexapi.media.TranscodeSession` object if found within the specified
        XML data.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            data (ElementTree): XML data to find TranscodeSession in.
    """

    elem = data.find('TranscodeSession')
    if elem is not None:
        from plexapi import media
        return media.TranscodeSession(server, elem)
    return None


def findUsername(data):
    """ Returns the username if found in the specified XML data. Returns None if not found.

        Parameters:
            data (ElementTree): XML data to find username in.
    """
    elem = data.find('User')
    if elem is not None:
        return elem.attrib.get('title')
    return None


def isInt(str):
    """ Returns True if the specified string passes as an int. """
    try:
        int(str)
        return True
    except ValueError:
        return False


def joinArgs(args):
    """ Returns a query string (uses for HTTP URLs) where only the value is URL encoded.
        Example return value: '?genre=action&type=1337'.

        Parameters:
            args (dict): Arguments to include in query string.
    """
    if not args:
        return ''
    arglist = []
    for key in sorted(args, key=lambda x: x.lower()):
        value = str(args[key])
        arglist.append('%s=%s' % (key, quote(value)))
    return '?%s' % '&'.join(arglist)


def listChoices(server, path):
    """ Returns a dict of {title:key} for all simple choices in a search filter.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            path (str): Relative path to request XML data from.
    """
    return {c.attrib['title']: c.attrib['key'] for c in server.query(path)}


def listItems(server, path, libtype=None, watched=None, bytag=False):
    """ Returns a list of object built from :func:`~plexapi.utils.buildItem()` found
        within the specified path.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            path (str): Relative path to request XML data from.
            libtype (str): Optionally return only the specified library type.
            watched (bool): Optionally return only watched or unwatched items.
            bytag (bool): Set true if libtype is found in the XML tag (and not the 'type' attribute).
    """
    items = []
    for elem in server.query(path):
        if libtype and elem.attrib.get('type') != libtype:
            continue
        if watched is True and int(elem.attrib.get('viewCount', 0)) == 0:
            continue
        if watched is False and int(elem.attrib.get('viewCount', 0)) >= 1:
            continue
        try:
            items.append(buildItem(server, elem, path, bytag))
        except UnknownType:
            pass
    return items


def rget(obj, attrstr, default=None, delim='.'):  # pragma: no cover
    """ Returns the value at the specified attrstr location within a nexted tree of
        dicts, lists, tuples, functions, classes, etc. The lookup is done recursivley
        for each key in attrstr (split by by the delimiter) This function is heavily
        influenced by the lookups used in Django templates.

        Parameters:
            obj (any): Object to start the lookup in (dict, obj, list, tuple, etc).
            attrstr (str): String to lookup (ex: 'foo.bar.baz.value')
            default (any): Default value to return if not found.
            delim (str): Delimiter separating keys in attrstr.
    """
    try:
        parts = attrstr.split(delim, 1)
        attr = parts[0]
        attrstr = parts[1] if len(parts) == 2 else None
        if isinstance(obj, dict):
            value = obj[attr]
        elif isinstance(obj, list):
            value = obj[int(attr)]
        elif isinstance(obj, tuple):
            value = obj[int(attr)]
        elif isinstance(obj, object):
            value = getattr(obj, attr)
        if attrstr:
            return rget(value, attrstr, default, delim)
        return value
    except:
        return default


def searchType(libtype):
    """ Returns the integer value of the library string type.

        Parameters:
            libtype (str): Library type to lookup (movie, show, season, episode,
                artist, album, track)

        Raises:
            NotFound: Unknown libtype
    """
    libtype = str(libtype)
    if libtype in [str(v) for v in SEARCHTYPES.values()]:
        return libtype
    if SEARCHTYPES.get(libtype) is not None:
        return SEARCHTYPES[libtype]
    raise NotFound('Unknown libtype: %s' % libtype)


def threaded(callback, listargs):
    """ Returns the result of <callback> for each set of \*args in listargs. Each call
        to <callback. is called concurrently in their own separate threads.

        Parameters:
            callback (func): Callback function to apply to each set of \*args.
            listargs (list): List of lists; \*args to pass each thread.
    """
    threads, results = [], []
    for args in listargs:
        args += [results, len(results)]
        results.append(None)
        threads.append(Thread(target=callback, args=args))
        threads[-1].start()
    for thread in threads:
        thread.join()

    return results


def toDatetime(value, format=None):
    """ Returns a datetime object from the specified value.

        Parameters:
            value (str): value to return as a datetime
            format (str): Format to pass strftime (optional; if value is a str).
    """
    if value and value != NA:
        if format:
            value = datetime.strptime(value, format)
        else:
            value = datetime.fromtimestamp(int(value))
    return value


def download(url, filename=None, savepath=None, session=None, chunksize=4024, mocked=False):
    """ Helper to download a thumb, videofile or other media item. Returns the local
        path to the downloaded file.

       Parameters:
            url (str): URL where the content be reached.
            filename (str): Filename of the downloaded file, default None.
            savepath (str): Defaults to current working dir.
            chunksize (int): What chunksize read/write at the time.
            mocked (bool): Helper to do evertything except write the file.

        Example:
            >>> download(a_episode.getStreamURL(), a_episode.location)
            /path/to/file
    """
    session = session or requests.Session()
    print('Mocked download %s' % mocked)
    if savepath is None:
        savepath = os.getcwd()
    else:
        # Make sure the user supplied path exists
        try:
            os.makedirs(savepath)
        except OSError:
            if not os.path.isdir(savepath):  # pragma: no cover
                raise
    filename = os.path.basename(filename)
    fullpath = os.path.join(savepath, filename)
    try:
        response = session.get(url, stream=True)
        # images dont have a extention so we try
        # to guess it from content-type
        ext = os.path.splitext(fullpath)[-1]
        if ext:
            ext = ''
        else:
            cp = response.headers.get('content-type')
            if cp:
                if 'image' in cp:
                    ext = '.%s' % cp.split('/')[1]
        fullpath = '%s%s' % (fullpath, ext)
        if mocked:
            return fullpath
        with open(fullpath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunksize):
                if chunk:
                    f.write(chunk)
        #log.debug('Downloaded %s to %s from %s' % (filename, fullpath, url))
        return fullpath
    except Exception as err:  # pragma: no cover
        print('Error downloading file: %s' % err)
        #log.exception('Failed to download %s to %s %s' % (url, fullpath, e))
