# -*- coding: utf-8 -*-

def test_audio_Artist_attr(a_artist):
    m = a_artist
    m.reload()
    assert str(m.addedAt.date()) == '2017-01-17'
    assert m.countries == []
    assert [i.tag for i in m.genres] == ['Electronic']
    assert m.guid == 'com.plexapp.agents.lastfm://Infinite%20State?lang=en'
    assert m.index == '1'
    assert m.initpath == '/library/metadata/20'
    assert m.key == '/library/metadata/20'
    assert m.librarySectionID == '3'
    assert m.listType == 'audio'
    assert m.location == '/media/music/unmastered_impulses'
    assert m.ratingKey == 20
    assert m.server.baseurl == 'http://138.68.157.5:32400'
    assert m.similar == []
    assert m.summary == ""
    assert m.title == 'Infinite State'
    assert m.titleSort == 'Infinite State'
    assert m.type == 'artist'
    # keeps breaking because of timezone differences between us
    # assert str(m.updatedAt.date()) == '2017-02-01'  
    assert m.viewCount == 0


def test_audio_Artist_get(a_artist, a_music_section):
    a_artist == a_music_section.searchArtists(**{'title': 'Infinite State'})[0]
    a_artist.title == 'Infinite State'


def test_audio_Artist_track(a_artist):
    track = a_artist.track('Holy Moment')
    assert track.title == 'Holy Moment'


def test_audio_Artist_tracks(a_artist):
    tracks = a_artist.tracks()
    assert len(tracks) == 14


def test_audio_Artist_album(a_artist):
    album = a_artist.album('Unmastered Impulses')
    assert album.title == 'Unmastered Impulses'


def test_audio_Artist_albums(a_artist):
    albums = a_artist.albums()
    assert len(albums) == 1 and albums[0].title == 'Unmastered Impulses'


def test_audio_Album_attrs(a_music_album):
    m = a_music_album
    assert str(m.addedAt.date()) == '2017-01-17'
    assert [i.tag for i in m.genres] == ['Electronic']
    assert m.index == '1'
    assert m.initpath == '/library/metadata/21'
    assert m.key == '/library/metadata/21'
    assert m.librarySectionID == '3'
    assert m.listType == 'audio'
    assert str(m.originallyAvailableAt.date()) == '2016-01-01'
    assert m.parentKey == '/library/metadata/20'
    assert m.parentRatingKey == '20'
    assert str(m.parentThumb) == '__NA__'
    assert m.parentTitle == 'Infinite State'
    assert m.ratingKey == 21
    assert m.server.baseurl == 'http://138.68.157.5:32400'
    assert str(m.studio) == '__NA__'
    assert m.summary == ''
    assert m.thumb == '/library/metadata/21/thumb/1484693407'
    assert m.title == 'Unmastered Impulses'
    assert m.titleSort == 'Unmastered Impulses'
    assert m.type == 'album'
    assert str(m.updatedAt.date()) == '2017-01-17'
    assert m.viewCount == 0
    assert m.year == 2016


def test_audio_Album_tracks(a_music_album):
    tracks = a_music_album.tracks()
    assert len(tracks) == 14
    assert tracks[0].grandparentKey == '/library/metadata/20'
    assert tracks[0].grandparentRatingKey == '20'
    assert tracks[0].grandparentTitle == 'Infinite State'
    assert tracks[0].index == '1'
    assert tracks[0].initpath == '/library/metadata/21/children'
    assert tracks[0].key == '/library/metadata/22'
    assert tracks[0].listType == 'audio'
    assert tracks[0].originalTitle == 'Kenneth Reitz'
    assert tracks[0].parentIndex == '1'
    assert tracks[0].parentKey == '/library/metadata/21'
    assert tracks[0].parentRatingKey == '21'
    assert tracks[0].parentThumb == '/library/metadata/21/thumb/1484693407'
    assert tracks[0].parentTitle == 'Unmastered Impulses'
    assert tracks[0].player is None
    assert tracks[0].ratingCount == 9
    assert tracks[0].ratingKey == 22
    assert tracks[0].server.baseurl == 'http://138.68.157.5:32400'
    assert tracks[0].summary == ""
    assert tracks[0].thumb == '/library/metadata/21/thumb/1484693407'
    assert tracks[0].title == 'Holy Moment'
    assert tracks[0].titleSort == 'Holy Moment'
    assert tracks[0].transcodeSession is None
    assert tracks[0].type == 'track'
    assert str(tracks[0].updatedAt.date()) == '2017-01-17'
    assert tracks[0].username is None
    assert tracks[0].viewCount == 0
    assert tracks[0].viewOffset == 0


