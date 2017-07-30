# -*- coding: utf-8 -*-
import logging
import os
import re
import requests
import time
import zipfile
from sys import version_info
from datetime import datetime
from threading import Thread

from plexapi import compat
from plexapi.exceptions import NotFound

# Search Types - Plex uses these to filter specific media types when searching.
# Library Types - Populated at runtime
SEARCHTYPES = {'movie': 1, 'show': 2, 'season': 3, 'episode': 4,
               'artist': 8, 'album': 9, 'track': 10, 'photo': 14}
PLEXOBJECTS = {}


if version_info < (3,):
    str = unicode


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
            if isinstance(cleanargs[i], compat.string_type):
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
        arglist.append('%s=%s' % (key, compat.quote(value)))
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
        threads[-1].setDaemon(True)
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
            if part.indexes:  # always use bif images if available.
                url = '/library/parts/%s/indexes/%s/%s' % (part.id, part.indexes.lower(), media.viewOffset)
        if url:
            if filename is None:
                prettyname = media._prettyfilename()
                filename = 'session_transcode_%s_%s_%s' % (media.usernames[0], prettyname, int(time.time()))
            url = server.transcodeImage(url, height, width, opacity, saturation)
            filepath = download(url, filename=filename)
            info['username'] = {'filepath': filepath, 'url': url}
    return info


def download(url, filename=None, savepath=None, session=None, chunksize=4024, unpack=False, mocked=False):
    """ Helper to download a thumb, videofile or other media item. Returns the local
        path to the downloaded file.

       Parameters:
            url (str): URL where the content be reached.
            filename (str): Filename of the downloaded file, default None.
            savepath (str): Defaults to current working dir.
            chunksize (int): What chunksize read/write at the time.
            mocked (bool): Helper to do evertything except write the file.
            unpack (bool): Unpack the zip file.

        Example:
            >>> download(a_episode.getStreamURL(), a_episode.location)
            /path/to/file
    """
    from plexapi import log
    # fetch the data to be saved
    session = session or requests.Session()
    response = session.get(url, stream=True)
    # make sure the savepath directory exists
    savepath = savepath or os.getcwd()
    compat.makedirs(savepath, exist_ok=True)
    # try getting filename from header if not specified in arguments (used for logs, db)
    if not filename and response.headers.get('Content-Disposition'):
        filename = re.findall(r'filename=\"(.+)\"', response.headers.get('Content-Disposition'))
        filename = filename[0] if filename[0] else None
    filename = os.path.basename(filename)
    fullpath = os.path.join(savepath, filename)
    # append file.ext from content-type if not already there
    extension = os.path.splitext(fullpath)[-1]
    if not extension:
        contenttype = response.headers.get('content-type')
        if contenttype and 'image' in contenttype:
            fullpath += contenttype.split('/')[1]
    # check this is a mocked download (testing)
    if mocked:
        log.debug('Mocked download %s', fullpath)
        return fullpath
    # save the file to disk
    log.info('Downloading: %s', fullpath)
    with open(fullpath, 'wb') as handle:
        for chunk in response.iter_content(chunk_size=chunksize):
            handle.write(chunk)
    # check we want to unzip the contents
    if fullpath.endswith('zip') and unpack:
        with zipfile.ZipFile(fullpath, 'r') as handle:
            handle.extractall(savepath)
    # finished; return fillpath
    return fullpath


def tag_helper(tag, items, locked=True, remove=False):
    """Simple tag helper for editing a object."""
    if not isinstance(items, list):
        items = [items]

    d = {}
    if not remove:
        for i, item in enumerate(items):
            tag_name = '%s[%s].tag.tag' % (tag, i)
            d[tag_name] = item

    if remove:
        tag_name = '%s[].tag.tag-' % tag
        d[tag_name] = ','.join(items)

    d['%s.locked' % tag] = 1 if locked else 0

    return d
