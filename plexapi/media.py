# -*- coding: utf-8 -*-
from plexapi.exceptions import BadRequest
from plexapi.utils import cast, listItems


class Media(object):
    """ Container object for all MediaPart objects. Provides useful data about the
        video this media belong to such as video framerate, resolution, etc.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to.
            data (ElementTree): Response from PlexServer used to build this object.
            initpath (str): Relative path requested when retrieving specified `data`.
            video (:class:`~plexapi.video.Video`): Video this media belongs to.

        Attributes:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            initpath (str): Relative path requested when retrieving specified data.
            video (str): Video this media belongs to.
            aspectRatio (float): Aspect ratio of the video (ex: 2.35).
            audioChannels (int): Number of audio channels for this video (ex: 6).
            audioCodec (str): Audio codec used within the video (ex: ac3).
            bitrate (int): Bitrate of the video (ex: 1624)
            container (str): Container this video is in (ex: avi).
            duration (int): Length of the video in milliseconds (ex: 6990483).
            height (int): Height of the video in pixels (ex: 256).
            id (int): Plex ID of this media item (ex: 46184).
            has64bitOffsets (bool): True if video has 64 bit offsets (?).
            optimizedForStreaming (bool): True if video is optimized for streaming.
            videoCodec (str): Video codec used within the video (ex: ac3).
            videoFrameRate (str): Video frame rate (ex: 24p).
            videoResolution (str): Video resolution (ex: sd).
            width (int): Width of the video in pixels (ex: 608).
            parts (list<:class:`~plexapi.media.MediaPart`>): List of MediaParts in this video.
    """
    TYPE = 'Media'

    def __init__(self, server, data, initpath, video):
        self.server = server
        self.initpath = initpath
        self.video = video
        self.aspectRatio = cast(float, data.attrib.get('aspectRatio'))
        self.audioChannels = cast(int, data.attrib.get('audioChannels'))
        self.audioCodec = data.attrib.get('audioCodec')
        self.bitrate = cast(int, data.attrib.get('bitrate'))
        self.container = data.attrib.get('container')
        self.duration = cast(int, data.attrib.get('duration'))
        self.height = cast(int, data.attrib.get('height'))
        self.id = cast(int, data.attrib.get('id'))
        self.has64bitOffsets = cast(bool, data.attrib.get('has64bitOffsets'))
        self.optimizedForStreaming = cast(bool, data.attrib.get('optimizedForStreaming'))
        self.videoCodec = data.attrib.get('videoCodec')
        self.videoFrameRate = data.attrib.get('videoFrameRate')
        self.videoResolution = data.attrib.get('videoResolution')
        self.width = cast(int, data.attrib.get('width'))
        self.parts = [MediaPart(server, e, initpath, self) for e in data]

    def __repr__(self):
        title = self.video.title.replace(' ','.')[0:20]
        return '<%s:%s>' % (self.__class__.__name__, title.encode('utf8'))


class MediaPart(object):
    """ Represents a single media part (often a single file) for the media this belongs to.
        
        Attributes:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            initpath (str): Relative path requested when retrieving specified data.
            media (:class:`~plexapi.media.Media`): Media object this part belongs to.
            container (str): Container type of this media part (ex: avi).
            duration (int): Length of this media part in milliseconds.
            file (str): Path to this file on disk (ex: /media/Movies/Cars.(2006)/Cars.cd2.avi)
            id (int): Unique ID of this media part.
            key (str): Key used to access this media part (ex: /library/parts/46618/1389985872/file.avi).
            size (int): Size of this file in bytes (ex: 733884416).
            streams (list<:class:`~plexapi.media.MediaPartStream`>): List of streams in this media part.
    """
    TYPE = 'Part'

    def __init__(self, server, data, initpath, media):
        self.server = server
        self.initpath = initpath
        self.media = media
        self.container = data.attrib.get('container')
        self.duration = cast(int, data.attrib.get('duration'))
        self.file = data.attrib.get('file')
        self.id = cast(int, data.attrib.get('id'))
        self.key = data.attrib.get('key')
        self.size = cast(int, data.attrib.get('size'))
        self.streams = [MediaPartStream.parse(self.server, e, self.initpath, self) for e in data if e.tag == 'Stream']

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.id)

    def selectedStream(self, stream_type):
        """ Return the selected stream for the specified stream_type.
            
            Paramters:
                stream_type (int): Specify which stream type you want the result for. This value
                    should be one of (1=:class:`~plexapi.media.VideoStream`,
                    2=:class:`~plexapi.media.AudioStream`, 3=:class:`~plexapi.media.SubtitleStream`).
        """
        streams = filter(lambda x: stream_type == x.type, self.streams)
        selected = list(filter(lambda x: x.selected is True, streams))
        if len(selected) == 0:
            return None
        return selected[0]


