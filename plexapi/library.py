# -*- coding: utf-8 -*-
"""
PlexLibrary
"""
from plexapi import log, utils
from plexapi import X_PLEX_CONTAINER_SIZE
from plexapi.media import MediaTag
from plexapi.exceptions import BadRequest, NotFound


class Library(object):

    def __init__(self, server, data):
        self.identifier = data.attrib.get('identifier')
        self.mediaTagVersion = data.attrib.get('mediaTagVersion')
        self.server = server
        self.title1 = data.attrib.get('title1')
        self.title2 = data.attrib.get('title2')
        self._sectionsByID = {}  # cached section UUIDs

    def __repr__(self):
        return '<Library:%s>' % self.title1.encode('utf8')

    def sections(self):
        items = []
        SECTION_TYPES = {
            MovieSection.TYPE: MovieSection,
            ShowSection.TYPE: ShowSection,
            MusicSection.TYPE: MusicSection,
            PhotoSection.TYPE: PhotoSection,
        }
        path = '/library/sections'
        for elem in self.server.query(path):
            stype = elem.attrib['type']
            if stype in SECTION_TYPES:
                cls = SECTION_TYPES[stype]
                section = cls(self.server, elem, path)
                self._sectionsByID[section.key] = section
                items.append(section)
        return items

    def section(self, title=None):
        for item in self.sections():
            if item.title == title:
                return item
        raise NotFound('Invalid library section: %s' % title)
        
    def sectionByID(self, sectionID):
        if not self._sectionsByID:
            self.sections()
        return self._sectionsByID[sectionID]

    def all(self):
        return utils.listItems(self.server, '/library/all')

    def onDeck(self):
        return utils.listItems(self.server, '/library/onDeck')

    def recentlyAdded(self):
        return utils.listItems(self.server, '/library/recentlyAdded')

    def get(self, title):
        return utils.findItem(self.server, '/library/all', title)

    def getByKey(self, key):
        return utils.findKey(self.server, key)
        
    def search(self, title=None, libtype=None, **kwargs):
        """ Searching within a library section is much more powerful. It seems certain attributes on the media
            objects can be targeted to filter this search down a bit, but I havent found the documentation for
            it. For example: "studio=Comedy%20Central" or "year=1999" "title=Kung Fu" all work. Other items
            such as actor=<id> seem to work, but require you already know the id of the actor.
            TLDR: This is untested but seems to work. Use library section search when you can.
        """
        args = {}
        if title: args['title'] = title
        if libtype: args['type'] = utils.searchType(libtype)
        for attr, value in kwargs.items():
            args[attr] = value
        query = '/library/all%s' % utils.joinArgs(args)
        return utils.listItems(self.server, query)
    
    def cleanBundles(self):
        self.server.query('/library/clean/bundles')

    def emptyTrash(self):
        for section in self.sections():
            section.emptyTrash()

    def optimize(self):
        self.server.query('/library/optimize')

    def refresh(self):
        self.server.query('/library/sections/all/refresh')


