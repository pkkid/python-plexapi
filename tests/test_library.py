# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime, timedelta
import pytest
from plexapi.exceptions import BadRequest, NotFound

from . import conftest as utils


def test_library_Library_section(plex):
    sections = plex.library.sections()
    assert len(sections) >= 3
    section_name = plex.library.section("TV Shows")
    assert section_name.title == "TV Shows"
    with pytest.raises(NotFound):
        assert plex.library.section("cant-find-me")


def test_library_Library_sectionByID_is_equal_section(plex, movies):
    # test that sctionmyID refreshes the section if the key is missing
    # this is needed if there isnt any cached sections
    assert plex.library.sectionByID(movies.key).uuid == movies.uuid


def test_library_sectionByID_with_attrs(plex, movies):
    assert movies.agent == "tv.plex.agents.movie"
    # This seems to fail for some reason.
    # my account alloew of sync, didnt find any about settings about the library.
    # assert movies.allowSync is ("sync" in plex.ownerFeatures)
    assert movies.art == "/:/resources/movie-fanart.jpg"
    assert utils.is_metadata(
        movies.composite, prefix="/library/sections/", contains="/composite/"
    )
    assert utils.is_datetime(movies.createdAt)
    assert movies.filters is True
    assert movies._initpath == "/library/sections"
    assert utils.is_int(movies.key)
    assert movies.language == "en-US"
    assert len(movies.locations) == 1
    assert len(movies.locations[0]) >= 10
    assert movies.refreshing is False
    assert movies.scanner == "Plex Movie"
    assert movies._server._baseurl == utils.SERVER_BASEURL
    assert movies.thumb == "/:/resources/movie.png"
    assert movies.title == "Movies"
    assert movies.type == "movie"
    assert utils.is_datetime(movies.updatedAt)
    assert len(movies.uuid) == 36


def test_library_section_get_movie(movies):
    assert movies.get("Sita Sings the Blues")


def test_library_section_movies_all(movies):
    # size should always be none unless pagenation is being used.
    assert movies.totalSize == 4
    assert len(movies.all(container_start=0, container_size=1, maxresults=1)) == 1


def test_library_section_delete(movies, patched_http_call):
    movies.delete()


def test_library_fetchItem(plex, movie):
    item1 = plex.library.fetchItem("/library/metadata/%s" % movie.ratingKey)
    item2 = plex.library.fetchItem(movie.ratingKey)
    assert item1.title == "Elephants Dream"
    assert item1 == item2 == movie


def test_library_onDeck(plex, movie):
    movie.updateProgress(movie.duration * 1000 / 10)  # set progress to 10%
    assert len(list(plex.library.onDeck()))
    movie.markUnwatched()


def test_library_recentlyAdded(plex):
    assert len(list(plex.library.recentlyAdded()))


def test_library_add_edit_delete(plex):
    # Dont add a location to prevent scanning scanning
    section_name = "plexapi_test_section"
    plex.library.add(
        name=section_name,
        type="movie",
        agent="com.plexapp.agents.imdb",
        scanner="Plex Movie Scanner",
        language="en",
    )
    assert plex.library.section(section_name)
    edited_library = plex.library.section(section_name).edit(
        name="a renamed lib", type="movie", agent="com.plexapp.agents.imdb"
    )
    assert edited_library.title == "a renamed lib"
    plex.library.section("a renamed lib").delete()


def test_library_Library_cleanBundle(plex):
    plex.library.cleanBundles()


def test_library_Library_optimize(plex):
    plex.library.optimize()


def test_library_Library_emptyTrash(plex):
    plex.library.emptyTrash()


def _test_library_Library_refresh(plex):
    # TODO: fix mangle and proof the sections attrs
    plex.library.refresh()


def test_library_Library_update(plex):
    plex.library.update()


def test_library_Library_cancelUpdate(plex):
    plex.library.cancelUpdate()


