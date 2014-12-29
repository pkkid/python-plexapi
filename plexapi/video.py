"""
PlexVideo
"""
from plexapi.media import Media, Country, Director, Genre, Producer, Actor, Writer
from plexapi.exceptions import NotFound, UnknownType
from plexapi.utils import PlexPartialObject, NA
from plexapi.utils import cast, toDatetime


class Video(PlexPartialObject):
    TYPE = None

    def __eq__(self, other):
        return self.type == other.type and self.key == other.key

    def __repr__(self):
        title = self.title.replace(' ','.')[0:20]
        return '<%s:%s>' % (self.__class__.__name__, title.encode('utf8'))

    def _loadData(self, data):
        self.type = data.attrib.get('type', NA)
        self.key = data.attrib.get('key', NA)
        self.ratingKey = data.attrib.get('ratingKey', NA)
        self.title = data.attrib.get('title', NA)
        self.summary = data.attrib.get('summary', NA)
        self.art = data.attrib.get('art', NA)
        self.thumb = data.attrib.get('thumb', NA)
        self.addedAt = toDatetime(data.attrib.get('addedAt', NA))
        self.updatedAt = toDatetime(data.attrib.get('updatedAt', NA))
        self.lastViewedAt = toDatetime(data.attrib.get('lastViewedAt', NA))
        self.index = data.attrib.get('index', NA)
        self.parentIndex = data.attrib.get('parentIndex', NA)
        if self.isFullObject():
            # These are auto-populated when requested
            self.media = [Media(self.server, elem, self.initpath, self) for elem in data if elem.tag == Media.TYPE]
            self.countries = [Country(self.server, elem) for elem in data if elem.tag == Country.TYPE]
            self.directors = [Director(self.server, elem) for elem in data if elem.tag == Director.TYPE]
            self.genres = [Genre(self.server, elem) for elem in data if elem.tag == Genre.TYPE]
            self.producers = [Producer(self.server, elem) for elem in data if elem.tag == Producer.TYPE]
            self.actors = [Actor(self.server, elem) for elem in data if elem.tag == Actor.TYPE]
            self.writers = [Writer(self.server, elem) for elem in data if elem.tag == Writer.TYPE]

    def iter_parts(self):
        for media in self.media:
            for part in media.parts:
                yield part

    def analyze(self):
        self.server.query('/%s/analyze' % self.key)

    def markWatched(self):
        path = '/:/scrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self.server.query(path)
        self.reload()

    def markUnwatched(self):
        path = '/:/unscrobble?key=%s&identifier=com.plexapp.plugins.library' % self.ratingKey
        self.server.query(path)
        self.reload()

    def play(self, client):
        client.playMedia(self)

    def refresh(self):
        self.server.query('/%s/refresh' % self.key)


