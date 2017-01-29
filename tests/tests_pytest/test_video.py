# -*- coding: utf-8 -*-
#test_the_file_class_method

import os

import pytest


def test_video_Movie(a_movie_section):
    m = a_movie_section.get('Cars')
    assert m.title == 'Cars'

def test_video_Movie_getStreamURL(a_movie):
    assert a_movie.getStreamURL() == "http://138.68.157.5:32400/video/:/transcode/universal/start.m3u8?X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&offset=0&path=%2Flibrary%2Fmetadata%2F1&X-Plex-Token={0}".format(os.environ.get('PLEX_TEST_TOKEN'))
    assert a_movie.getStreamURL(videoResolution='800x600') == "http://138.68.157.5:32400/video/:/transcode/universal/start.m3u8?X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&offset=0&path=%2Flibrary%2Fmetadata%2F1&videoResolution=800x600&X-Plex-Token={0}".format(os.environ.get('PLEX_TEST_TOKEN'))

def test_video_Movie_isFullObject_and_reload(pms):
    movie = pms.library.section('Movies').get('16 Blocks')
    assert movie.isFullObject() is False
    movie.reload()
    assert movie.isFullObject() is True

    movie_via_search = pms.library.search('16 Blocks')[0]
    assert movie_via_search.isFullObject() is False
    movie_via_search.reload()
    assert movie_via_search.isFullObject() is True

    movie_via_section_search = pms.library.section('Movies').search('16 Blocks')[0]
    assert movie_via_section_search.isFullObject() is False
    movie_via_section_search.reload()
    assert movie_via_section_search.isFullObject() is True
    # If the verify that the object has been reloaded. xml from search only returns 3 actors.
    assert len(movie_via_section_search.roles) > 3


def test_video_Movie_isPartialObject(a_movie):
    assert a_movie.isPartialObject()


def test_video_Movie_iterParts(a_movie):
    assert len(list(a_movie.iterParts())) == 1

def test_video_Show_download(monkeydownload, tmpdir, a_movie):
    downloaded_movie = a_movie.download(savepath=str(tmpdir))
    assert len(downloaded_movie) == 1

    downloaded_movie2 = a_movie.download(savepath=str(tmpdir), **{'videoResolution': '500x300'})
    assert len(downloaded_movie2) == 1