def test_audio_Album_track(a_music_album):
    # this is not reloaded. its not that much info missing.
    track = a_music_album.track('Holy Moment')
    assert str(track.addedAt.date()) == '2017-01-17'
    assert track.duration == 298606
    assert track.grandparentKey == '/library/metadata/20'
    assert track.grandparentRatingKey == '20'
    assert track.grandparentTitle == 'Infinite State'
    assert track.index == '1'
    assert track.initpath == '/library/metadata/21/children'
    assert track.key == '/library/metadata/22'
    assert track.listType == 'audio'
    # Assign 0 track.media
    med0 = track.media[0]
    assert track.originalTitle == 'Kenneth Reitz'
    assert track.parentIndex == '1'
    assert track.parentKey == '/library/metadata/21'
    assert track.parentRatingKey == '21'
    assert track.parentThumb == '/library/metadata/21/thumb/1484693407'
    assert track.parentTitle == 'Unmastered Impulses'
    assert track.player is None
    assert track.ratingCount == 9
    assert track.ratingKey == 22
    assert track.server.baseurl == 'http://138.68.157.5:32400'
    assert track.summary == ''
    assert track.thumb == '/library/metadata/21/thumb/1484693407'
    assert track.title == 'Holy Moment'
    assert track.titleSort == 'Holy Moment'
    assert track.transcodeSession is None
    assert track.type == 'track'
    assert str(track.updatedAt.date()) == '2017-01-17'
    assert track.username is None
    assert track.viewCount == 0
    assert track.viewOffset == 0
    assert med0.aspectRatio is None
    assert med0.audioChannels == 2
    assert med0.audioCodec == 'mp3'
    assert med0.bitrate == 385
    assert med0.container == 'mp3'
    assert med0.duration == 298606
    assert med0.height is None
    assert med0.id == 22
    assert med0.initpath == '/library/metadata/21/children'
    assert med0.optimizedForStreaming is None
    # Assign 0 med0.parts
    par0 = med0.parts[0]
    assert med0.server.baseurl == 'http://138.68.157.5:32400'
    assert med0.videoCodec is None
    assert med0.videoFrameRate is None
    assert med0.videoResolution is None
    assert med0.width is None
    assert par0.container == 'mp3'
    assert par0.duration == 298606
    assert par0.file == '/media/music/unmastered_impulses/01-Holy_Moment.mp3'
    assert par0.id == 22
    assert par0.initpath == '/library/metadata/21/children'
    assert par0.key == '/library/parts/22/1484693136/file.mp3'
    assert par0.server.baseurl == 'http://138.68.157.5:32400'
    assert par0.size == 14360402


def test_audio_Album_get():
    """ Just a alias for track(); skip it. """
    pass


def test_audio_Album_artist(a_music_album):
    artist = a_music_album.artist()
    artist.title == 'Infinite State'