class LibrarySection(object):
    ALLOWED_FILTERS = ()
    ALLOWED_SORT = ()
    BOOLEAN_FILTERS = ('unwatched', 'duplicate')

    def __init__(self, server, data, initpath):
        self.server = server
        self.initpath = initpath
        self.agent = data.attrib.get('agent')
        self.allowSync = utils.cast(bool, data.attrib.get('allowSync'))
        self.art = data.attrib.get('art')
        self.composite = data.attrib.get('composite')
        self.createdAt = utils.toDatetime(data.attrib.get('createdAt'))
        self.filters = data.attrib.get('filters')
        self.key = data.attrib.get('key')
        self.language = data.attrib.get('language')
        self.language = data.attrib.get('language')
        self.locations = utils.findLocations(data)
        self.refreshing = utils.cast(bool, data.attrib.get('refreshing'))
        self.scanner = data.attrib.get('scanner')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.type = data.attrib.get('type')
        self.updatedAt = utils.toDatetime(data.attrib.get('updatedAt'))
        self.uuid = data.attrib.get('uuid')

    def __repr__(self):
        title = self.title.replace(' ','.')[0:20]
        return '<%s:%s>' % (self.__class__.__name__, title.encode('utf8'))
    
    def get(self, title):
        path = '/library/sections/%s/all' % self.key
        return utils.findItem(self.server, path, title)

    def all(self):
        return utils.listItems(self.server, '/library/sections/%s/all' % self.key)
        
    def onDeck(self):
        return utils.listItems(self.server, '/library/sections/%s/onDeck' % self.key)

    def recentlyAdded(self, maxresults=50):
        return self.search(sort='addedAt:desc', maxresults=maxresults)
        
    def analyze(self):
        self.server.query('/library/sections/%s/analyze' % self.key)

    def emptyTrash(self):
        self.server.query('/library/sections/%s/emptyTrash' % self.key)

    def refresh(self):
        self.server.query('/library/sections/%s/refresh' % self.key)
        
    def listChoices(self, category, libtype=None, **kwargs):
        """ List choices for the specified filter category. kwargs can be any of the same
            kwargs in self.search() to help narrow down the choices to only those that
            matter in your current context.
        """
        if category in kwargs:
            raise BadRequest('Cannot include kwarg equal to specified category: %s' % category)
        args = {}
        for subcategory, value in kwargs.items():
            args[category] = self._cleanSearchFilter(subcategory, value)
        if libtype is not None: args['type'] = utils.searchType(libtype)
        query = '/library/sections/%s/%s%s' % (self.key, category, utils.joinArgs(args))
        return utils.listItems(self.server, query, bytag=True)

    def search(self, title=None, sort=None, maxresults=999999, libtype=None, **kwargs):
        """ Search the library. If there are many results, they will be fetched from the server
            in batches of X_PLEX_CONTAINER_SIZE amounts. If you're only looking for the first <num>
            results, it would be wise to set the maxresults option to that amount so this functions
            doesn't iterate over all results on the server.
            title: General string query to search for.
            sort: column:dir; column can be any of {addedAt, originallyAvailableAt, lastViewedAt,
              titleSort, rating, mediaHeight, duration}. dir can be asc or desc.
            maxresults: Only return the specified number of results
            libtype: Filter results to a spcifiec libtype {movie, show, episode, artist, album, track}
            kwargs: Any of the available filters for the current library section. Partial string
              matches allowed. Multiple matches OR together. All inputs will be compared with the
              available options and a warning logged if the option does not appear valid.
                'unwatched': Display or hide unwatched content (True, False). [all]
                'duplicate': Display or hide duplicate items (True, False). [movie]
                'actor': List of actors to search ([actor_or_id, ...]). [movie]
                'collection': List of collections to search within ([collection_or_id, ...]). [all]
                'contentRating': List of content ratings to search within ([rating_or_key, ...]). [movie,tv]
                'country': List of countries to search within ([country_or_key, ...]). [movie,music]
                'decade': List of decades to search within ([yyy0, ...]). [movie]
                'director': List of directors to search ([director_or_id, ...]). [movie]
                'genre': List Genres to search within ([genere_or_id, ...]). [all]
                'network': List of TV networks to search within ([resolution_or_key, ...]). [tv]
                'resolution': List of video resolutions to search within ([resolution_or_key, ...]). [movie]
                'studio': List of studios to search within ([studio_or_key, ...]). [music]
                'year': List of years to search within ([yyyy, ...]). [all]
        """
        # Cleanup the core arguments
        args = {}
        for category, value in kwargs.items():
            args[category] = self._cleanSearchFilter(category, value, libtype)
        if title is not None: args['title'] = title
        if sort is not None: args['sort'] = self._cleanSearchSort(sort)
        if libtype is not None: args['type'] = utils.searchType(libtype)
        # Iterate over the results
        results, subresults = [], '_init'
        args['X-Plex-Container-Start'] = 0
        args['X-Plex-Container-Size'] = min(X_PLEX_CONTAINER_SIZE, maxresults)
        while subresults and maxresults > len(results):
            query = '/library/sections/%s/all%s' % (self.key, utils.joinArgs(args))
            subresults = utils.listItems(self.server, query)
            results += subresults[:maxresults-len(results)]
            args['X-Plex-Container-Start'] += args['X-Plex-Container-Size']
        return results

    def _cleanSearchFilter(self, category, value, libtype=None):
        # check a few things before we begin
        if category not in self.ALLOWED_FILTERS:
            raise BadRequest('Unknown filter category: %s' % category)
        if category in self.BOOLEAN_FILTERS:
            return '1' if value else '0'
        if not isinstance(value, (list, tuple)):
            value = [value]
        # convert list of values to list of keys or ids
        result = set()
        choices = self.listChoices(category, libtype)
        lookup = {c.title.lower():c.key for c in choices}
        allowed = set(c.key for c in choices)
        for item in value:
            item = str(item.id if isinstance(item, MediaTag) else item).lower()
            # find most logical choice(s) to use in url
            if item in allowed: result.add(item); continue
            if item in lookup: result.add(lookup[item]); continue
            matches = [k for t,k in lookup.items() if item in t]
            if matches: map(result.add, matches); continue
            # nothing matched; use raw item value
            log.warning('Filter value not listed, using raw item value: %s' % item)
            result.add(item)
        return ','.join(result)
                
    def _cleanSearchSort(self, sort):
        sort = '%s:asc' % sort if ':' not in sort else sort
        scol, sdir = sort.lower().split(':')
        lookup = {s.lower():s for s in self.ALLOWED_SORT}
        if scol not in lookup:
            raise BadRequest('Unknown sort column: %s' % scol)
        if sdir not in ('asc', 'desc'):
            raise BadRequest('Unknown sort dir: %s' % sdir)
        return '%s:%s' % (lookup[scol], sdir)