def test_video_Movie_attrs_as_much_as_possible(a_movie_section):
    m = a_movie_section.get('Cars')

    assert m.location == '/media/movies/cars/cars.mp4'
    assert str(m.addedAt.date()) == '2017-01-17'
    assert m.art == '/library/metadata/2/art/1484690715'
    assert m.audienceRating == 7.9
    assert m.audienceRatingImage == 'rottentomatoes://image.rating.upright'
    # Assign 0 m.audioStreams
    aud0 = m.audioStreams[0]
    assert m.chapterSource == 'agent'
    assert m.collections == []
    assert m.contentRating == 'G'
    #assert m.countries == [<Country:35:USA>]
    assert [i.tag for i in m.directors] == ['John Lasseter', 'Joe Ranft']
    assert m.duration == 170859
    assert m.fields == []
    assert [i.tag for i in m.genres] == ['Animation', 'Family', 'Comedy', 'Sport', 'Adventure']
    assert m.guid == 'com.plexapp.agents.imdb://tt0317219?lang=en'
    assert m.initpath == '/library/metadata/2'
    assert m.key == '/library/metadata/2'
    assert str(m.lastViewedAt) == '__NA__'
    assert m.librarySectionID == '1'
    assert m.listType == 'video'
    # Assign 0 m.media
    med0 = m.media[0]
    assert str(m.originalTitle) == '__NA__'
    assert str(m.originallyAvailableAt.date()) == '2006-06-09'
    assert m.player is None
    assert str(m.playlistItemID) == '__NA__'
    assert str(m.primaryExtraKey) == '__NA__'
    #assert m.producers == [<Producer:130:Darla.K..Anderson>]
    assert m.rating == '7.4'
    assert m.ratingImage == 'rottentomatoes://image.rating.certified'
    assert m.ratingKey == 2
    assert [i.tag for i in m.roles] == ['Owen Wilson', 'Paul Newman', 'Bonnie Hunt', 'Larry the Cable Guy', 'Cheech Marin', 'Tony Shalhoub', 'Guido Quaroni', 'Jenifer Lewis', 'Paul Dooley', 'Michael Wallis', 'George Carlin', 'Katherine Helmond', 'John Ratzenberger', 'Michael Keaton', 'Joe Ranft', 'Richard Petty', 'Jeremy Piven', 'Bob Costas', 'Darrell Waltrip', 'Richard Kind', 'Edie McClurg', 'Humpy Wheeler', 'Tom Magliozzi', 'Ray Magliozzi', 'Lynda Petty', 'Andrew Stanton', 'Dale Earnhardt Jr.', 'Michael Schumacher', 'Jay Leno', 'Sarah Clark', 'Mike Nelson', 'Joe Ranft', 'Jonas Rivera', 'Lou Romano', 'Adrian Ochoa', 'E.J. Holowicki', 'Elissa Knight', 'Lindsey Collins', 'Larry Benton', 'Douglas Keever', 'Tom Hanks', 'Tim Allen', 'John Ratzenberger', 'Billy Crystal', 'John Goodman', 'John Ratzenberger', 'Dave Foley', 'John Ratzenberger', 'Vanness Wu']
    assert m.server.baseurl == 'http://138.68.157.5:32400'
    assert str(m.sessionKey) == '__NA__'
    assert m.studio == 'Walt Disney Pictures'
    assert m.summary == u"Lightning McQueen, a hotshot rookie race car driven to succeed, discovers that life is about the journey, not the finish line, when he finds himself unexpectedly detoured in the sleepy Route 66 town of Radiator Springs. On route across the country to the big Piston Cup Championship in California to compete against two seasoned pros, McQueen gets to know the town's offbeat characters."
    assert m.tagline == "Ahhh... it's got that new movie smell."
    assert m.thumb == '/library/metadata/2/thumb/1484690715'
    assert m.title == 'Cars'
    assert m.titleSort == 'Cars'
    assert m.transcodeSession is None
    assert m.type == 'movie'
    assert str(m.updatedAt.date()) == '2017-01-17'
    assert str(m.userRating) == '__NA__'
    assert m.username is None
    # Assign 0 m.videoStreams
    vid0 = m.videoStreams[0]
    assert m.viewCount == 0
    assert m.viewOffset == 0
    assert str(m.viewedAt) == '__NA__'
    assert [i.tag for i in m.writers] == ['Dan Fogelman', 'Joe Ranft', 'John Lasseter', 'Kiel Murray', 'Phil Lorin', 'Jorgen Klubien']
    assert m.year == 2006
    assert aud0.audioChannelLayout == '5.1'
    assert aud0.bitDepth is None
    assert aud0.bitrate == 388
    assert aud0.bitrateMode is None
    assert aud0.channels == 6
    assert aud0.codec == 'aac'
    assert aud0.codecID is None
    assert aud0.dialogNorm is None
    assert aud0.duration is None
    assert aud0.id == 10
    assert aud0.index == 1
    assert aud0.initpath == '/library/metadata/2'
    assert aud0.language is None
    assert aud0.languageCode is None
    #assert aud0.part == <MediaPart:2>
    assert aud0.samplingRate == 48000
    assert aud0.selected is True
    assert aud0.server.baseurl == 'http://138.68.157.5:32400'
    assert aud0.streamType == 2
    assert aud0.title is None
    assert aud0.type == 2
    assert med0.aspectRatio == 1.78
    assert med0.audioChannels == 6
    assert med0.audioCodec == 'aac'
    assert med0.bitrate == 1474
    assert med0.container == 'mp4'
    assert med0.duration == 170859
    assert med0.height == 720
    assert med0.id == 2
    assert med0.initpath == '/library/metadata/2'
    assert med0.optimizedForStreaming is False
    # Assign 0 med0.parts
    par0 = med0.parts[0]
    assert med0.server.baseurl == 'http://138.68.157.5:32400'
    assert med0.video == m
    assert med0.videoCodec == 'h264'
    assert med0.videoFrameRate == 'PAL'
    assert med0.videoResolution == '720'
    assert med0.width == 1280
    assert vid0.bitDepth == 8
    assert vid0.bitrate == 1086
    assert vid0.cabac is None
    assert vid0.chromaSubsampling == '4:2:0'
    assert vid0.codec == 'h264'
    assert vid0.codecID is None
    assert vid0.colorSpace is None
    assert vid0.duration is None
    assert vid0.frameRate == 25.0
    assert vid0.frameRateMode is None
    assert vid0.hasScallingMatrix is None
    assert vid0.height == 720
    assert vid0.id == 9
    assert vid0.index == 0
    assert vid0.initpath == '/library/metadata/2'
    assert vid0.language is None
    assert vid0.languageCode is None
    assert vid0.level == 31
    #assert vid0.part == <MediaPart:2>
    assert vid0.profile == 'main'
    assert vid0.refFrames == 1
    assert vid0.scanType is None
    assert vid0.selected is False
    assert vid0.server.baseurl == 'http://138.68.157.5:32400'
    assert vid0.streamType == 1
    assert vid0.title is None
    assert vid0.type == 1
    assert vid0.width == 1280
    assert par0.container == 'mp4'
    assert par0.duration == 170859
    assert par0.file == '/media/movies/cars/cars.mp4'
    assert par0.id == 2
    assert par0.initpath == '/library/metadata/2'
    assert par0.key == '/library/parts/2/1484679008/file.mp4'
    #assert par0.media == <Media:Cars>
    assert par0.server.baseurl == 'http://138.68.157.5:32400'
    assert par0.size == 31491130
    # Assign 0 par0.streams
    str0 = par0.streams[0]
    # Assign 1 par0.streams
    str1 = par0.streams[1]
    assert str0.bitDepth == 8
    assert str0.bitrate == 1086
    assert str0.cabac is None
    assert str0.chromaSubsampling == '4:2:0'
    assert str0.codec == 'h264'
    assert str0.codecID is None
    assert str0.colorSpace is None
    assert str0.duration is None
    assert str0.frameRate == 25.0
    assert str0.frameRateMode is None
    assert str0.hasScallingMatrix is None
    assert str0.height == 720
    assert str0.id == 9
    assert str0.index == 0
    assert str0.initpath == '/library/metadata/2'
    assert str0.language is None
    assert str0.languageCode is None
    assert str0.level == 31
    #assert str0.part == <MediaPart:2>
    assert str0.profile == 'main'
    assert str0.refFrames == 1
    assert str0.scanType is None
    assert str0.selected is False
    assert str0.server.baseurl == 'http://138.68.157.5:32400'
    assert str0.streamType == 1
    assert str0.title is None
    assert str0.type == 1
    assert str0.width == 1280
    assert str1.audioChannelLayout == '5.1'
    assert str1.bitDepth is None
    assert str1.bitrate == 388
    assert str1.bitrateMode is None
    assert str1.channels == 6
    assert str1.codec == 'aac'
    assert str1.codecID is None
    assert str1.dialogNorm is None
    assert str1.duration is None
    assert str1.id == 10
    assert str1.index == 1
    assert str1.initpath == '/library/metadata/2'
    assert str1.language is None
    assert str1.languageCode is None
    #assert str1.part == <MediaPart:2>
    assert str1.samplingRate == 48000
    assert str1.selected is True
    assert str1.server.baseurl == 'http://138.68.157.5:32400'
    assert str1.streamType == 2
    assert str1.title is None
    assert str1.type == 2



