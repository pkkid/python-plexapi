# -*- coding: utf-8 -*-
from datetime import datetime
from . import conftest as utils


def test_audio_Artist_attr(artist):
    artist.reload()
    assert utils.is_datetime(artist.addedAt)
    assert artist.countries == []
    assert [i.tag for i in artist.genres] == ['Electronic']
    assert utils.is_string(artist.guid, gte=5)
    assert artist.index == '1'
    assert utils.is_metadata(artist._initpath)
    assert utils.is_metadata(artist.key)
    assert utils.is_int(artist.librarySectionID)
    assert artist.listType == 'audio'
    assert len(artist.locations) == 1
    assert len(artist.locations[0]) >= 10
    assert artist.ratingKey >= 1
    assert artist._server._baseurl == utils.SERVER_BASEURL
    assert [a.tag for a in artist.similar] == ['Kenneth Reitz']
    assert artist.summary == ''
    assert artist.title == 'Infinite State'
    assert artist.titleSort == 'Infinite State'
    assert artist.type == 'artist'
    assert utils.is_datetime(artist.updatedAt)
    assert utils.is_int(artist.viewCount, gte=0)


def test_audio_Artist_get(artist, music):
    artist == music.searchArtists(**{'title': 'Infinite State'})[0]
    artist.title == 'Infinite State'


def test_audio_Artist_track(artist):
    track = artist.track('Holy Moment')
    assert track.title == 'Holy Moment'


def test_audio_Artist_tracks(artist):
    tracks = artist.tracks()
    assert len(tracks) == 14


def test_audio_Artist_album(artist):
    album = artist.album('Unmastered Impulses')
    assert album.title == 'Unmastered Impulses'


def test_audio_Artist_albums(artist):
    albums = artist.albums()
    assert len(albums) == 1 and albums[0].title == 'Unmastered Impulses'


def test_audio_Album_attrs(album):
    assert utils.is_datetime(album.addedAt)
    assert [i.tag for i in album.genres] == ['Electronic']
    assert album.index == '1'
    assert utils.is_metadata(album._initpath)
    assert utils.is_metadata(album.key)
    assert utils.is_int(album.librarySectionID)
    assert album.listType == 'audio'
    assert album.originallyAvailableAt == datetime(2016, 1, 1)
    assert utils.is_metadata(album.parentKey)
    assert utils.is_int(album.parentRatingKey)
    if album.parentThumb:
        assert utils.is_metadata(album.parentThumb, contains='/thumb/')
    assert album.parentTitle == 'Infinite State'
    assert album.ratingKey >= 1
    assert album._server._baseurl == utils.SERVER_BASEURL
    assert album.studio is None
    assert album.summary == ''
    assert utils.is_metadata(album.thumb, contains='/thumb/')
    assert album.title == 'Unmastered Impulses'
    assert album.titleSort == 'Unmastered Impulses'
    assert album.type == 'album'
    assert utils.is_datetime(album.updatedAt)
    assert utils.is_int(album.viewCount, gte=0)
    assert album.year == 2016


def test_audio_Album_tracks(album):
    tracks = album.tracks()
    track = tracks[0]
    assert len(tracks) == 14
    assert utils.is_metadata(track.grandparentKey)
    assert utils.is_int(track.grandparentRatingKey)
    assert track.grandparentTitle == 'Infinite State'
    assert track.index == '1'
    assert utils.is_metadata(track._initpath)
    assert utils.is_metadata(track.key)
    assert track.listType == 'audio'
    assert track.originalTitle == 'Kenneth Reitz'
    assert utils.is_int(track.parentIndex)
    assert utils.is_metadata(track.parentKey)
    assert utils.is_int(track.parentRatingKey)
    assert utils.is_metadata(track.parentThumb, contains='/thumb/')
    assert track.parentTitle == 'Unmastered Impulses'
    assert track.ratingCount == 9
    assert utils.is_int(track.ratingKey)
    assert track._server._baseurl == utils.SERVER_BASEURL
    assert track.summary == ""
    assert utils.is_metadata(track.thumb, contains='/thumb/')
    assert track.title == 'Holy Moment'
    assert track.titleSort == 'Holy Moment'
    assert not track.transcodeSessions
    assert track.type == 'track'
    assert utils.is_datetime(track.updatedAt)
    assert utils.is_int(track.viewCount, gte=0)
    assert track.viewOffset == 0


def test_audio_Album_track(album, track=None):
    # this is not reloaded. its not that much info missing.
    track = track or album.track('Holy Moment')
    assert utils.is_datetime(track.addedAt)
    assert track.duration == 298606
    assert utils.is_metadata(track.grandparentKey)
    assert utils.is_int(track.grandparentRatingKey)
    assert track.grandparentTitle == 'Infinite State'
    assert int(track.index) == 1
    assert utils.is_metadata(track._initpath)
    assert utils.is_metadata(track.key)
    assert track.listType == 'audio'
    # Assign 0 track.media
    media = track.media[0]
    assert track.originalTitle == 'Kenneth Reitz'
    assert utils.is_int(track.parentIndex)
    assert utils.is_metadata(track.parentKey)
    assert utils.is_int(track.parentRatingKey)
    assert utils.is_metadata(track.parentThumb, contains='/thumb/')
    assert track.parentTitle == 'Unmastered Impulses'
    assert track.ratingCount == 9
    assert utils.is_int(track.ratingKey)
    assert track._server._baseurl == utils.SERVER_BASEURL
    assert track.summary == ''
    assert utils.is_metadata(track.thumb, contains='/thumb/')
    assert track.title == 'Holy Moment'
    assert track.titleSort == 'Holy Moment'
    assert not track.transcodeSessions
    assert track.type == 'track'
    assert utils.is_datetime(track.updatedAt)
    assert utils.is_int(track.viewCount, gte=0)
    assert track.viewOffset == 0
    assert media.aspectRatio is None
    assert media.audioChannels == 2
    assert media.audioCodec == 'mp3'
    assert media.bitrate == 385
    assert media.container == 'mp3'
    assert media.duration == 298606
    assert media.height is None
    assert utils.is_int(media.id, gte=1)
    assert utils.is_metadata(media._initpath)
    assert media.optimizedForStreaming is None
    # Assign 0 media.parts
    part = media.parts[0]
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.videoCodec is None
    assert media.videoFrameRate is None
    assert media.videoResolution is None
    assert media.width is None
    assert part.container == 'mp3'
    assert part.duration == 298606
    assert part.file.endswith('.mp3')
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert utils.is_part(part.key)
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert part.size == 14360402