def test_library_Library_deleteMediaPreviews(plex):
    plex.library.deleteMediaPreviews()


def test_library_Library_all(plex):
    assert len(plex.library.all(title__iexact="The 100"))


def test_library_Library_search(plex):
    item = plex.library.search("Elephants Dream")[0]
    assert item.title == "Elephants Dream"
    assert len(plex.library.search(libtype="episode"))


def test_library_MovieSection_update(movies):
    movies.update()


def test_library_MovieSection_update_path(movies):
    movies.update(path=movies.locations[0])


def test_library_MovieSection_refresh(movies, patched_http_call):
    movies.refresh()


def test_library_MovieSection_search_genre(movie, movies):
    genre = movie.genres[0]
    assert len(movies.search(genre=genre)) >= 1


def test_library_MovieSection_cancelUpdate(movies):
    movies.cancelUpdate()


def test_librarty_deleteMediaPreviews(movies):
    movies.deleteMediaPreviews()


def test_library_MovieSection_onDeck(movie, movies, tvshows, episode):
    movie.updateProgress(movie.duration * 1000 / 10)  # set progress to 10%
    assert movies.onDeck()
    movie.markUnwatched()
    episode.updateProgress(episode.duration * 1000 / 10)
    assert tvshows.onDeck()
    episode.markUnwatched()


def test_library_MovieSection_searchMovies(movies):
    assert movies.searchMovies(title="Elephants Dream")


def test_library_MovieSection_recentlyAdded(movies):
    assert len(movies.recentlyAdded())


def test_library_MovieSection_analyze(movies):
    movies.analyze()


def test_library_MovieSection_collections(movies, collection):
    assert len(movies.collections())


def test_library_ShowSection_all(tvshows):
    assert len(tvshows.all(title__iexact="The 100"))


def test_library_ShowSection_searchShows(tvshows):
    assert tvshows.searchShows(title="The 100")


def test_library_ShowSection_searchSseasons(tvshows):
    assert tvshows.searchSeasons(**{"show.title": "The 100"})


def test_library_ShowSection_searchEpisodes(tvshows):
    assert tvshows.searchEpisodes(title="Winter Is Coming")


def test_library_ShowSection_recentlyAdded(tvshows):
    assert len(tvshows.recentlyAdded())


def test_library_ShowSection_playlists(plex, tvshows, show):
    episodes = show.episodes()
    playlist = plex.createPlaylist("test_library_ShowSection_playlists", episodes[:3])
    try:
        assert len(tvshows.playlists())
    finally:
        playlist.delete()


def test_library_MusicSection_albums(music):
    assert len(music.albums())


def test_library_MusicSection_searchTracks(music):
    assert len(music.searchTracks(title="As Colourful As Ever"))


def test_library_MusicSection_searchAlbums(music):
    assert len(music.searchAlbums(title="Layers"))


def test_library_PhotoSection_searchAlbums(photos, photoalbum):
    title = photoalbum.title
    albums = photos.searchAlbums(title)
    assert len(albums)


def test_library_PhotoSection_searchPhotos(photos, photoalbum):
    title = photoalbum.photos()[0].title
    assert len(photos.searchPhotos(title))


def test_library_and_section_search_for_movie(plex, movies):
    find = "Elephants Dream"
    l_search = plex.library.search(find)
    s_search = movies.search(find)
    assert l_search == s_search


def test_library_settings(movies):
    settings = movies.settings()
    assert len(settings) >= 1


def test_library_editAdvanced_default(movies):
    movies.editAdvanced(hidden=2)
    for setting in movies.settings():
        if setting.id == "hidden":
            assert int(setting.value) == 2

    movies.editAdvanced(collectionMode=0)
    for setting in movies.settings():
        if setting.id == "collectionMode":
            assert int(setting.value) == 0

    movies.reload()
    movies.defaultAdvanced()
    for setting in movies.settings():
        assert str(setting.value) == str(setting.default)