def test_video_Show(a_show):
    assert a_show.title == 'The 100'


def test_video_Show_attrs(a_show):
    m = a_show
    assert str(m.addedAt.date()) == '2017-01-17'
    assert '/library/metadata/12/art/' in m.art
    assert '/library/metadata/12/banner/' in m.banner
    assert m.childCount == 2
    assert m.contentRating == 'TV-14'
    assert m.duration == 2700000
    assert m.initpath == '/library/sections/2/all'
    # Since we access m.genres the show is forced to reload
    assert [i.tag for i in m.genres] == ['Drama', 'Science-Fiction', 'Suspense', 'Thriller']
    # So the initkey should have changed because of the reload
    assert m.initpath == '/library/metadata/12'
    assert m.index == '1'
    assert m.key == '/library/metadata/12'
    assert str(m.lastViewedAt.date()) == '2017-01-22'
    assert m.leafCount == 9
    assert m.listType == 'video'
    assert m.location == '/media/tvshows/the 100'
    assert str(m.originallyAvailableAt.date()) == '2014-03-19'
    assert m.rating == 8.1
    assert m.ratingKey == 12
    assert [i.tag for i in m.roles][:3] == ['Richard Harmon', 'Alycia Debnam-Carey', 'Lindsey Morgan']
    assert m.server.baseurl == 'http://138.68.157.5:32400'
    assert m.studio == 'The CW'
    assert m.summary == u"When nuclear Armageddon destroys civilization on Earth, the only survivors are those on the 12 international space stations in orbit at the time. Three generations later, the 4,000 survivors living on a space ark of linked stations see their resources dwindle and face draconian measures established to ensure humanity's future. Desperately looking for a solution, the ark's leaders send 100 juvenile prisoners back to the planet to test its habitability. Having always lived in space, the exiles find the planet fascinating and terrifying, but with the fate of the human race in their hands, they must forge a path into the unknown."
    assert '/library/metadata/12/theme/' in m.theme
    assert '/library/metadata/12/thumb/' in m.thumb
    assert m.title == 'The 100'
    assert m.titleSort == '100'
    assert m.type == 'show'
    assert str(m.updatedAt.date()) == '2017-01-22'
    assert m.viewCount == 1
    assert m.viewedLeafCount == 1
    assert m.year == 2014