def test_audio_Album_get(album):
    # alias for album.track()
    track = album.get('Holy Moment')
    test_audio_Album_track(album, track=track)


def test_audio_Album_artist(album):
    artist = album.artist()
    artist.title == 'Infinite State'


def test_audio_Track_attrs(album):
    track = album.get('Holy Moment').reload()
    assert utils.is_datetime(track.addedAt)
    assert track.art is None
    assert track.chapterSource is None
    assert track.duration == 298606
    assert track.grandparentArt is None
    assert utils.is_metadata(track.grandparentKey)
    assert utils.is_int(track.grandparentRatingKey)
    if track.grandparentThumb:
        assert utils.is_metadata(track.grandparentThumb, contains='/thumb/')
    assert track.grandparentTitle == 'Infinite State'
    assert track.guid.startswith('local://')
    assert int(track.index) == 1
    assert utils.is_metadata(track._initpath)
    assert utils.is_metadata(track.key)
    if track.lastViewedAt:
        assert utils.is_datetime(track.lastViewedAt)
    assert utils.is_int(track.librarySectionID)
    assert track.listType == 'audio'
    # Assign 0 track.media
    media = track.media[0]
    assert track.moods == []
    assert track.originalTitle == 'Kenneth Reitz'
    assert int(track.parentIndex) == 1
    assert utils.is_metadata(track.parentKey)
    assert utils.is_int(track.parentRatingKey)
    assert utils.is_metadata(track.parentThumb, contains='/thumb/')
    assert track.parentTitle == 'Unmastered Impulses'
    assert track.playlistItemID is None
    assert track.primaryExtraKey is None
    assert track.ratingCount == 9
    assert utils.is_int(track.ratingKey)
    assert track._server._baseurl == utils.SERVER_BASEURL
    assert track.sessionKey is None
    assert track.summary == ''
    assert utils.is_metadata(track.thumb, contains='/thumb/')
    assert track.title == 'Holy Moment'
    assert track.titleSort == 'Holy Moment'
    assert not track.transcodeSessions
    assert track.type == 'track'
    assert utils.is_datetime(track.updatedAt)
    assert utils.is_int(track.viewCount, gte=0)
    assert track.viewOffset == 0
    assert track.viewedAt is None
    assert track.year is None
    assert media.aspectRatio is None
    assert media.audioChannels == 2
    assert media.audioCodec == 'mp3'
    assert media.bitrate == 385
    assert media.container == 'mp3'
    assert media.duration == 298606
    assert media.height is None
    assert utils.is_int(media.id, gte=1)
    assert utils.is_metadata(media._initpath)
    assert media.optimizedForStreaming is None
    # Assign 0 media.parts
    part = media.parts[0]
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.videoCodec is None
    assert media.videoFrameRate is None
    assert media.videoResolution is None
    assert media.width is None
    assert part.container == 'mp3'
    assert part.duration == 298606
    assert part.file.endswith('.mp3')
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert utils.is_part(part.key)
    #assert part.media == <Media:Holy.Moment>
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert part.size == 14360402
    # Assign 0 part.streams
    stream = part.streams[0]
    assert stream.audioChannelLayout == 'stereo'
    assert stream.bitDepth is None
    assert stream.bitrate == 320
    assert stream.bitrateMode is None
    assert stream.channels == 2
    assert stream.codec == 'mp3'
    assert stream.codecID is None
    assert stream.dialogNorm is None
    assert stream.duration is None
    assert utils.is_int(stream.id)
    assert stream.index == 0
    assert utils.is_metadata(stream._initpath)
    assert stream.language is None
    assert stream.languageCode is None
    #assert stream.part == <MediaPart:22>
    assert stream.samplingRate == 44100
    assert stream.selected is True
    assert stream._server._baseurl == utils.SERVER_BASEURL
    assert stream.streamType == 2
    assert stream.title is None
    assert stream.type == 2


def test_audio_Track_album(album):
    tracks = album.tracks()
    assert tracks[0].album() == album


def test_audio_Track_artist(album, artist):
    tracks = album.tracks()
    assert tracks[0].artist() == artist


def test_audio_Audio_section(artist, album, track):
    assert artist.section()
    assert album.section()
    assert track.section()
    assert track.section().key == album.section().key == artist.section().key


def test_audio_Track_download(monkeydownload, tmpdir, track):
    f = track.download(savepath=str(tmpdir))
    assert f


def test_audio_album_download(monkeydownload, album, tmpdir):
    f = album.download(savepath=str(tmpdir))
    assert len(f) == 14


def test_audio_Artist_download(monkeydownload, artist, tmpdir):
    f = artist.download(savepath=str(tmpdir))
    assert len(f) == 14
