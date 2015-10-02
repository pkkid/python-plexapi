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
        self.streams = [
            MediaPartStream.parse(self.server, elem, self.initpath, self)
            for elem in data if elem.tag == MediaPartStream.TYPE
        ]

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.id)

    def selected_stream(self, stream_type):
        streams = filter(lambda x: stream_type == x.type, self.streams)
        selected = list(filter(lambda x: x.selected is True, streams))
        if len(selected) == 0:
            return None

        return selected[0]


class MediaPartStream(object):
    TYPE = 'Stream'

    def __init__(self, server, data, initpath, part):
        self.server = server
        self.initpath = initpath
        self.part = part
        self.id = cast(int, data.attrib.get('id'))
        self.type = cast(int, data.attrib.get('streamType'))
        self.codec = data.attrib.get('codec')
        self.selected = cast(bool, data.attrib.get('selected', '0'))
        self.index = cast(int, data.attrib.get('index', '-1'))

    @staticmethod
    def parse(server, data, initpath, part):
        STREAMCLS = {
            StreamVideo.TYPE: StreamVideo,
            StreamAudio.TYPE: StreamAudio,
            StreamSubtitle.TYPE: StreamSubtitle
        }

        stype = cast(int, data.attrib.get('streamType'))
        cls = STREAMCLS.get(stype, MediaPartStream)
        # return generic MediaPartStream if type is unknown
        return cls(server, data, initpath, part)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.id)


class StreamVideo(MediaPartStream):
    TYPE = 1

    def __init__(self, server, data, initpath, part):
        super(StreamVideo, self).__init__(server, data, initpath, part)
        self.bitrate = cast(int, data.attrib.get('bitrate'))
        self.language = data.attrib.get('langauge')
        self.language_code = data.attrib.get('languageCode')
        self.bit_depth = cast(int, data.attrib.get('bitDepth'))
        self.cabac = cast(int, data.attrib.get('cabac'))
        self.chroma_subsampling = data.attrib.get('chromaSubsampling')
        self.codec_id = data.attrib.get('codecID')
        self.color_space = data.attrib.get('colorSpace')
        self.duration = cast(int, data.attrib.get('duration'))
        self.frame_rate = cast(float, data.attrib.get('frameRate'))
        self.frame_rate_mode = data.attrib.get('frameRateMode')
        self.has_scalling_matrix = cast(bool, data.attrib.get('hasScallingMatrix'))
        self.height = cast(int, data.attrib.get('height'))
        self.level = cast(int, data.attrib.get('level'))
        self.profile = data.attrib.get('profile')
        self.ref_frames = cast(int, data.attrib.get('refFrames'))
        self.scan_type = data.attrib.get('scanType')
        self.title = data.attrib.get('title')
        self.width = cast(int, data.attrib.get('width'))


class StreamAudio(MediaPartStream):
    TYPE = 2

    def __init__(self, server, data, initpath, part):
        super(StreamAudio, self).__init__(server, data, initpath, part)
        self.channels = cast(int, data.attrib.get('channels'))
        self.bitrate = cast(int, data.attrib.get('bitrate'))
        self.bit_depth = cast(int, data.attrib.get('bitDepth'))
        self.bitrate_mode = data.attrib.get('bitrateMode')
        self.codec_id = data.attrib.get('codecID')
        self.dialog_norm = cast(int, data.attrib.get('dialogNorm'))
        self.duration = cast(int, data.attrib.get('duration'))
        self.sampling_rate = cast(int, data.attrib.get('samplingRate'))
        self.title = data.attrib.get('title')


class StreamSubtitle(MediaPartStream):
    TYPE = 3

    def __init__(self, server, data, initpath, part):
        super(StreamSubtitle, self).__init__(server, data, initpath, part)
        self.key = data.attrib.get('key')
        self.language = data.attrib.get('langauge')
        self.language_code = data.attrib.get('languageCode')
        self.format = data.attrib.get('format')


class VideoTag(object):
    TYPE = None

    def __init__(self, server, data):
        self.server = server
        self.id = cast(int, data.attrib.get('id'))
        self.tag = data.attrib.get('tag')
        self.role = data.attrib.get('role')

    def __repr__(self):
        tag = self.tag.replace(' ','.')[0:20]
        return '<%s:%s:%s>' % (self.__class__.__name__, self.id, tag)


class Country(VideoTag): TYPE='Country'; FILTER='country'  # noqa
class Director(VideoTag): TYPE = 'Director'; FILTER='director'  # noqa
class Genre(VideoTag): TYPE='Genre'; FILTER='genre'  # noqa
class Producer(VideoTag): TYPE = 'Producer'; FILTER='producer'  # noqa
class Actor(VideoTag): TYPE = 'Role'; FILTER='actor'  # noqa
class Writer(VideoTag): TYPE = 'Writer'; FILTER='writer'  # noqa