def test_video_Show_location(pms):
    # This should be a part of test test_video_Show_attrs
    # But is excluded because of https://github.com/mjs7231/python-plexapi/issues/97
    s = pms.library.section('TV Shows').get('The 100')
    # This will require a reload since the xml from http://138.68.157.5:32400/library/sections/2/all
    # Does not contain a location
    assert s.location == '/media/tvshows/the 100'

def test_video_Show_reload(pms):
    s = pms.library.section('TV Shows').get('Game of Thrones')
    assert s.initpath == '/library/sections/2/all'
    s.reload()
    assert s.initpath == '/library/metadata/6'
    assert len(s.roles) > 3



def test_video_Show_episodes(a_show):
    inc_watched = a_show.episodes()
    ex_watched = a_show.episodes(watched=False)
    assert len(inc_watched) == 9
    assert len(ex_watched) == 8

def test_video_Show_download(tmpdir, a_show):
    f = a_show.download(savepath=str(tmpdir))
    assert len(f) == 9


def _test_video_Season_download(tmpdir, a_show):
    sn = a_show.season('Season 1')

    f = sn.download(savepath=str(tmpdir))
    assert len(f) == 8

def test_video_Episode_download(tmpdir, a_episode):
    f = a_episode.download(savepath=str(tmpdir))
    assert len(f) == 1

    with_sceen_size = a_episode.download(savepath=str(tmpdir), **{'videoResolution': '500x300'})
    assert len(with_sceen_size) == 1




def test_video_Show_thumbUrl(a_show):
    assert 'http://138.68.157.5:32400/library/metadata/12/thumb/' in a_show.thumbUrl

@pytest.mark.xfail
def test_video_Show_analyze(a_show):
    show = a_show.analyze()  # this isnt possble.. should it even be available?

def test_video_Show_markWatched(a_tv_section):
    show = a_tv_section.get("Marvel's Daredevil")
    show.markWatched()
    assert a_tv_section.get("Marvel's Daredevil").isWatched


def test_video_Show_markUnwatched(a_tv_section):
    show = a_tv_section.get("Marvel's Daredevil")
    show.markUnwatched()
    assert not a_tv_section.get("Marvel's Daredevil").isWatched


def test_video_Show_refresh(a_tv_section):
    show = a_tv_section.get("Marvel's Daredevil")
    show.refresh()


def test_video_Show_get(a_show):
    assert a_show.get('Pilot').title == 'Pilot'


def test_video_Show_isWatched(a_show):
    assert not a_show.isWatched


@pytest.mark.xfail
def test_video_Show_section(a_show):  # BROKEN!
    show = a_show.section()


def test_video_Episode(a_show):
    pilot = a_show.episode('Pilot')
    assert pilot == a_show.episode(season=1, episode=1)

def test_video_Episode_analyze(a_tv_section):
    ep = a_tv_section.get("Marvel's Daredevil").episode(season=1, episode=1)
    ep.analyze()


