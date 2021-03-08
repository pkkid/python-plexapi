# -*- coding: utf-8 -*-
import os
from datetime import datetime
from time import sleep
from urllib.parse import quote_plus

import pytest
from plexapi.exceptions import BadRequest, NotFound

from . import conftest as utils
from . import test_mixins


def test_video_Movie(movies, movie):
    movie2 = movies.get(movie.title)
    assert movie2.title == movie.title


def test_video_Movie_attributeerror(movie):
    with pytest.raises(AttributeError):
        movie.asshat


def test_video_ne(movies):
    assert (
        len(
            movies.fetchItems(
                "/library/sections/%s/all" % movies.key, title__ne="Sintel"
            )
        )
        == 3
    )


def test_video_Movie_delete(movie, patched_http_call):
    movie.delete()


def test_video_Movie_merge(movie, patched_http_call):
    movie.merge(1337)


def test_video_Movie_mixins_images(movie):
    test_mixins.edit_art(movie)
    test_mixins.edit_poster(movie)


def test_video_Movie_mixins_tags(movie):
    test_mixins.edit_collection(movie)
    test_mixins.edit_country(movie)
    test_mixins.edit_director(movie)
    test_mixins.edit_genre(movie)
    test_mixins.edit_label(movie)
    test_mixins.edit_producer(movie)
    test_mixins.edit_writer(movie)


def test_video_Movie_getStreamURL(movie, account):
    key = movie.ratingKey
    assert movie.getStreamURL() == (
        "{0}/video/:/transcode/universal/start.m3u8?"
        "X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&"
        "offset=0&path=%2Flibrary%2Fmetadata%2F{1}&X-Plex-Token={2}").format(
        utils.SERVER_BASEURL, key, account.authenticationToken
    )  # noqa
    assert movie.getStreamURL(
        videoResolution="800x600"
    ) == ("{0}/video/:/transcode/universal/start.m3u8?"
        "X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&"
        "offset=0&path=%2Flibrary%2Fmetadata%2F{1}&videoResolution=800x600&X-Plex-Token={2}").format(
        utils.SERVER_BASEURL, key, account.authenticationToken
    )  # noqa


def test_video_Movie_isFullObject_and_reload(plex):
    movie = plex.library.section("Movies").get("Sita Sings the Blues")
    assert movie.isFullObject() is False
    movie.reload(checkFiles=False)
    assert movie.isFullObject() is False
    movie.reload()
    assert movie.isFullObject() is True
    movie_via_search = plex.library.search(movie.title)[0]
    assert movie_via_search.isFullObject() is False
    movie_via_search.reload()
    assert movie_via_search.isFullObject() is True
    movie_via_section_search = plex.library.section("Movies").search(movie.title)[0]
    assert movie_via_section_search.isFullObject() is False
    movie_via_section_search.reload()
    assert movie_via_section_search.isFullObject() is True
    # If the verify that the object has been reloaded. xml from search only returns 3 actors.
    assert len(movie_via_section_search.roles) >= 3


def test_video_Movie_isPartialObject(movie):
    assert movie.isPartialObject()


def test_video_Movie_delete_part(movie, mocker):
    # we need to reload this as there is a bug in part.delete
    # See https://github.com/pkkid/python-plexapi/issues/201
    m = movie.reload()
    for media in m.media:
        with utils.callable_http_patch():
            media.delete()


def test_video_Movie_iterParts(movie):
    assert len(list(movie.iterParts())) >= 1


def test_video_Movie_download(monkeydownload, tmpdir, movie):
    filepaths1 = movie.download(savepath=str(tmpdir))
    assert len(filepaths1) >= 1
    filepaths2 = movie.download(savepath=str(tmpdir), videoResolution="500x300")
    assert len(filepaths2) >= 1


def test_video_Movie_subtitlestreams(movie):
    assert not movie.subtitleStreams()


def test_video_Episode_subtitlestreams(episode):
    assert not episode.subtitleStreams()


def test_video_Movie_upload_select_remove_subtitle(movie, subtitle):

    filepath = os.path.realpath(subtitle.name)

    movie.uploadSubtitles(filepath)
    movie.reload()
    subtitles = [sub.title for sub in movie.subtitleStreams()]
    subname = subtitle.name.rsplit(".", 1)[0]
    assert subname in subtitles

    subtitleSelection = movie.subtitleStreams()[0]
    parts = list(movie.iterParts())
    parts[0].setDefaultSubtitleStream(subtitleSelection)
    movie.reload()

    subtitleSelection = movie.subtitleStreams()[0]
    assert subtitleSelection.selected

    movie.removeSubtitles(streamTitle=subname)
    movie.reload()
    subtitles = [sub.title for sub in movie.subtitleStreams()]
    assert subname not in subtitles

    try:
        os.remove(filepath)
    except:
        pass