class Movie(Video):
    TYPE = 'movie'

    def _loadData(self, data):
        super(Movie, self)._loadData(data)
        self.studio = data.attrib.get('studio', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.rating = data.attrib.get('rating', NA)
        self.viewCount = cast(int, data.attrib.get('viewCount', 0))
        self.viewOffset = cast(int, data.attrib.get('viewOffset', 0))
        self.year = cast(int, data.attrib.get('year', NA))
        self.tagline = data.attrib.get('tagline', NA)
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.primaryExtraKey = data.attrib.get('primaryExtraKey', NA)


class Show(Video):
    TYPE = 'show'
        
    def _loadData(self, data):
        super(Show, self)._loadData(data)
        self.studio = data.attrib.get('studio', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.rating = data.attrib.get('rating', NA)
        self.year = cast(int, data.attrib.get('year', NA))
        self.banner = data.attrib.get('banner', NA)
        self.theme = data.attrib.get('theme', NA)
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')
        self.leafCount = cast(int, data.attrib.get('leafCount', NA))
        self.viewedLeafCount = cast(int, data.attrib.get('viewedLeafCount', NA))
        self.childCount = cast(int, data.attrib.get('childCount', NA))

    def seasons(self):
        path = '/library/metadata/%s/children' % self.ratingKey
        return list_items(self.server, path, Season.TYPE)

    def season(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return find_item(self.server, path, title)

    def episodes(self):
        leavesKey = '/library/metadata/%s/allLeaves' % self.ratingKey
        return list_items(self.server, leavesKey)

    def episode(self, title):
        path = '/library/metadata/%s/allLeaves' % self.ratingKey
        return find_item(self.server, path, title)

    def get(self, title):
        return self.episode(title)


class Season(Video):
    TYPE = 'season'

    def _loadData(self, data):
        super(Season, self)._loadData(data)
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.librarySectionTitle = data.attrib.get('librarySectionTitle', NA)
        self.parentRatingKey = data.attrib.get('parentRatingKey', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentTitle = data.attrib.get('parentTitle', NA)
        self.parentSummary = data.attrib.get('parentSummary', NA)
        self.index = data.attrib.get('index', NA)
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.parentTheme = data.attrib.get('parentTheme', NA)
        self.leafCount = cast(int, data.attrib.get('leafCount', NA))
        self.viewedLeafCount = cast(int, data.attrib.get('viewedLeafCount', NA))

    def episodes(self):
        childrenKey = '/library/metadata/%s/children' % self.ratingKey
        return list_items(self.server, childrenKey)

    def episode(self, title):
        path = '/library/metadata/%s/children' % self.ratingKey
        return find_item(self.server, path, title)

    def get(self, title):
        return self.episode(title)

    def show(self):
        return list_items(self.server, self.parentKey)[0]


class Episode(Video):
    TYPE = 'episode'

    def _loadData(self, data):
        super(Episode, self)._loadData(data)
        self.librarySectionID = data.attrib.get('librarySectionID', NA)
        self.librarySectionTitle = data.attrib.get('librarySectionTitle', NA)
        self.grandparentKey = data.attrib.get('grandparentKey', NA)
        self.grandparentTitle = data.attrib.get('grandparentTitle', NA)
        self.grandparentThumb = data.attrib.get('grandparentThumb', NA)
        self.parentKey = data.attrib.get('parentKey', NA)
        self.parentIndex = data.attrib.get('parentIndex', NA)
        self.parentThumb = data.attrib.get('parentThumb', NA)
        self.contentRating = data.attrib.get('contentRating', NA)
        self.index = data.attrib.get('index', NA)
        self.rating = data.attrib.get('rating', NA)
        self.viewCount = cast(int, data.attrib.get('viewCount', 0))
        self.viewOffset = cast(int, data.attrib.get('viewOffset', 0))
        self.year = cast(int, data.attrib.get('year', NA))
        self.duration = cast(int, data.attrib.get('duration', NA))
        self.originallyAvailableAt = toDatetime(data.attrib.get('originallyAvailableAt', NA), '%Y-%m-%d')

    def season(self):
        return list_items(self.server, self.parentKey)[0]

    def show(self):
        return list_items(self.server, self.grandparentKey)[0]


def build_item(server, elem, initpath):
    VIDEOCLS = {Movie.TYPE:Movie, Show.TYPE:Show, Season.TYPE:Season, Episode.TYPE:Episode}
    vtype = elem.attrib.get('type')
    if vtype in VIDEOCLS:
        cls = VIDEOCLS[vtype]
        return cls(server, elem, initpath)
    raise UnknownType('Unknown video type: %s' % vtype)


def find_item(server, path, title):
    for elem in server.query(path):
        if elem.attrib.get('title').lower() == title.lower():
            return build_item(server, elem, path)
    raise NotFound('Unable to find title: %s' % title)


def list_items(server, path, videotype=None):
    items = []
    for elem in server.query(path):
        if not videotype or elem.attrib.get('type') == videotype:
            try:
                items.append(build_item(server, elem, path))
            except UnknownType:
                pass
    return items


def search_type(videotype):
    if videotype == Movie.TYPE: return 1
    elif videotype == Show.TYPE: return 2
    elif videotype == Season.TYPE: return 3
    elif videotype == Episode.TYPE: return 4
    raise NotFound('Unknown videotype: %s' % videotype)