def test_video_Episode_attrs(a_episode):
    ep = a_episode
    assert str(ep.addedAt.date()) == '2017-01-17'
    assert ep.contentRating == 'TV-14'
    assert [i.tag for i in ep.directors] == ['Bharat Nalluri']
    assert ep.duration == 170859
    assert ep.grandparentTitle == 'The 100'
    assert ep.index == 1
    assert ep.initpath == '/library/metadata/12/allLeaves'
    assert ep.key == '/library/metadata/14'
    assert ep.listType == 'video'
    # Assign 0 ep.media
    med0 = ep.media[0]
    assert str(ep.originallyAvailableAt.date()) == '2014-03-19'
    assert ep.parentIndex == '1'
    assert ep.parentKey == '/library/metadata/13'
    assert ep.parentRatingKey == 13
    assert '/library/metadata/13/thumb/' in ep.parentThumb
    #assert ep.parentThumb == '/library/metadata/13/thumb/1485096623'
    assert ep.player is None
    assert ep.rating == 7.4
    assert ep.ratingKey == 14
    assert ep.server.baseurl == 'http://138.68.157.5:32400'
    assert ep.summary == u'Ninety-seven years ago, nuclear Armageddon decimated planet Earth, destroying civilization. The only survivors were the 400 inhabitants of 12 international space stations that were in orbit at the time. Three generations have been born in space, the survivors now number 4,000, and resources are running out on their dying "Ark." Among the 100 young exiles are Clarke, the bright teenage daughter of the Ark’s chief medical officer; the daredevil Finn; the brother/sister duo of Bellamy and Octavia, whose illegal sibling status has always led them to flaunt the rules, the lighthearted Jasper and the resourceful Monty. Technologically blind to what’s happening on the planet below them, the Ark’s leaders — Clarke’s widowed mother, Abby; Chancellor Jaha; and his shadowy second in command, Kane — are faced with difficult decisions about life, death and the continued existence of the human race.'
    assert ep.thumb == '/library/metadata/14/thumb/1485115318'
    assert ep.title == 'Pilot'
    assert ep.titleSort == 'Pilot'
    assert ep.transcodeSession is None
    assert ep.type == 'episode'
    assert str(ep.updatedAt.date()) == '2017-01-22'
    assert ep.username is None
    assert ep.viewCount == 1
    assert ep.viewOffset == 0
    assert [i.tag for i in ep.writers] == ['Jason Rothenberg']
    assert ep.year == 2014
    assert med0.aspectRatio == 1.78
    assert med0.audioChannels == 6
    assert med0.audioCodec == 'aac'
    assert med0.bitrate == 1474
    assert med0.container == 'mp4'
    assert med0.duration == 170859
    assert med0.height == 720
    assert med0.id == 12
    assert med0.initpath == '/library/metadata/12/allLeaves'
    assert med0.optimizedForStreaming is False
    # Assign 0 med0.parts
    par0 = med0.parts[0]
    assert med0.server.baseurl == 'http://138.68.157.5:32400'
    #assert med0.video == <Episode:14:The 100:S1:E1:Pilot>
    assert med0.videoCodec == 'h264'
    assert med0.videoFrameRate == 'PAL'
    assert med0.videoResolution == '720'
    assert med0.width == 1280
    assert par0.container == 'mp4'
    assert par0.duration == 170859
    assert par0.file == '/media/tvshows/the 100/season 1/the.100.s01e01.mp4'
    assert par0.id == 12
    assert par0.initpath == '/library/metadata/12/allLeaves'
    assert par0.key == '/library/parts/12/1484679008/file.mp4'
    #assert par0.media == <Media:Pilot>
    assert par0.server.baseurl == 'http://138.68.157.5:32400'
    assert par0.size == 31491130


def test_video_Season(a_show):
    seasons = a_show.seasons()
    assert len(seasons) == 2
    assert ['Season 1', 'Season 2'] == [s.title for s in seasons]
    assert a_show.season('Season 1') == seasons[0]


def test_video_Season_attrs(a_show):
    m = a_show.season('Season 1')
    assert str(m.addedAt.date()) == '2017-01-17'
    assert m.index == 1
    assert m.initpath == '/library/metadata/12/children'
    assert m.key == '/library/metadata/13'
    assert str(m.lastViewedAt.date()) == '2017-01-22'
    assert m.leafCount == 8
    assert m.listType == 'video'
    assert m.parentKey == '/library/metadata/12'
    assert m.parentRatingKey == 12
    assert m.parentTitle == 'The 100'
    assert m.ratingKey == 13
    assert m.server.baseurl == 'http://138.68.157.5:32400'
    assert m.summary == ''
    assert '/library/metadata/13/thumb/' in m.thumb
    #assert m.thumb == '/library/metadata/13/thumb/1485096623'
    assert m.title == 'Season 1'
    assert m.titleSort == 'Season 1'
    assert m.type == 'season'
    assert str(m.updatedAt.date()) == '2017-01-22'
    assert m.viewCount == 1
    assert m.viewedLeafCount == 1


def test_video_Season_show(a_show):
    sn = a_show.seasons()[0]
    season_by_name = a_show.season('Season 1')
    assert a_show.ratingKey == sn.parentRatingKey and season_by_name.parentRatingKey
    assert sn.ratingKey == season_by_name.ratingKey


def test_video_Season_watched(a_tv_section):
    show = a_tv_section.get("Marvel's Daredevil")
    sn = show.season(1)
    sne = show.season('Season 1')
    assert sn == sne
    sn.markWatched()
    assert sn.isWatched


def test_video_Season_unwatched(a_tv_section):
    sn = a_tv_section.get("Marvel's Daredevil").season(1)
    sn.markUnwatched()
    assert not sn.isWatched


def test_video_Season_get(a_show):
    ep = a_show.season(1).get('Pilot')
    assert ep.title == 'Pilot'


def test_video_Season_episode(a_show):
    ep = a_show.season(1).get('Pilot')
    assert ep.title == 'Pilot'


def test_video_Season_episodes(a_show):
    sn_eps = a_show.season(2).episodes()
    assert len(sn_eps) == 1