def test_video_Movie_attrs(movies):
    movie = movies.get("Sita Sings the Blues")
    assert len(movie.locations) == 1
    assert len(movie.locations[0]) >= 10
    assert utils.is_datetime(movie.addedAt)
    if movie.art:
        assert utils.is_art(movie.art)
    assert float(movie.rating) >= 6.4
    assert movie.ratingImage == 'rottentomatoes://image.rating.ripe'
    assert movie.audienceRating >= 8.5
    assert movie.audienceRatingImage == 'rottentomatoes://image.rating.upright'
    movie.reload()  # RELOAD
    assert movie.chapterSource is None
    assert not movie.collections
    assert movie.contentRating in utils.CONTENTRATINGS
    if movie.countries:
        assert "United States of America" in [i.tag for i in movie.countries]
    if movie.producers:
        assert "Nina Paley" in [i.tag for i in movie.producers]
    if movie.directors:
        assert "Nina Paley" in [i.tag for i in movie.directors]
    if movie.roles:
        assert "Reena Shah" in [i.tag for i in movie.roles]
    if movie.writers:
        assert "Nina Paley" in [i.tag for i in movie.writers]
    assert movie.duration >= 160000
    assert not movie.fields
    assert movie.posters()
    assert "Animation" in [i.tag for i in movie.genres]
    assert "imdb://tt1172203" in [i.id for i in movie.guids]
    assert movie.guid == "plex://movie/5d776846880197001ec967c6"
    assert utils.is_metadata(movie._initpath)
    assert utils.is_metadata(movie.key)
    assert utils.is_datetime(movie.lastViewedAt)
    assert int(movie.librarySectionID) >= 1
    assert movie.listType == "video"
    assert movie.originalTitle is None
    assert utils.is_datetime(movie.originallyAvailableAt)
    assert movie.playlistItemID is None
    if movie.primaryExtraKey:
        assert utils.is_metadata(movie.primaryExtraKey)
    assert movie.ratingKey >= 1
    assert movie._server._baseurl == utils.SERVER_BASEURL
    assert movie.sessionKey is None
    assert movie.studio == "Nina Paley"
    assert utils.is_string(movie.summary, gte=100)
    assert movie.tagline == "The Greatest Break-Up Story Ever Told"
    if movie.thumb:
        assert utils.is_thumb(movie.thumb)
    assert movie.title == "Sita Sings the Blues"
    assert movie.titleSort == "Sita Sings the Blues"
    assert not movie.transcodeSessions
    assert movie.type == "movie"
    assert movie.updatedAt > datetime(2017, 1, 1)
    assert movie.userRating is None
    assert movie.viewCount == 0
    assert utils.is_int(movie.viewOffset, gte=0)
    assert movie.viewedAt is None
    assert movie.year == 2008
    # Audio
    audio = movie.media[0].parts[0].audioStreams()[0]
    if audio.audioChannelLayout:
        assert audio.audioChannelLayout in utils.AUDIOLAYOUTS
    assert audio.bitDepth is None
    assert utils.is_int(audio.bitrate)
    assert audio.bitrateMode is None
    assert audio.channels in utils.AUDIOCHANNELS
    assert audio.codec in utils.CODECS
    assert audio.default is True
    assert audio.displayTitle == "Unknown (AAC Stereo)"
    assert audio.duration is None
    assert audio.extendedDisplayTitle == "Unknown (AAC Stereo)"
    assert audio.id >= 1
    assert audio.index == 1
    assert utils.is_metadata(audio._initpath)
    assert audio.language is None
    assert audio.languageCode is None
    assert audio.profile == "lc"
    assert audio.requiredBandwidths is None or audio.requiredBandwidths
    assert audio.samplingRate == 44100
    assert audio.selected is True
    assert audio.streamIdentifier == 2
    assert audio.streamType == 2
    assert audio._server._baseurl == utils.SERVER_BASEURL
    assert audio.title is None
    assert audio.type == 2
    with pytest.raises(AttributeError):
        assert audio.albumGain is None  # Check track only attributes are not available
    # Media
    media = movie.media[0]
    assert media.aspectRatio >= 1.3
    assert media.audioChannels in utils.AUDIOCHANNELS
    assert media.audioCodec in utils.CODECS
    assert media.audioProfile == "lc"
    assert utils.is_int(media.bitrate)
    assert media.container in utils.CONTAINERS
    assert utils.is_int(media.duration, gte=160000)
    assert utils.is_int(media.height)
    assert utils.is_int(media.id)
    assert utils.is_metadata(media._initpath)
    assert media.has64bitOffsets is False
    assert media.optimizedForStreaming in [None, False, True]
    assert media.proxyType is None
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.target is None
    assert media.title is None
    assert media.videoCodec in utils.CODECS
    assert media.videoFrameRate in utils.FRAMERATES
    assert media.videoProfile == "main"
    assert media.videoResolution in utils.RESOLUTIONS
    assert utils.is_int(media.width, gte=200)
    with pytest.raises(AttributeError):
        assert media.aperture is None  # Check photo only attributes are not available
    # Video
    video = movie.media[0].parts[0].videoStreams()[0]
    assert video.anamorphic is None
    assert video.bitDepth in (
        8,
        None,
    )  # Different versions of Plex Server return different values
    assert utils.is_int(video.bitrate)
    assert video.cabac is None
    assert video.chromaLocation == "left"
    assert video.chromaSubsampling in ("4:2:0", None)
    assert video.codec in utils.CODECS
    assert video.codecID is None
    assert utils.is_int(video.codedHeight, gte=1080)
    assert utils.is_int(video.codedWidth, gte=1920)
    assert video.colorPrimaries is None
    assert video.colorRange is None
    assert video.colorSpace is None
    assert video.colorTrc is None
    assert video.default is True
    assert video.displayTitle == "1080p (H.264)"
    assert video.DOVIBLCompatID is None
    assert video.DOVIBLPresent is None
    assert video.DOVIELPresent is None
    assert video.DOVILevel is None
    assert video.DOVIPresent is None
    assert video.DOVIProfile is None
    assert video.DOVIRPUPresent is None
    assert video.DOVIVersion is None
    assert video.duration is None
    assert video.extendedDisplayTitle == "1080p (H.264)"
    assert utils.is_float(video.frameRate, gte=20.0)
    assert video.frameRateMode is None
    assert video.hasScallingMatrix is None
    assert utils.is_int(video.height, gte=250)
    assert utils.is_int(video.id)
    assert utils.is_int(video.index, gte=0)
    assert utils.is_metadata(video._initpath)
    assert video.language is None
    assert video.languageCode is None
    assert utils.is_int(video.level)
    assert video.profile in utils.PROFILES
    assert video.pixelAspectRatio is None
    assert video.pixelFormat is None
    assert utils.is_int(video.refFrames)
    assert video.requiredBandwidths is None or video.requiredBandwidths
    assert video.scanType in ("progressive", None)
    assert video.selected is False
    assert video.streamType == 1
    assert video.streamIdentifier == 1
    assert video._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(video.streamType)
    assert video.title is None
    assert video.type == 1
    assert utils.is_int(video.width, gte=400)
    # Part
    part = media.parts[0]
    assert part.accessible
    assert part.audioProfile == "lc"
    assert part.container in utils.CONTAINERS
    assert part.decision is None
    assert part.deepAnalysisVersion is None or utils.is_int(part.deepAnalysisVersion)
    assert utils.is_int(part.duration, gte=160000)
    assert part.exists
    assert len(part.file) >= 10
    assert part.has64bitOffsets is False
    assert part.hasThumbnail is None
    assert utils.is_int(part.id)
    assert part.indexes is None
    assert utils.is_metadata(part._initpath)
    assert len(part.key) >= 10
    assert part.optimizedForStreaming is True
    assert part.packetLength is None
    assert part.requiredBandwidths is None or part.requiredBandwidths
    assert utils.is_int(part.size, gte=1000000)
    assert part.syncItemId is None
    assert part.syncState is None
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert part.videoProfile == "main"
    # Stream 1
    stream1 = part.streams[0]
    assert stream1.bitDepth in (8, None)
    assert utils.is_int(stream1.bitrate)
    assert stream1.cabac is None
    assert stream1.chromaSubsampling in ("4:2:0", None)
    assert stream1.codec in utils.CODECS
    assert stream1.colorSpace is None
    assert stream1.duration is None
    assert utils.is_float(stream1.frameRate, gte=20.0)
    assert stream1.frameRateMode is None
    assert stream1.hasScallingMatrix is None
    assert utils.is_int(stream1.height, gte=250)
    assert utils.is_int(stream1.id)
    assert utils.is_int(stream1.index, gte=0)
    assert utils.is_metadata(stream1._initpath)
    assert stream1.language is None
    assert stream1.languageCode is None
    assert utils.is_int(stream1.level)
    assert stream1.profile in utils.PROFILES
    assert utils.is_int(stream1.refFrames)
    assert stream1.scanType in ("progressive", None)
    assert stream1.selected is False
    assert stream1._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(stream1.streamType)
    assert stream1.title is None
    assert stream1.type == 1
    assert utils.is_int(stream1.width, gte=400)
    # Stream 2
    stream2 = part.streams[1]
    if stream2.audioChannelLayout:
        assert stream2.audioChannelLayout in utils.AUDIOLAYOUTS
    assert stream2.bitDepth is None
    assert utils.is_int(stream2.bitrate)
    assert stream2.bitrateMode is None
    assert stream2.channels in utils.AUDIOCHANNELS
    assert stream2.codec in utils.CODECS
    assert stream2.duration is None
    assert utils.is_int(stream2.id)
    assert utils.is_int(stream2.index)
    assert utils.is_metadata(stream2._initpath)
    assert stream2.language is None
    assert stream2.languageCode is None
    assert utils.is_int(stream2.samplingRate)
    assert stream2.selected is True
    assert stream2._server._baseurl == utils.SERVER_BASEURL
    assert stream2.streamType == 2
    assert stream2.title is None
    assert stream2.type == 2


