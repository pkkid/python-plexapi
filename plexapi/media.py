# -*- coding: utf-8 -*-
"""
PlexAPI Media
"""
from plexapi.utils import cast


class Media(object):
    TYPE = 'Media'

    def __init__(self, server, data, initpath, video):
        self.server = server
        self.initpath = initpath
        self.video = video
        self.videoResolution = data.attrib.get('videoResolution')
        self.id = cast(int, data.attrib.get('id'))
        self.duration = cast(int, data.attrib.get('duration'))
        self.bitrate = cast(int, data.attrib.get('bitrate'))
        self.width = cast(int, data.attrib.get('width'))
        self.height = cast(int, data.attrib.get('height'))
        self.aspectRatio = cast(float, data.attrib.get('aspectRatio'))
        self.audioChannels = cast(int, data.attrib.get('audioChannels'))
        self.audioCodec = data.attrib.get('audioCodec')
        self.videoCodec = data.attrib.get('videoCodec')
        self.container = data.attrib.get('container')
        self.videoFrameRate = data.attrib.get('videoFrameRate')
        self.optimizedForStreaming = cast(bool, data.attrib.get('optimizedForStreaming'))
        self.optimizedForStreaming = cast(bool, data.attrib.get('has64bitOffsets'))
        self.parts = [MediaPart(server, elem, initpath, self) for elem in data]

    def __repr__(self):
        title = self.video.title.replace(' ','.')[0:20]
        return '<%s:%s>' % (self.__class__.__name__, title.encode('utf8'))


class MediaPart(object):
    TYPE = 'Part'

    def __init__(self, server, data, initpath, media):
        self.server = server
        self.initpath = initpath
        self.media = media
        self.id = cast(int, data.attrib.get('id'))
        self.key = data.attrib.get('key')
        self.duration = cast(int, data.attrib.get('duration'))
        self.file = data.attrib.get('file')
        self.size = cast(int, data.attrib.get('size'))
        self.container = data.attrib.get('container')
        self.streams = [MediaPartStream.parse(self.server, e, self.initpath, self) for e in data if e.tag == 'Stream']

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.id)

    def selectedStream(self, stream_type):
        streams = filter(lambda x: stream_type == x.type, self.streams)
        selected = list(filter(lambda x: x.selected is True, streams))
        if len(selected) == 0:
            return None
        return selected[0]


class MediaPartStream(object):
    TYPE = None
    STREAMTYPE = None

    def __init__(self, server, data, initpath, part):
        self.server = server
        self.initpath = initpath
        self.part = part
        self.codec = data.attrib.get('codec')
        self.codecID = data.attrib.get('codecID')
        self.id = cast(int, data.attrib.get('id'))
        self.index = cast(int, data.attrib.get('index', '-1'))
        self.language = data.attrib.get('language')
        self.languageCode = data.attrib.get('languageCode')
        self.selected = cast(bool, data.attrib.get('selected', '0'))
        self.streamType = cast(int, data.attrib.get('streamType'))
        self.type = cast(int, data.attrib.get('streamType'))

    @staticmethod
    def parse(server, data, initpath, part):
        STREAMCLS = {1:VideoStream, 2:AudioStream, 3:SubtitleStream}
        stype = cast(int, data.attrib.get('streamType'))
        cls = STREAMCLS.get(stype, MediaPartStream)
        return cls(server, data, initpath, part)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.id)