def test_search_with_weird_a(plex, tvshows):
    ep_title = "Coup de Grâce"
    result_root = plex.search(ep_title)
    result_shows = tvshows.searchEpisodes(title=ep_title)
    assert result_root
    assert result_shows
    assert result_root == result_shows


def test_crazy_search(plex, movies, movie):
    assert movie in movies.search(
        actor=movie.actors[0], sort="titleSort"
    ), "Unable to search movie by actor."
    assert movie in movies.search(
        director=movie.directors[0]
    ), "Unable to search movie by director."
    assert movie in movies.search(
        year=["2006", "2007"]
    ), "Unable to search movie by year."
    assert movie not in movies.search(year=2007), "Unable to filter movie by year."
    assert movie in movies.search(actor=movie.actors[0].tag)
    assert len(movies.search(container_start=2, maxresults=1)) == 1
    assert len(movies.search(container_size=None)) == 4
    assert len(movies.search(container_size=1)) == 4
    assert len(movies.search(container_start=9999, container_size=1)) == 0
    assert len(movies.search(container_start=2, container_size=1)) == 2


def test_library_section_timeline(plex, movies):
    tl = movies.timeline()
    assert tl.TAG == "LibraryTimeline"
    assert tl.size > 0
    assert tl.allowSync is False
    assert tl.art == "/:/resources/movie-fanart.jpg"
    assert tl.content == "secondary"
    assert tl.identifier == "com.plexapp.plugins.library"
    assert datetime.fromtimestamp(tl.latestEntryTime).date() == datetime.today().date()
    assert tl.mediaTagPrefix == "/system/bundle/media/flags/"
    assert tl.mediaTagVersion > 1
    assert tl.thumb == "/:/resources/movie.png"
    assert tl.title1 == "Movies"
    assert utils.is_int(tl.updateQueueSize, gte=0)
    assert tl.viewGroup == "secondary"
    assert tl.viewMode == 65592


def test_library_MovieSection_hubSearch(movies):
    assert movies.hubSearch("Elephants Dream")


def test_library_MovieSection_search(movies, movie):
    movie.addLabel("test_search")
    movie.addCollection("test_search")
    _test_library_search(movies, movie)
    movie.removeLabel("test_search", locked=False)
    movie.removeCollection("test_search", locked=False)


def test_library_ShowSection_search(tvshows, show):
    show.addLabel("test_search")
    show.addCollection("test_search")
    _test_library_search(tvshows, show)
    show.removeLabel("test_search", locked=False)
    show.removeCollection("test_search", locked=False)

    season = show.season(season=1)
    _test_library_search(tvshows, season)

    episode = season.episode(episode=1)
    _test_library_search(tvshows, episode)


def test_library_MusicSection_search(music, artist):
    artist.addGenre("test_search")
    artist.addStyle("test_search")
    artist.addMood("test_search")
    artist.addCollection("test_search")
    _test_library_search(music, artist)
    artist.removeGenre("test_search", locked=False)
    artist.removeStyle("test_search", locked=False)
    artist.removeMood("test_search", locked=False)
    artist.removeCollection("test_search", locked=False)

    album = artist.album("Layers")
    album.addGenre("test_search")
    album.addStyle("test_search")
    album.addMood("test_search")
    album.addCollection("test_search")
    album.addLabel("test_search")
    _test_library_search(music, album)
    album.removeGenre("test_search", locked=False)
    album.removeStyle("test_search", locked=False)
    album.removeMood("test_search", locked=False)
    album.removeCollection("test_search", locked=False)
    album.removeLabel("test_search", locked=False)
    
    track = album.track(track=1)
    track.addMood("test_search")
    _test_library_search(music, track)
    track.removeMood("test_search", locked=False)