def test_audio_Track_attrs(a_music_album):
    track = a_music_album.get('Holy Moment')
    track.reload()
    assert str(track.addedAt.date()) == '2017-01-17'
    assert str(track.art) == '__NA__'
    assert str(track.chapterSource) == '__NA__'
    assert track.duration == 298606
    assert str(track.grandparentArt) == '__NA__'
    assert track.grandparentKey == '/library/metadata/20'
    assert track.grandparentRatingKey == '20'
    assert str(track.grandparentThumb) == '__NA__'
    assert track.grandparentTitle == 'Infinite State'
    assert track.guid == 'local://22'
    assert track.index == '1'
    assert track.initpath == '/library/metadata/22'
    assert track.key == '/library/metadata/22'
    assert str(track.lastViewedAt) == '__NA__'
    assert track.librarySectionID == '3'
    assert track.listType == 'audio'
    # Assign 0 track.media
    med0 = track.media[0]
    assert track.moods == []
    assert track.originalTitle == 'Kenneth Reitz'
    assert track.parentIndex == '1'
    assert track.parentKey == '/library/metadata/21'
    assert track.parentRatingKey == '21'
    assert track.parentThumb == '/library/metadata/21/thumb/1484693407'
    assert track.parentTitle == 'Unmastered Impulses'
    assert track.player is None
    assert str(track.playlistItemID) == '__NA__'
    assert str(track.primaryExtraKey) == '__NA__'
    assert track.ratingCount == 9
    assert track.ratingKey == 22
    assert track.server.baseurl == 'http://138.68.157.5:32400'
    assert str(track.sessionKey) == '__NA__'
    assert track.summary == ''
    assert track.thumb == '/library/metadata/21/thumb/1484693407'
    assert track.title == 'Holy Moment'
    assert track.titleSort == 'Holy Moment'
    assert track.transcodeSession is None
    assert track.type == 'track'
    assert str(track.updatedAt.date()) == '2017-01-17'
    assert track.username is None
    assert track.viewCount == 0
    assert track.viewOffset == 0
    assert str(track.viewedAt) == '__NA__'
    assert str(track.year) == '__NA__'
    assert med0.aspectRatio is None
    assert med0.audioChannels == 2
    assert med0.audioCodec == 'mp3'
    assert med0.bitrate == 385
    assert med0.container == 'mp3'
    assert med0.duration == 298606
    assert med0.height is None
    assert med0.id == 22
    assert med0.initpath == '/library/metadata/22'
    assert med0.optimizedForStreaming is None
    # Assign 0 med0.parts
    par0 = med0.parts[0]
    assert med0.server.baseurl == 'http://138.68.157.5:32400'
    assert med0.videoCodec is None
    assert med0.videoFrameRate is None
    assert med0.videoResolution is None
    assert med0.width is None
    assert par0.container == 'mp3'
    assert par0.duration == 298606
    assert par0.file == '/media/music/unmastered_impulses/01-Holy_Moment.mp3'
    assert par0.id == 22
    assert par0.initpath == '/library/metadata/22'
    assert par0.key == '/library/parts/22/1484693136/file.mp3'
    #assert par0.media == <Media:Holy.Moment>
    assert par0.server.baseurl == 'http://138.68.157.5:32400'
    assert par0.size == 14360402
    # Assign 0 par0.streams
    str0 = par0.streams[0]
    assert str0.audioChannelLayout == 'stereo'
    assert str0.bitDepth is None
    assert str0.bitrate == 320
    assert str0.bitrateMode is None
    assert str0.channels == 2
    assert str0.codec == 'mp3'
    assert str0.codecID is None
    assert str0.dialogNorm is None
    assert str0.duration is None
    assert str0.id == 44
    assert str0.index == 0
    assert str0.initpath == '/library/metadata/22'
    assert str0.language is None
    assert str0.languageCode is None
    #assert str0.part == <MediaPart:22>
    assert str0.samplingRate == 44100
    assert str0.selected is True
    assert str0.server.baseurl == 'http://138.68.157.5:32400'
    assert str0.streamType == 2
    assert str0.title is None
    assert str0.type == 2


def test_audio_Track_album(a_music_album):
    assert a_music_album.tracks()[0].album() == a_music_album


def test_audio_Track_artist(a_music_album, a_artist):
    assert a_music_album.tracks()[0].artist() == a_artist


def test_audio_Audio_section(a_artist, a_music_album, a_track):
    assert a_artist.section()
    assert a_music_album.section()
    assert a_track.section()
    assert a_track.section().key == a_music_album.section().key == a_artist.section().key


def test_audio_Track_download(monkeydownload, tmpdir, a_track):
    f = a_track.download(savepath=str(tmpdir))
    assert f


def test_audio_album_download(monkeydownload, a_music_album, tmpdir):
    f = a_music_album.download(savepath=str(tmpdir))
    assert len(f) == 14


def test_audio_Artist_download(monkeydownload, a_artist, tmpdir):
    f = a_artist.download(savepath=str(tmpdir))
    assert len(f) == 14
