# -*- coding: utf-8 -*-
from . import conftest as utils
from . import test_mixins


def test_audio_Artist_attr(artist):
    artist.reload()
    assert utils.is_datetime(artist.addedAt)
    assert artist.albumSort == -1
    if artist.art:
        assert utils.is_art(artist.art)
    if artist.countries:
        assert "United States of America" in [i.tag for i in artist.countries]
    #assert "Electronic" in [i.tag for i in artist.genres]
    assert utils.is_string(artist.guid, gte=5)
    assert artist.index == 1
    assert utils.is_metadata(artist._initpath)
    assert utils.is_metadata(artist.key)
    assert utils.is_int(artist.librarySectionID)
    assert artist.listType == "audio"
    assert len(artist.locations) == 1
    assert len(artist.locations[0]) >= 10
    assert artist.ratingKey >= 1
    assert artist._server._baseurl == utils.SERVER_BASEURL
    assert isinstance(artist.similar, list)
    if artist.summary:
        assert "Alias" in artist.summary
    if artist.thumb:
        assert utils.is_thumb(artist.thumb)
    assert artist.title == "Broke For Free"
    assert artist.titleSort == "Broke For Free"
    assert artist.type == "artist"
    assert utils.is_datetime(artist.updatedAt)
    assert utils.is_int(artist.viewCount, gte=0)


def test_audio_Artist_get(artist, music):
    artist == music.searchArtists(**{"title": "Broke For Free"})[0]
    artist.title == "Broke For Free"


def test_audio_Artist_history(artist):
    history = artist.history()
    assert isinstance(history, list)


def test_audio_Artist_track(artist):
    track = artist.track("As Colourful as Ever")
    assert track.title == "As Colourful as Ever"
    track = artist.track(album="Layers", track=1)
    assert track.parentTitle == "Layers"
    assert track.index == 1


def test_audio_Artist_tracks(artist):
    tracks = artist.tracks()
    assert len(tracks) == 1


def test_audio_Artist_album(artist):
    album = artist.album("Layers")
    assert album.title == "Layers"


def test_audio_Artist_albums(artist):
    albums = artist.albums()
    assert len(albums) == 1 and albums[0].title == "Layers"


def test_audio_Artist_mixins_edit_advanced_settings(artist):
    test_mixins.edit_advanced_settings(artist)


def test_audio_Artist_mixins_images(artist):
    test_mixins.edit_art(artist)
    test_mixins.edit_poster(artist)
    test_mixins.attr_artUrl(artist)
    test_mixins.attr_posterUrl(artist)


def test_audio_Artist_mixins_tags(artist):
    test_mixins.edit_collection(artist)
    test_mixins.edit_country(artist)
    test_mixins.edit_genre(artist)
    test_mixins.edit_mood(artist)
    test_mixins.edit_similar_artist(artist)
    test_mixins.edit_style(artist)


def test_audio_Album_attrs(album):
    assert utils.is_datetime(album.addedAt)
    if album.art:
        assert utils.is_art(album.art)
    assert isinstance(album.genres, list)
    assert album.index == 1
    assert utils.is_metadata(album._initpath)
    assert utils.is_metadata(album.key)
    assert utils.is_int(album.librarySectionID)
    assert album.listType == "audio"
    assert utils.is_datetime(album.originallyAvailableAt)
    assert utils.is_metadata(album.parentKey)
    assert utils.is_int(album.parentRatingKey)
    if album.parentThumb:
        assert utils.is_thumb(album.parentThumb)
    assert album.parentTitle == "Broke For Free"
    assert album.ratingKey >= 1
    assert album._server._baseurl == utils.SERVER_BASEURL
    assert album.studio == "[no label]"
    assert album.summary == ""
    if album.thumb:
        assert utils.is_thumb(album.thumb)
    assert album.title == "Layers"
    assert album.titleSort == "Layers"
    assert album.type == "album"
    assert utils.is_datetime(album.updatedAt)
    assert utils.is_int(album.viewCount, gte=0)
    assert album.year in (2012,)


def test_audio_Album_history(album):
    history = album.history()
    assert isinstance(history, list)


def test_audio_Track_history(track):
    history = track.history()
    assert isinstance(history, list)


def test_audio_Album_tracks(album):
    tracks = album.tracks()
    assert len(tracks) == 1


def test_audio_Album_track(album, track=None):
    # this is not reloaded. its not that much info missing.
    track = track or album.track("As Colourful As Ever")
    track2 = album.track(track=1)
    assert track == track2


def test_audio_Album_get(album):
    # alias for album.track()
    track = album.get("As Colourful As Ever")
    test_audio_Album_track(album, track=track)


def test_audio_Album_artist(album):
    artist = album.artist()
    artist.title == "Broke For Free"