class MediaPartStream(object):
    """ Base class for media streams. These consist of video, audio and subtitles.
        
        Attributes:
            server (:class:`~plexapi.server.PlexServer`): PlexServer object this is from.
            initpath (str): Relative path requested when retrieving specified data.
            part (:class:`~plexapi.media.MediaPart`): Media part this stream belongs to.
            codec (str): Codec of this stream (ex: srt, ac3, mpeg4).
            codecID (str): Codec ID (ex: XVID).
            id (int): Unique stream ID on this server.
            index (int): Unknown
            language (str): Stream language (ex: English, ไทย).
            languageCode (str): Ascii code for language (ex: eng, tha).
            selected (bool): True if this stream is selected.
            streamType (int): Stream type (1=:class:`~plexapi.media.VideoStream`,
                2=:class:`~plexapi.media.AudioStream`, 3=:class:`~plexapi.media.SubtitleStream`).
            type (int): Alias for streamType.
    """
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
        """ Factory method returns a new MediaPartStream from xml data. """
        STREAMCLS = {1:VideoStream, 2:AudioStream, 3:SubtitleStream}
        stype = cast(int, data.attrib.get('streamType'))
        cls = STREAMCLS.get(stype, MediaPartStream)
        return cls(server, data, initpath, part)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.id)


class VideoStream(MediaPartStream):
    """ Respresents a video stream within a :class:`~plexapi.media.MediaPart`.

        Attributes:
            bitDepth (int): Bit depth (ex: 8).
            bitrate (int): Bitrate (ex: 1169)
            cabac (int): Unknown
            chromaSubsampling (str): Chroma Subsampling (ex: 4:2:0).
            colorSpace (str): Unknown
            duration (int): Duration of video stream in milliseconds.
            frameRate (float): Frame rate (ex: 23.976)
            frameRateMode (str): Unknown
            hasScallingMatrix (bool): True if video stream has a scaling matrix.
            height (int): Height of video stream.
            level (int): Videl stream level (?).
            profile (str): Video stream profile (ex: asp).
            refFrames (int): Unknown
            scanType (str): Video stream scan type (ex: progressive).
            title (str): Title of this video stream.
            width (int): Width of video stream.
    """
    TYPE = 'videostream'
    STREAMTYPE = 1

    def __init__(self, server, data, initpath, part):
        super(VideoStream, self).__init__(server, data, initpath, part)
        self.bitDepth = cast(int, data.attrib.get('bitDepth'))
        self.bitrate = cast(int, data.attrib.get('bitrate'))
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
    """ Respresents a audio stream within a :class:`~plexapi.media.MediaPart`.

        Attributes:
            audioChannelLayout (str): Audio channel layout (ex: 5.1(side)).
            bitDepth (int): Bit depth (ex: 16).
            bitrate (int): Audio bitrate (ex: 448).
            bitrateMode (str): Bitrate mode (ex: cbr).
            channels (int): number of channels in this stream (ex: 6).
            dialogNorm (int): Unknown (ex: -27).
            duration (int): Duration of audio stream in milliseconds.
            samplingRate (int): Sampling rate (ex: xxx)
            title (str): Title of this audio stream.
    """
    TYPE = 'audiostream'
    STREAMTYPE = 2

    def __init__(self, server, data, initpath, part):
        super(AudioStream, self).__init__(server, data, initpath, part)
        self.audioChannelLayout = data.attrib.get('audioChannelLayout')
        self.bitDepth = cast(int, data.attrib.get('bitDepth'))
        self.bitrate = cast(int, data.attrib.get('bitrate'))
        self.bitrateMode = data.attrib.get('bitrateMode')
        self.channels = cast(int, data.attrib.get('channels'))
        self.dialogNorm = cast(int, data.attrib.get('dialogNorm'))
        self.duration = cast(int, data.attrib.get('duration'))
        self.samplingRate = cast(int, data.attrib.get('samplingRate'))
        self.title = data.attrib.get('title')


class SubtitleStream(MediaPartStream):
    """ Respresents a audio stream within a :class:`~plexapi.media.MediaPart`.
        
        Attributes:
            format (str): Subtitle format (ex: srt).
            key (str): Key of this subtitle stream (ex: /library/streams/212284).
            title (str): Title of this subtitle stream.
    """
    TYPE = 'subtitlestream'
    STREAMTYPE = 3

    def __init__(self, server, data, initpath, part):
        super(SubtitleStream, self).__init__(server, data, initpath, part)
        self.format = data.attrib.get('format')
        self.key = data.attrib.get('key')
        self.title = data.attrib.get('title')