class VideoStream(MediaPartStream):
    TYPE = 'videostream'
    STREAMTYPE = 1

    def __init__(self, server, data, initpath, part):
        super(VideoStream, self).__init__(server, data, initpath, part)
        self.bitrate = cast(int, data.attrib.get('bitrate'))
        self.bitDepth = cast(int, data.attrib.get('bitDepth'))
        self.cabac = cast(int, data.attrib.get('cabac'))
        self.chromaSubsampling = data.attrib.get('chromaSubsampling')
        self.colorSpace = data.attrib.get('colorSpace')
        self.duration = cast(int, data.attrib.get('duration'))
        self.frameRate = cast(float, data.attrib.get('frameRate'))
        self.frameRateMode = data.attrib.get('frameRateMode')
        self.hasScallingMatrix = cast(bool, data.attrib.get('hasScallingMatrix'))
        self.height = cast(int, data.attrib.get('height'))
        self.level = cast(int, data.attrib.get('level'))
        self.profile = data.attrib.get('profile')
        self.refFrames = cast(int, data.attrib.get('refFrames'))
        self.scanType = data.attrib.get('scanType')
        self.title = data.attrib.get('title')
        self.width = cast(int, data.attrib.get('width'))


class AudioStream(MediaPartStream):
    TYPE = 'audiostream'
    STREAMTYPE = 2

    def __init__(self, server, data, initpath, part):
        super(AudioStream, self).__init__(server, data, initpath, part)
        self.audioChannelLayout = data.attrib.get('audioChannelLayout')
        self.channels = cast(int, data.attrib.get('channels'))
        self.bitrate = cast(int, data.attrib.get('bitrate'))
        self.bitDepth = cast(int, data.attrib.get('bitDepth'))
        self.bitrateMode = data.attrib.get('bitrateMode')
        self.dialogNorm = cast(int, data.attrib.get('dialogNorm'))
        self.duration = cast(int, data.attrib.get('duration'))
        self.samplingRate = cast(int, data.attrib.get('samplingRate'))
        self.title = data.attrib.get('title')


class SubtitleStream(MediaPartStream):
    TYPE = 'subtitlestream'
    STREAMTYPE = 3

    def __init__(self, server, data, initpath, part):
        super(SubtitleStream, self).__init__(server, data, initpath, part)
        self.key = data.attrib.get('key')
        self.format = data.attrib.get('format')
        self.title = data.attrib.get('title')


class TranscodeSession(object):
    TYPE = 'TranscodeSession'

    def __init__(self, server, data):
        self.server = server
        self.key = data.attrib.get('key')
        self.throttled = cast(int, data.attrib.get('throttled'))
        self.progress = cast(float, data.attrib.get('progress'))
        self.speed = cast(int, data.attrib.get('speed'))
        self.duration = cast(int, data.attrib.get('duration'))
        self.remaining = cast(int, data.attrib.get('remaining'))
        self.context = data.attrib.get('context')
        self.videoDecision = data.attrib.get('videoDecision')
        self.audioDecision = data.attrib.get('audioDecision')
        self.protocol = data.attrib.get('protocol')
        self.container = data.attrib.get('container')
        self.videoCodec = data.attrib.get('videoCodec')
        self.audioCodec = data.attrib.get('audioCodec')
        self.audioChannels = cast(int, data.attrib.get('audioChannels'))
        self.width = cast(int, data.attrib.get('width'))
        self.height = cast(int, data.attrib.get('height'))


class MediaTag(object):
    TYPE = None

    def __init__(self, server, data):
        self.server = server
        self.id = cast(int, data.attrib.get('id'))
        self.tag = data.attrib.get('tag')
        self.role = data.attrib.get('role')

    def __repr__(self):
        tag = self.tag.replace(' ','.')[0:20]
        return '<%s:%s:%s>' % (self.__class__.__name__, self.id, tag)


class Collection(MediaTag): TYPE = 'Collection'; FILTER = 'collection'
class Country(MediaTag): TYPE = 'Country'; FILTER = 'country'
class Director(MediaTag): TYPE = 'Director'; FILTER = 'director'
class Genre(MediaTag): TYPE = 'Genre'; FILTER = 'genre'
class Mood(MediaTag): TYPE = 'Mood'; FILTER = 'mood'
class Producer(MediaTag): TYPE = 'Producer'; FILTER = 'producer'
class Role(MediaTag): TYPE = 'Role'; FILTER = 'role'
class Similar(MediaTag): TYPE = 'Similar'; FILTER = 'similar'
class Writer(MediaTag): TYPE = 'Writer'; FILTER = 'writer'