def test_audio_Album_mixins_images(album):
    test_mixins.edit_art(album)
    test_mixins.edit_poster(album)
    test_mixins.attr_artUrl(album)
    test_mixins.attr_posterUrl(album)


def test_audio_Album_mixins_tags(album):
    test_mixins.edit_collection(album)
    test_mixins.edit_genre(album)
    test_mixins.edit_label(album)
    test_mixins.edit_mood(album)
    test_mixins.edit_style(album)


def test_audio_Track_attrs(album):
    track = album.get("As Colourful As Ever").reload()
    assert utils.is_datetime(track.addedAt)
    if track.art:
        assert utils.is_art(track.art)
    assert track.chapterSource is None
    assert utils.is_int(track.duration)
    if track.grandparentArt:
        assert utils.is_art(track.grandparentArt)
    assert utils.is_metadata(track.grandparentKey)
    assert utils.is_int(track.grandparentRatingKey)
    if track.grandparentThumb:
        assert utils.is_thumb(track.grandparentThumb)
    assert track.grandparentTitle == "Broke For Free"
    assert track.guid.startswith("mbid://") or track.guid.startswith("plex://track/")
    assert int(track.index) == 1
    assert utils.is_metadata(track._initpath)
    assert utils.is_metadata(track.key)
    assert utils.is_datetime(track.lastViewedAt)
    assert utils.is_int(track.librarySectionID)
    assert track.listType == "audio"
    assert len(track.locations) == 1
    assert len(track.locations[0]) >= 10
    # Assign 0 track.media
    media = track.media[0]
    assert track.moods == []
    assert track.originalTitle in (None, "Broke For Free")
    assert int(track.parentIndex) == 1
    assert utils.is_metadata(track.parentKey)
    assert utils.is_int(track.parentRatingKey)
    if track.parentThumb:
        assert utils.is_thumb(track.parentThumb)
    assert track.parentTitle == "Layers"
    assert track.playlistItemID is None
    assert track.primaryExtraKey is None
    # assert utils.is_int(track.ratingCount)
    assert utils.is_int(track.ratingKey)
    assert track._server._baseurl == utils.SERVER_BASEURL
    assert track.sessionKey is None
    assert track.summary == ""
    if track.thumb:
        assert utils.is_thumb(track.thumb)
    assert track.title == "As Colourful as Ever"
    assert track.titleSort == "As Colourful as Ever"
    assert not track.transcodeSessions
    assert track.type == "track"
    assert utils.is_datetime(track.updatedAt)
    assert utils.is_int(track.viewCount, gte=0)
    assert track.viewOffset == 0
    assert track.viewedAt is None
    assert track.year is None
    assert media.aspectRatio is None
    assert media.audioChannels == 2
    assert media.audioCodec == "mp3"
    assert media.bitrate == 128
    assert media.container == "mp3"
    assert utils.is_int(media.duration)
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
    assert part.container == "mp3"
    assert utils.is_int(part.duration)
    assert part.file.endswith(".mp3")
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert utils.is_part(part.key)
    # assert part.media == <Media:Holy.Moment>
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert part.size == 3761053
    # Assign 0 part.streams
    stream = part.streams[0]
    assert stream.audioChannelLayout == "stereo"
    assert stream.bitDepth is None
    assert stream.bitrate == 128
    assert stream.bitrateMode is None
    assert stream.channels == 2
    assert stream.codec == "mp3"
    assert stream.duration is None
    assert utils.is_int(stream.id)
    assert stream.index == 0
    assert utils.is_metadata(stream._initpath)
    assert stream.language is None
    assert stream.languageCode is None
    # assert stream.part == <MediaPart:22>
    assert stream.samplingRate == 48000
    assert stream.selected is True
    assert stream._server._baseurl == utils.SERVER_BASEURL
    assert stream.streamType == 2
    assert stream.title is None
    assert stream.type == 2
    assert stream.albumGain is None
    assert stream.albumPeak is None
    assert stream.albumRange is None
    assert stream.endRamp is None
    assert stream.gain is None
    assert stream.loudness is None
    assert stream.lra is None
    assert stream.peak is None
    assert stream.startRamp is None


def test_audio_Track_album(album):
    tracks = album.tracks()
    assert tracks[0].album() == album


def test_audio_Track_artist(album, artist):
    tracks = album.tracks()
    assert tracks[0].artist() == artist


def test_audio_Track_mixins_images(track):
    test_mixins.attr_artUrl(track)
    test_mixins.attr_posterUrl(track)


def test_audio_Track_mixins_tags(track):
    test_mixins.edit_mood(track)


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
    assert len(f) == 1


def test_audio_Artist_download(monkeydownload, artist, tmpdir):
    f = artist.download(savepath=str(tmpdir))
    assert len(f) == 1
