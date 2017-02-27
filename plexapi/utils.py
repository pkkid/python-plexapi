# -*- coding: utf-8 -*-
import logging
import os
import re
import requests
import time
import zipfile
from datetime import datetime
from threading import Thread
from plexapi.compat import quote, string_type
from plexapi.exceptions import NotFound


# Search Types - Plex uses these to filter specific media types when searching.
# Library Types - Populated at runtime
SEARCHTYPES = {'movie': 1, 'show': 2, 'season': 3, 'episode': 4,
               'artist': 8, 'album': 9, 'track': 10, 'photo': 14}
PLEXOBJECTS = {}


class SecretsFilter(logging.Filter):
    """ Logging filter to hide secrets. """
    def __init__(self, secrets=None):
        self.secrets = secrets or set()

    def add_secret(self, secret):
        if secret is not None:
            self.secrets.add(secret)
        return secret

    def filter(self, record):
        cleanargs = list(record.args)
        for i in range(len(cleanargs)):
            if isinstance(cleanargs[i], string_type):
                for secret in self.secrets:
                    cleanargs[i] = cleanargs[i].replace(secret, '<hidden>')
        record.args = tuple(cleanargs)
        return True


def registerPlexObject(cls):
    """ Registry of library types we may come across when parsing XML. This allows us to
        define a few helper functions to dynamically convery the XML into objects. See
        buildItem() below for an example.
    """
    etype = getattr(cls, 'STREAMTYPE', cls.TYPE)
    ehash = '%s.%s' % (cls.TAG, etype) if etype else cls.TAG
    if ehash in PLEXOBJECTS:
        raise Exception('Ambiguous PlexObject definition %s(tag=%s, type=%s) with %s' %
            (cls.__name__, cls.TAG, etype, PLEXOBJECTS[ehash].__name__))
    PLEXOBJECTS[ehash] = cls
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


def getattributeOrNone(obj, self, attr):
    """ Returns result from __getattribute__ or None if not found. """
    try:
        return super(obj, self).__getattribute__(attr)
    except AttributeError:
        return None


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


def lowerFirst(s):
    return s[0].lower() + s[1:]


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
            libtype (str): LibType to lookup (movie, show, season, episode, artist, album, track)

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


def downloadSessionImages(server, filename=None, height=150, width=150, opacity=100, saturation=100):
    """ Helper to download a bif image or thumb.url from plex.server.sessions.

       Parameters:
           filename (str): default to None,
           height (int): Height of the image.
           width (int): width of the image.
           opacity (int): Opacity of the resulting image (possibly deprecated).
           saturation (int): Saturating of the resulting image.

       Returns:
            {'hellowlol': {'filepath': '<filepath>', 'url': 'http://<url>'},
            {'<username>': {filepath, url}}, ...
    """
    info = {}
    for media in server.sessions():
        url = None
        for part in media.iterParts():
            if media.thumb:
                url = media.thumb
            if part.indexes:  # Always use bif images if available.
                url = '/library/parts/%s/indexes/%s/%s' % (part.id, part.indexes.lower(), media.viewOffset)
        if url:
            if filename is None:
                prettyname = media._prettyfilename()
                filename = 'session_transcode_%s_%s_%s' % (media.usernames[0], prettyname, int(time.time()))
            url = server.transcodeImage(url, height=height, width=width, opacity=opacity, saturation=saturation)
            dfp = download(url, filename=filename)
            info['username'] = {'filepath': dfp, 'url': url}
    return info


def download(url, filename=None, savepath=None, session=None, chunksize=4024, mocked=False, unpack=False):
    """ Helper to download a thumb, videofile or other media item. Returns the local
        path to the downloaded file.

       Parameters:
            url (str): URL where the content be reached.
            filename (str): Filename of the downloaded file, default None.
            savepath (str): Defaults to current working dir.
            chunksize (int): What chunksize read/write at the time.
            mocked (bool): Helper to do evertything except write the file.
            unpack (bool): Unpack the zip file

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

    try:
        response = session.get(url, stream=True)

        # Lets grab the name if we dont supply one.
        # This will be used for downloading logs/db etc.
        if filename is None and response.headers.get('Content-Disposition'):
            filename = re.findall(ur'filename=\"(.+)\"', response.headers.get('Content-Disposition'))
            if filename:
                filename = filename[0]

        filename = os.path.basename(filename)
        fullpath = os.path.join(savepath, filename)

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

        if fullpath.endswith('zip') and unpack is True:
            with zipfile.ZipFile(fullpath, 'r') as zp:
                zp.extractall(savepath)

        # log.debug('Downloaded %s to %s from %s' % (filename, fullpath, url))
        return fullpath

    except Exception as err:  # pragma: no cover
        log.exception('Error downloading file: %s' % err)
        raise
        # log.exception('Failed to download %s to %s %s' % (url, fullpath, e))