class TranscodeSession(object):
    """ Represents a current transcode session. 
        TODO: Document this.
    """
    TYPE = 'TranscodeSession'

    def __init__(self, server, data):
        self.server = server
        self.audioChannels = cast(int, data.attrib.get('audioChannels'))
        self.audioCodec = data.attrib.get('audioCodec')
        self.audioDecision = data.attrib.get('audioDecision')
        self.container = data.attrib.get('container')
        self.context = data.attrib.get('context')
        self.duration = cast(int, data.attrib.get('duration'))
        self.height = cast(int, data.attrib.get('height'))
        self.key = data.attrib.get('key')
        self.progress = cast(float, data.attrib.get('progress'))
        self.protocol = data.attrib.get('protocol')
        self.remaining = cast(int, data.attrib.get('remaining'))
        self.speed = cast(int, data.attrib.get('speed'))
        self.throttled = cast(int, data.attrib.get('throttled'))
        self.videoCodec = data.attrib.get('videoCodec')
        self.videoDecision = data.attrib.get('videoDecision')
        self.width = cast(int, data.attrib.get('width'))


class MediaTag(object):
    """ Base class for media tags used for filtering and searching your library
        items or navigating the metadata of media items in your library. Tags are
        the construct used for things such as Country, Director, Genre, etc.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this client is connected to (optional)
            data (ElementTree): Response from PlexServer used to build this object (optional).

        Attributes:
            server (:class:`~plexapi.server.PlexServer`): Server this client is connected to.
            id (id): Tag ID (This seems meaningless except to use it as a unique id).
            role (str): Unknown
            tag (str): Name of the tag. This will be Animation, SciFi etc for Genres. The name of
                person for Directors and Roles (ex: Animation, Stephen Graham, etc).
            <Hub_Search_Attributes>: Attributes only applicable in search results from
                PlexServer :func:`~plexapi.server.PlexServer.search()`. They provide details of which 
                library section the tag was found as well as the url to dig deeper into the results.
            
                * key (str): API URL to dig deeper into this tag (ex: /library/sections/1/all?actor=9081).
                * librarySectionID (int): Section ID this tag was generated from.
                * librarySectionTitle (str): Library section title this tag was found.
                * librarySectionType (str): Media type of the library section this tag was found.
                * tagType (int): Tag type ID.
                * thumb (str): URL to thumbnail image.
    """
    TYPE = None

    def __init__(self, server, data):
        self._data = data
        self.server = server
        self.id = cast(int, data.attrib.get('id'))
        self.role = data.attrib.get('role')
        self.tag = data.attrib.get('tag')
        # additional attributes only from hub search
        self.key = data.attrib.get('key')
        self.librarySectionID = cast(int, data.attrib.get('librarySectionID'))
        self.librarySectionTitle = data.attrib.get('librarySectionTitle')
        self.librarySectionType = data.attrib.get('librarySectionType')
        self.tagType = cast(int, data.attrib.get('tagType'))
        self.thumb = data.attrib.get('thumb')

    def __repr__(self):
        tag = self.tag.replace(' ', '.')[0:20].encode('utf-8')
        if self.librarySectionTitle:
            return u'<%s:%s:%s:%s>' % (self.__class__.__name__, self.id, tag, self.librarySectionTitle)
        return u'<%s:%s:%s>' % (self.__class__.__name__, self.id, tag)

    def items(self, *args, **kwargs):
        """ Return the list of items within this tag. This function is only applicable
            in search results from PlexServer :func:`~plexapi.server.PlexServer.search()`.
        """
        if not self.key:
            raise BadRequest('Key is not defined for this tag: %s' % self.tag)
        return listItems(self.server, self.key)


class Collection(MediaTag):
    TYPE = 'Collection'
    FILTER = 'collection'


class Country(MediaTag):
    TYPE = 'Country'
    FILTER = 'country'


class Director(MediaTag):
    TYPE = 'Director'
    FILTER = 'director'


class Genre(MediaTag):
    TYPE = 'Genre'
    FILTER = 'genre'


class Mood(MediaTag):
    TYPE = 'Mood'
    FILTER = 'mood'


class Producer(MediaTag):
    TYPE = 'Producer'
    FILTER = 'producer'


class Role(MediaTag):
    TYPE = 'Role'
    FILTER = 'role'


class Similar(MediaTag):
    TYPE = 'Similar'
    FILTER = 'similar'


class Writer(MediaTag):
    TYPE = 'Writer'
    FILTER = 'writer'


class Field(object):
    TYPE = 'Field'

    def __init__(self, data):
        self.name = data.attrib.get('name')
        self.locked = cast(bool, data.attrib.get('locked'))

    def __repr__(self):
        name = self.name.replace(' ', '.')[0:20]
        return '<%s:%s:%s>' % (self.__class__.__name__, name, self.locked)