def test_video_Movie_history(movie):
    movie.markWatched()
    history = movie.history()
    assert len(history)
    movie.markUnwatched()


def test_video_Movie_match(movies):
    sectionAgent = movies.agent
    sectionAgents = [agent.identifier for agent in movies.agents() if agent.shortIdentifier != 'none']
    sectionAgents.remove(sectionAgent)
    altAgent = sectionAgents[0]

    movie = movies.all()[0]
    title = movie.title
    year = str(movie.year)
    titleUrlEncode = quote_plus(title)

    def parse_params(key):
        params = key.split('?', 1)[1]
        params = params.split("&")
        return {x.split("=")[0]: x.split("=")[1] for x in params}

    results = movie.matches(title="", year="")
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('title') == ""
        assert parsedParams.get('year') == ""
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title=title, year="", agent=sectionAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('title') == titleUrlEncode
        assert parsedParams.get('year') == ""
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title=title, agent=sectionAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('title') == titleUrlEncode
        assert parsedParams.get('year') == year
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title="", year="")
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title="", year="", agent=altAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('agent') == altAgent
    else:
        assert len(results) == 0

    results = movie.matches(agent=altAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('agent') == altAgent
    else:
        assert len(results) == 0

    results = movie.matches()
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
    else:
        assert len(results) == 0


def test_video_Movie_hubs(movies):
    movie = movies.get('Big Buck Bunny')
    hubs = movie.hubs()
    assert len(hubs)
    hub = hubs[0]
    assert hub.context == "hub.movie.similar"
    assert utils.is_metadata(hub.hubKey)
    assert hub.hubIdentifier == "movie.similar"
    assert len(hub.items) == hub.size
    assert utils.is_metadata(hub.key)
    assert hub.more is False
    assert hub.size == 1
    assert hub.style in (None, "shelf")
    assert hub.title == "Related Movies"
    assert hub.type == "movie"
    assert len(hub) == hub.size
    # Force hub reload
    hub.more = True
    hub.reload()
    assert len(hub.items) == hub.size
    assert hub.more is False
    assert hub.size == 1


def test_video_Show(show):
    assert show.title == "Game of Thrones"


def test_video_Episode_updateProgress(episode, patched_http_call):
    episode.updateProgress(10 * 60 * 1000)  # 10 minutes.


def test_video_Episode_updateTimeline(episode, patched_http_call):
    episode.updateTimeline(
        10 * 60 * 1000, state="playing", duration=episode.duration
    )  # 10 minutes.


def test_video_Episode_stop(episode, mocker, patched_http_call):
    mocker.patch.object(
        episode, "session", return_value=list(mocker.MagicMock(id="hello"))
    )
    episode.stop(reason="It's past bedtime!")


def test_video_Show_attrs(show):
    assert utils.is_datetime(show.addedAt)
    if show.art:
        assert utils.is_art(show.art)
    if show.banner:
        assert utils.is_banner(show.banner)
    assert utils.is_int(show.childCount)
    assert show.contentRating in utils.CONTENTRATINGS
    assert utils.is_int(show.duration, gte=1600000)
    assert utils.is_section(show._initpath)
    # Check reloading the show loads the full list of genres
    assert not {"Adventure", "Drama"} - {i.tag for i in show.genres}
    show.reload()
    assert show.audienceRating is None  # TODO: Change when updating test to the Plex TV agent
    assert show.audienceRatingImage is None  # TODO: Change when updating test to the Plex TV agent
    assert show.autoDeletionItemPolicyUnwatchedLibrary == 0
    assert show.autoDeletionItemPolicyWatchedLibrary == 0
    assert show.episodeSort == -1
    assert show.flattenSeasons == -1
    assert sorted([i.tag for i in show.genres]) == ["Adventure", "Drama", "Fantasy"]
    assert show.guids == []  # TODO: Change when updating test to the Plex TV agent
    # So the initkey should have changed because of the reload
    assert utils.is_metadata(show._initpath)
    assert utils.is_int(show.index)
    assert utils.is_metadata(show.key)
    assert show.languageOverride is None
    assert utils.is_datetime(show.lastViewedAt)
    assert utils.is_int(show.leafCount)
    assert show.listType == "video"
    assert len(show.locations) == 1
    assert len(show.locations[0]) >= 10
    assert show.network is None
    assert utils.is_datetime(show.originallyAvailableAt)
    assert show.originalTitle is None
    assert show.rating >= 8.0
    assert utils.is_int(show.ratingKey)
    assert sorted([i.tag for i in show.roles])[:4] == [
        "Aidan Gillen",
        "Aimee Richardson",
        "Alexander Siddig",
        "Alfie Allen",
    ]  # noqa
    assert sorted([i.tag for i in show.actors])[:4] == [
        "Aidan Gillen",
        "Aimee Richardson",
        "Alexander Siddig",
        "Alfie Allen",
    ]  # noqa
    assert show._server._baseurl == utils.SERVER_BASEURL
    assert show.showOrdering in (None, 'aired')
    assert show.studio == "HBO"
    assert utils.is_string(show.summary, gte=100)
    assert show.tagline is None
    assert utils.is_metadata(show.theme, contains="/theme/")
    if show.thumb:
        assert utils.is_thumb(show.thumb)
    assert show.title == "Game of Thrones"
    assert show.titleSort == "Game of Thrones"
    assert show.type == "show"
    assert show.useOriginalTitle == -1
    assert show.userRating is None
    assert utils.is_datetime(show.updatedAt)
    assert utils.is_int(show.viewCount, gte=0)
    assert utils.is_int(show.viewedLeafCount, gte=0)
    assert show.year in (2011, 2010)
    assert show.url(None) is None


def test_video_Show_history(show):
    show.markWatched()
    history = show.history()
    assert len(history)
    show.markUnwatched()


def test_video_Show_watched(tvshows):
    show = tvshows.get("The 100")
    episode = show.episodes()[0]
    episode.markWatched()
    watched = show.watched()
    assert len(watched) == 1 and watched[0].title == "Pilot"
    episode.markUnwatched()


def test_video_Show_unwatched(tvshows):
    show = tvshows.get("The 100")
    episodes = show.episodes()
    episode = episodes[0]
    episode.markWatched()
    unwatched = show.unwatched()
    assert len(unwatched) == len(episodes) - 1
    episode.markUnwatched()


def test_video_Show_settings(show):
    preferences = show.preferences()
    assert len(preferences) >= 1


def test_video_Show_editAdvanced_default(show):
    show.editAdvanced(showOrdering='absolute')
    show.reload()
    for pref in show.preferences():
        if pref.id == 'showOrdering':
            assert pref.value == 'absolute'

    show.editAdvanced(flattenSeasons=1)
    show.reload()
    for pref in show.preferences():
        if pref.id == 'flattenSeasons':
            assert pref.value == 1

    show.defaultAdvanced()
    show.reload()
    for pref in show.preferences():
        assert pref.value == pref.default


def test_video_Show_reload(plex):
    show = plex.library.section("TV Shows").get("Game of Thrones")
    assert utils.is_metadata(show._initpath, prefix="/library/sections/")
    assert len(show.roles) == 3
    show.reload()
    assert utils.is_metadata(show._initpath, prefix="/library/metadata/")
    assert len(show.roles) > 3


def test_video_Show_episodes(tvshows):
    show = tvshows.get("The 100")
    episodes = show.episodes()
    episodes[0].markWatched()
    unwatched = show.episodes(viewCount=0)
    assert len(unwatched) == len(episodes) - 1


def test_video_Show_download(monkeydownload, tmpdir, show):
    episodes = show.episodes()
    filepaths = show.download(savepath=str(tmpdir))
    assert len(filepaths) == len(episodes)


def test_video_Season_download(monkeydownload, tmpdir, show):
    season = show.season("Season 1")
    filepaths = season.download(savepath=str(tmpdir))
    assert len(filepaths) >= 4


def test_video_Episode_download(monkeydownload, tmpdir, episode):
    f = episode.download(savepath=str(tmpdir))
    assert len(f) == 1
    with_sceen_size = episode.download(
        savepath=str(tmpdir), **{"videoResolution": "500x300"}
    )
    assert len(with_sceen_size) == 1


# Analyze seems to fail intermittently
@pytest.mark.xfail
def test_video_Show_analyze(show):
    show = show.analyze()


def test_video_Show_markWatched(show):
    show.markWatched()
    assert show.isWatched


def test_video_Show_markUnwatched(show):
    show.markUnwatched()
    assert not show.isWatched


def test_video_Show_refresh(show):
    show.refresh()


def test_video_Show_get(show):
    assert show.get("Winter Is Coming").title == "Winter Is Coming"


def test_video_Show_isWatched(show):
    assert not show.isWatched


def test_video_Show_section(show):
    section = show.section()
    assert section.title == "TV Shows"


def test_video_Show_mixins_images(show):
    test_mixins.edit_art(show)
    test_mixins.edit_banner(show)
    test_mixins.edit_poster(show)
    test_mixins.attr_artUrl(show)
    test_mixins.attr_bannerUrl(show)
    test_mixins.attr_posterUrl(show)


def test_video_Show_mixins_tags(show):
    test_mixins.edit_collection(show)
    test_mixins.edit_genre(show)
    test_mixins.edit_label(show)


def test_video_Episode(show):
    episode = show.episode("Winter Is Coming")
    assert episode == show.episode(season=1, episode=1)
    with pytest.raises(BadRequest):
        show.episode()
    with pytest.raises(NotFound):
        show.episode(season=1337, episode=1337)


def test_video_Episode_history(episode):
    episode.markWatched()
    history = episode.history()
    assert len(history)
    episode.markUnwatched()


def test_video_Episode_hidden_season(episode):
    assert episode.skipParent is False
    assert episode.parentRatingKey
    assert episode.parentKey
    assert episode.seasonNumber
    show = episode.show()
    show.editAdvanced(flattenSeasons=1)
    episode.reload()
    assert episode.skipParent is True
    assert episode.parentRatingKey
    assert episode.parentKey
    assert episode.seasonNumber
    show.defaultAdvanced()


def test_video_Episode_parent_weakref(show):
    season = show.season(season=1)
    episode = season.episode(episode=1)
    assert episode._parent is not None
    assert episode._parent() == season
    episode = show.season(season=1).episode(episode=1)
    assert episode._parent is not None
    assert episode._parent() is None


# Analyze seems to fail intermittently
@pytest.mark.xfail
def test_video_Episode_analyze(tvshows):
    episode = tvshows.get("Game of Thrones").episode(season=1, episode=1)
    episode.analyze()


def test_video_Episode_attrs(episode):
    assert utils.is_datetime(episode.addedAt)
    if episode.art:
        assert utils.is_art(episode.art)
    assert episode.audienceRating is None  # TODO: Change when updating test to the Plex TV agent
    assert episode.audienceRatingImage is None  # TODO: Change when updating test to the Plex TV agent
    assert episode.contentRating in utils.CONTENTRATINGS
    if len(episode.directors):
        assert [i.tag for i in episode.directors] == ["Tim Van Patten"]
    assert utils.is_int(episode.duration, gte=120000)
    if episode.grandparentArt:
        assert utils.is_art(episode.grandparentArt)
    if episode.grandparentThumb:
        assert utils.is_thumb(episode.grandparentThumb)
    assert episode.grandparentTitle == "Game of Thrones"
    assert episode.guids == []  # TODO: Change when updating test to the Plex TV agent
    assert episode.index == 1
    assert utils.is_metadata(episode._initpath)
    assert utils.is_metadata(episode.key)
    assert episode.listType == "video"
    assert utils.is_datetime(episode.originallyAvailableAt)
    assert utils.is_int(episode.parentIndex)
    assert utils.is_metadata(episode.parentKey)
    assert utils.is_int(episode.parentRatingKey)
    if episode.parentThumb:
        assert utils.is_thumb(episode.parentThumb)
    assert episode.rating >= 7.7
    assert utils.is_int(episode.ratingKey)
    assert episode._server._baseurl == utils.SERVER_BASEURL
    assert episode.skipParent is False
    assert utils.is_string(episode.summary, gte=100)
    if episode.thumb:
        assert utils.is_thumb(episode.thumb)
    assert episode.title == "Winter Is Coming"
    assert episode.titleSort == "Winter Is Coming"
    assert not episode.transcodeSessions
    assert episode.type == "episode"
    assert utils.is_datetime(episode.updatedAt)
    assert utils.is_int(episode.viewCount, gte=0)
    assert episode.viewOffset == 0
    assert sorted([i.tag for i in episode.writers]) == sorted(
        ["David Benioff", "D. B. Weiss"]
    )
    assert episode.year == 2011
    assert episode.isWatched in [True, False]
    assert len(episode.locations) == 1
    assert len(episode.locations[0]) >= 10
    # Media
    media = episode.media[0]
    assert media.aspectRatio == 1.78
    assert media.audioChannels in utils.AUDIOCHANNELS
    assert media.audioCodec in utils.CODECS
    assert utils.is_int(media.bitrate)
    assert media.container in utils.CONTAINERS
    assert utils.is_int(media.duration, gte=150000)
    assert utils.is_int(media.height, gte=200)
    assert utils.is_int(media.id)
    assert utils.is_metadata(media._initpath)
    if media.optimizedForStreaming:
        assert isinstance(media.optimizedForStreaming, bool)
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.videoCodec in utils.CODECS
    assert media.videoFrameRate in utils.FRAMERATES
    assert media.videoResolution in utils.RESOLUTIONS
    assert utils.is_int(media.width, gte=400)
    # Part
    part = media.parts[0]
    assert part.container in utils.CONTAINERS
    assert utils.is_int(part.duration, gte=150000)
    assert len(part.file) >= 10
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert len(part.key) >= 10
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(part.size, gte=18184197)
    assert part.exists
    assert part.accessible


def test_video_Episode_mixins_images(episode):
    #test_mixins.edit_art(episode)  # Uploading episode artwork is broken in Plex
    test_mixins.edit_poster(episode)
    test_mixins.attr_artUrl(episode)
    test_mixins.attr_posterUrl(episode)


def test_video_Episode_mixins_tags(episode):
    test_mixins.edit_director(episode)
    test_mixins.edit_writer(episode)


def test_video_Season(show):
    seasons = show.seasons()
    assert len(seasons) == 2
    assert ["Season 1", "Season 2"] == [s.title for s in seasons[:2]]
    assert show.season("Season 1") == seasons[0]


def test_video_Season_history(show):
    season = show.season("Season 1")
    season.markWatched()
    history = season.history()
    assert len(history)
    season.markUnwatched()


def test_video_Season_watched(tvshows):
    season = tvshows.get("The 100").season(1)
    episode = season.episode(1)
    episode.markWatched()
    watched = season.watched()
    assert len(watched) == 1 and watched[0].title == "Pilot"
    episode.markUnwatched()


def test_video_Season_unwatched(tvshows):
    season = tvshows.get("The 100").season(1)
    episodes = season.episodes()
    episode = episodes[0]
    episode.markWatched()
    unwatched = season.unwatched()
    assert len(unwatched) == len(episodes) - 1
    episode.markUnwatched()


def test_video_Season_attrs(show):
    season = show.season("Season 1")
    assert utils.is_datetime(season.addedAt)
    if season.art:
        assert utils.is_art(season.art)
    assert season.guids == []  # TODO: Change when updating test to the Plex TV agent
    assert season.index == 1
    assert utils.is_metadata(season._initpath)
    assert utils.is_metadata(season.key)
    assert utils.is_datetime(season.lastViewedAt)
    assert utils.is_int(season.leafCount, gte=3)
    assert season.listType == "video"
    assert utils.is_metadata(season.parentKey)
    assert utils.is_int(season.parentRatingKey)
    if season.parentThumb:
        assert utils.is_thumb(season.parentThumb)
    assert season.parentTitle == "Game of Thrones"
    assert utils.is_int(season.ratingKey)
    assert season._server._baseurl == utils.SERVER_BASEURL
    assert season.summary == ""
    if season.thumb:
        assert utils.is_thumb(season.thumb)
    assert season.title == "Season 1"
    assert season.titleSort == "Season 1"
    assert season.type == "season"
    assert utils.is_datetime(season.updatedAt)
    assert utils.is_int(season.viewCount, gte=0)
    assert utils.is_int(season.viewedLeafCount, gte=0)
    assert utils.is_int(season.seasonNumber)


def test_video_Season_show(show):
    season = show.seasons()[0]
    season_by_name = show.season("Season 1")
    assert show.ratingKey == season.parentRatingKey and season_by_name.parentRatingKey
    assert season.ratingKey == season_by_name.ratingKey


def test_video_Season_watched(show):
    season = show.season("Season 1")
    season.markWatched()
    assert season.isWatched


def test_video_Season_unwatched(show):
    season = show.season("Season 1")
    season.markUnwatched()
    assert not season.isWatched


def test_video_Season_get(show):
    episode = show.season("Season 1").get("Winter Is Coming")
    assert episode.title == "Winter Is Coming"


def test_video_Season_episode(show):
    episode = show.season("Season 1").get("Winter Is Coming")
    assert episode.title == "Winter Is Coming"


def test_video_Season_episode_by_index(show):
    episode = show.season(season=1).episode(episode=1)
    assert episode.index == 1


def test_video_Season_episodes(show):
    episodes = show.season("Season 2").episodes()
    assert len(episodes) >= 1


def test_video_Season_mixins_images(show):
    season = show.season(season=1)
    test_mixins.edit_art(season)
    test_mixins.edit_poster(season)
    test_mixins.attr_artUrl(season)
    test_mixins.attr_posterUrl(season)


def test_that_reload_return_the_same_object(plex):
    # we want to check this that all the urls are correct
    movie_library_search = plex.library.section("Movies").search("Elephants Dream")[0]
    movie_search = plex.search("Elephants Dream")[0]
    movie_section_get = plex.library.section("Movies").get("Elephants Dream")
    movie_library_search_key = movie_library_search.key
    movie_search_key = movie_search.key
    movie_section_get_key = movie_section_get.key
    assert (
        movie_library_search_key
        == movie_library_search.reload().key
        == movie_search_key
        == movie_search.reload().key
        == movie_section_get_key
        == movie_section_get.reload().key
    )  # noqa
    tvshow_library_search = plex.library.section("TV Shows").search("The 100")[0]
    tvshow_search = plex.search("The 100")[0]
    tvshow_section_get = plex.library.section("TV Shows").get("The 100")
    tvshow_library_search_key = tvshow_library_search.key
    tvshow_search_key = tvshow_search.key
    tvshow_section_get_key = tvshow_section_get.key
    assert (
        tvshow_library_search_key
        == tvshow_library_search.reload().key
        == tvshow_search_key
        == tvshow_search.reload().key
        == tvshow_section_get_key
        == tvshow_section_get.reload().key
    )  # noqa
    season_library_search = tvshow_library_search.season("Season 1")
    season_search = tvshow_search.season("Season 1")
    season_section_get = tvshow_section_get.season("Season 1")
    season_library_search_key = season_library_search.key
    season_search_key = season_search.key
    season_section_get_key = season_section_get.key
    assert (
        season_library_search_key
        == season_library_search.reload().key
        == season_search_key
        == season_search.reload().key
        == season_section_get_key
        == season_section_get.reload().key
    )  # noqa
    episode_library_search = tvshow_library_search.episode(season=1, episode=1)
    episode_search = tvshow_search.episode(season=1, episode=1)
    episode_section_get = tvshow_section_get.episode(season=1, episode=1)
    episode_library_search_key = episode_library_search.key
    episode_search_key = episode_search.key
    episode_section_get_key = episode_section_get.key
    assert (
        episode_library_search_key
        == episode_library_search.reload().key
        == episode_search_key
        == episode_search.reload().key
        == episode_section_get_key
        == episode_section_get.reload().key
    )  # noqa


def test_video_exists_accessible(movie, episode):
    assert movie.media[0].parts[0].exists is None
    assert movie.media[0].parts[0].accessible is None
    movie.reload()
    assert movie.media[0].parts[0].exists is True
    assert movie.media[0].parts[0].accessible is True

    assert episode.media[0].parts[0].exists is None
    assert episode.media[0].parts[0].accessible is None
    episode.reload()
    assert episode.media[0].parts[0].exists is True
    assert episode.media[0].parts[0].accessible is True


def test_video_edits_locked(movie, episode):
    edits = {'titleSort.value': 'New Title Sort', 'titleSort.locked': 1}
    movieTitleSort = movie.titleSort
    movie.edit(**edits)
    movie.reload()
    for field in movie.fields:
        if field.name == 'titleSort':
            assert movie.titleSort == 'New Title Sort'
            assert field.locked is True
    movie.edit(**{'titleSort.value': movieTitleSort, 'titleSort.locked': 0})

    episodeTitleSort = episode.titleSort
    episode.edit(**edits)
    episode.reload()
    for field in episode.fields:
        if field.name == 'titleSort':
            assert episode.titleSort == 'New Title Sort'
            assert field.locked is True
    episode.edit(**{'titleSort.value': episodeTitleSort, 'titleSort.locked': 0})


@pytest.mark.skip(
    reason="broken? assert len(plex.conversions()) == 1 may fail on some builds"
)
def test_video_optimize(movie, plex):
    plex.optimizedItems(removeAll=True)
    movie.optimize(targetTagID=1)
    plex.conversions(pause=True)
    sleep(1)
    assert len(plex.optimizedItems()) == 1
    assert len(plex.conversions()) == 1
    conversion = plex.conversions()[0]
    conversion.remove()
    assert len(plex.conversions()) == 0
    assert len(plex.optimizedItems()) == 1
    optimized = plex.optimizedItems()[0]
    video = plex.optimizedItem(optimizedID=optimized.id)
    assert movie.key == video.key
    plex.optimizedItems(removeAll=True)
    assert len(plex.optimizedItems()) == 0
