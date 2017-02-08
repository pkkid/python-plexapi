# -*- coding: utf-8 -*-
import logging, os, requests
from datetime import datetime
from threading import Thread
from plexapi.compat import quote, string_type
from plexapi.exceptions import NotFound

# Search Types - Plex uses these to filter specific media types when searching.
# Library Types - Populated at runtime
SEARCHTYPES = {'movie': 1, 'show': 2, 'season': 3, 'episode': 4,
    'artist': 8, 'album': 9, 'track': 10, 'photo': 14}
LIBRARY_TYPES = {}


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


def register_libtype(cls):
    """ Registry of library types we may come across when parsing XML. This allows us to
        define a few helper functions to dynamically convery the XML into objects. See
        buildItem() below for an example.
    """
    LIBRARY_TYPES[cls.TYPE] = cls
    return cls


def cast(func, value):
    """ Cast the specified value to the specified type (returned by func). Currently this
        only support int, float, bool. Should be extended if needed.

        Parameters:
            func (func): Calback function to used cast to type (int, bool, float).
            value (any): value to be cast and returned.
    """
    if value is not None:
        if func == bool:
            return bool(int(value))
        elif func in (int, float):
            try:
                return func(value)
            except ValueError:
                return float('nan')
        return func(value)
    return value


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


def getattributeOrNone(obj, self, attr):
    try:
        return super(obj, self).__getattribute__(attr)
    except AttributeError:
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
    return {c.attrib['title']: c.attrib['key'] for c in server._query(path)}


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
    if value and value is not None:
        if format:
            value = datetime.strptime(value, format)
        else:
            value = datetime.fromtimestamp(int(value))
    return value


def toList(value, itemcast=None, delim=','):
    """ Returns a list of strings from the specified value.
        
        Parameters:
            value (str): comma delimited string to convert to list.
            itemcast (func): Function to cast each list item to (default str).
            delim (str): string delimiter (optional; default ',').
    """
    value = value or ''
    itemcast = itemcast or str
    return [itemcast(item) for item in value.split(delim) if item != '']


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
    # TODO: Review this; It should be properly logging and raising exceptions..
    from plexapi import log
    session = session or requests.Session()
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
            log.debug('Mocked download %s', fullpath)
            return fullpath
        with open(fullpath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunksize):
                if chunk:
                    f.write(chunk)
        #log.debug('Downloaded %s to %s from %s' % (filename, fullpath, url))
        return fullpath
    except Exception as err:  # pragma: no cover
        log.error('Error downloading file: %s' % err)
        raise
        #log.exception('Failed to download %s to %s %s' % (url, fullpath, e))