class MovieSection(LibrarySection):
    ALLOWED_FILTERS = ('unwatched', 'duplicate', 'year', 'decade', 'genre', 'contentRating', 'collection',
        'director', 'actor', 'country', 'studio', 'resolution')
    ALLOWED_SORT = ('addedAt', 'originallyAvailableAt', 'lastViewedAt', 'titleSort', 'rating',
        'mediaHeight', 'duration')
    TYPE = 'movie'


class ShowSection(LibrarySection):
    ALLOWED_FILTERS = ('unwatched', 'year', 'genre', 'contentRating', 'network', 'collection')
    ALLOWED_SORT = ('addedAt', 'lastViewedAt', 'originallyAvailableAt', 'titleSort', 'rating', 'unwatched')
    TYPE = 'show'

    def searchShows(self, **kwargs):
        return self.search(libtype='show', **kwargs)

    def searchEpisodes(self, **kwargs):
        return self.search(libtype='episode', **kwargs)

    def recentlyAdded(self, libtype='episode', maxresults=50):
        return self.search(sort='addedAt:desc', libtype=libtype, maxresults=maxresults)


class MusicSection(LibrarySection):
    ALLOWED_FILTERS = ('genre', 'country', 'collection')
    ALLOWED_SORT = ('addedAt', 'lastViewedAt', 'viewCount', 'titleSort')
    TYPE = 'artist'
    
    def albums(self):
        return utils.listItems(self.server, '/library/sections/%s/albums' % self.key)

    def searchArtists(self, **kwargs):
        return self.search(libtype='artist', **kwargs)

    def searchAlbums(self, **kwargs):
        return self.search(libtype='album', **kwargs)
        
    def searchTracks(self, **kwargs):
        return self.search(libtype='track', **kwargs)


class PhotoSection(LibrarySection):
    ALLOWED_FILTERS = ()
    ALLOWED_SORT = ()
    TYPE = 'photo'
    
    def searchAlbums(self, **kwargs):
        return self.search(libtype='photo', **kwargs)
        
    def searchPhotos(self, **kwargs):
        return self.search(libtype='photo', **kwargs)


@utils.register_libtype
class FilterChoice(object):
    TYPE = 'Directory'

    def __init__(self, server, data, initpath):
        self.server = server
        self.initpath = initpath
        self.fastKey = data.attrib.get('fastKey')
        self.key = data.attrib.get('key')
        self.thumb = data.attrib.get('thumb')
        self.title = data.attrib.get('title')
        self.type = data.attrib.get('type')

    def __repr__(self):
        title = self.title.replace(' ','.')[0:20]
        return '<%s:%s:%s>' % (self.__class__.__name__, self.key, title)