def test_library_PhotoSection_search(photos, photoalbum):
    photo = photoalbum.photo("photo1")
    photo.addTag("test_search")
    _test_library_search(photos, photo)
    photo.removeTag("test_search")


def test_library_MovieSection_search_sort(movies):
    results = movies.search(sort="titleSort")
    titleSort = [r.titleSort for r in results]
    assert titleSort == sorted(titleSort)
    results_asc = movies.search(sort="titleSort:asc")
    titleSort_asc = [r.titleSort for r in results_asc]
    assert titleSort == titleSort_asc
    results_desc = movies.search(sort="titleSort:desc")
    titleSort_desc = [r.titleSort for r in results_desc]
    assert titleSort_desc == sorted(titleSort_desc, reverse=True)


def test_library_search_exceptions(movies):
    with pytest.raises(BadRequest):
        movies.listFilterChoices(field="123abc.title")
    with pytest.raises(BadRequest):
        movies.search(**{"123abc": True})
    with pytest.raises(BadRequest):
        movies.search(year="123abc")
    with pytest.raises(BadRequest):
        movies.search(sort="123abc")
    with pytest.raises(NotFound):
        movies.getFilterType(libtype='show')
    with pytest.raises(NotFound):
        movies.getFieldType(fieldType="unknown")
    with pytest.raises(NotFound):
        movies.listFilterChoices(field="unknown")
    with pytest.raises(NotFound):
        movies.search(unknown="unknown")
    with pytest.raises(NotFound):
        movies.search(**{"title<>!=": "unknown"})
    with pytest.raises(NotFound):
        movies.search(sort="unknown")
    with pytest.raises(NotFound):
        movies.search(sort="titleSort:bad")


def _test_library_search(library, obj):
    # Create & operator
    AndOperator = namedtuple('AndOperator', ['key', 'title'])
    andOp = AndOperator('&=', 'and')

    fields = library.listFields(obj.type)
    for field in fields:
        fieldAttr = field.key.split(".")[-1]
        operators = library.listOperators(field.type)
        if field.type in {'tag', 'string'}:
            operators += [andOp]

        for operator in operators:
            if fieldAttr == "unmatched" and operator.key == "!=" or fieldAttr == 'userRating':
                continue

            value = getattr(obj, fieldAttr, None)

            if field.type == "boolean" and value is None:
                value = fieldAttr.startswith("unwatched")
            if field.type == "tag" and isinstance(value, list) and value and operator.title != 'and':
                value = value[0]
            elif value is None:
                continue

            if operator.title == "begins with":
                searchValue = value[:3]
            elif operator.title == "ends with":
                searchValue = value[-3:]
            elif "contain" in operator.title:
                searchValue = value.split(" ")[0]
            elif operator.title == "is less than":
                searchValue = value + 1
            elif operator.title == "is greater than":
                searchValue = max(value - 1, 0)
            elif operator.title == "is before":
                searchValue = value + timedelta(days=1)
            elif operator.title == "is after":
                searchValue = value - timedelta(days=1)
            else:
                searchValue = value
            
            searchFilter = {field.key + operator.key[:-1]: searchValue}
            results = library.search(libtype=obj.type, **searchFilter)

            if operator.key.startswith("!") or operator.key.startswith(">>") and searchValue == 0:
                assert obj not in results
            else:
                assert obj in results

            # Test search again using string tag and date
            if field.type in {"tag", "date"}:
                if field.type == "tag" and fieldAttr != 'contentRating':
                    if not isinstance(searchValue, list):
                        searchValue = [searchValue]
                    searchValue = [v.tag for v in searchValue]
                elif field.type == "date":
                    searchValue = searchValue.strftime("%Y-%m-%d")

                searchFilter = {field.key + operator.key[:-1]: searchValue}
                results = library.search(libtype=obj.type, **searchFilter)

                if operator.key.startswith("!") or operator.key.startswith(">>") and searchValue == 0:
                    assert obj not in results
                else:
                    assert obj in results
