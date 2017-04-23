# -*- coding: utf-8 -*-
import pytest
from plexapi.exceptions import NotFound
from . import conftest as utils


def test_library_Library_section(plex):
    sections = plex.library.sections()
    assert len(sections) == 4
    section_name = plex.library.section('TV Shows')
    assert section_name.title == 'TV Shows'
    with pytest.raises(NotFound):
        assert plex.library.section('cant-find-me')


def test_library_Library_sectionByID_is_equal_section(plex, plex2):
    # test that sctionmyID refreshes the section if the key is missing
    # this is needed if there isnt any cached sections
    assert plex2.library.sectionByID('1')
    assert plex.library.sectionByID('1').uuid == plex.library.section('Movies').uuid


def test_library_sectionByID_with_attrs(plex):
    section = plex.library.sectionByID('1')
    assert section.agent == 'com.plexapp.agents.imdb'
    assert section.allowSync is False
    assert section.art == '/:/resources/movie-fanart.jpg'
    assert '/library/sections/1/composite/' in section.composite
    assert utils.is_datetime(section.createdAt)
    assert section.filters == '1'
    assert section._initpath == '/library/sections'
    assert section.key == '1'
    assert section.language == 'en'
    assert len(section.locations) == 1
    assert len(section.locations[0]) >= 10
    assert section.refreshing is False
    assert section.scanner == 'Plex Movie Scanner'
    assert section._server._baseurl == utils.SERVER_BASEURL
    assert section.thumb == '/:/resources/movie.png'
    assert section.title == 'Movies'
    assert section.type == 'movie'
    assert utils.is_datetime(section.updatedAt)
    assert len(section.uuid) == 36


def test_library_section_get_movie(plex):
    assert plex.library.section('Movies').get('16 blocks')


def test_library_section_delete(monkeypatch, movies):
    monkeypatch.delattr("requests.sessions.Session.request")
    try:
        movies.delete()
    except AttributeError:
        # will always raise because there is no request
        pass


def test_library_fetchItem(plex, movie):
    item1 = plex.library.fetchItem('/library/metadata/%s' % movie.ratingKey)
    item2 = plex.library.fetchItem(movie.ratingKey)
    assert item1.title == '16 Blocks'
    assert item1 == item2 == movie


def test_library_onDeck(plex):
    assert len(list(plex.library.onDeck()))


def test_library_recentlyAdded(plex):
    assert len(list(plex.library.recentlyAdded()))


def test_library_search(plex):
    item = plex.library.search('16 blocks')[0]
    assert item.title == '16 Blocks'


def test_library_add_edit_delete(plex):
    # Dont add a location to prevent scanning scanning
    plex.library.add(name='zomg strange11', type='movie', agent='com.plexapp.agents.imdb',
        scanner='Plex Movie Scanner', language='en')
    assert plex.library.section('zomg strange11')
    edited_library = plex.library.section('zomg strange11').edit(name='a renamed lib',
        type='movie', agent='com.plexapp.agents.imdb')
    assert edited_library.title == 'a renamed lib'
    plex.library.section('a renamed lib').delete()


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


def _test_library_MovieSection_refresh(movies):
    movies.refresh()


def test_library_MovieSection_update(movies):
    movies.update()


def test_library_MovieSection_cancelUpdate(movies):
    movies.cancelUpdate()


def test_librarty_deleteMediaPreviews(movies):
    movies.deleteMediaPreviews()


def test_library_MovieSection_onDeck(movies):
    assert len(movies.onDeck())


def test_library_MovieSection_recentlyAdded(movies):
    assert len(movies.recentlyAdded())


def test_library_MovieSection_analyze(movies):
    movies.analyze()


def test_library_ShowSection_searchShows(tvshows):
    assert tvshows.searchShows(title='The 100')


def test_library_ShowSection_searchEpisodes(tvshows):
    assert tvshows.searchEpisodes(title='Pilot')


def test_library_ShowSection_recentlyAdded(tvshows):
    assert len(tvshows.recentlyAdded())


def test_library_MusicSection_albums(music):
    assert len(music.albums())


def test_library_MusicSection_searchTracks(music):
    assert len(music.searchTracks(title='Holy Moment'))


def test_library_MusicSection_searchAlbums(music):
    assert len(music.searchAlbums(title='Unmastered Impulses'))


def test_library_PhotoSection_searchAlbums(photos):
    albums = photos.searchAlbums('Cats')
    assert len(albums)
    print([i.TYPE for i in albums])


def test_library_PhotoSection_searchPhotos(photos):
    assert len(photos.searchPhotos('CatBed'))


# Start on library search
def test_library_and_section_search_for_movie(plex):
    find = '16 blocks'
    l_search = plex.library.search(find)
    s_search = plex.library.section('Movies').search(find)
    assert l_search == s_search


def test_search_with_apostrophe(plex):
    show_title = "Marvel's Daredevil"
    result_root = plex.search(show_title)
    result_shows = plex.library.section('TV Shows').search(show_title)
    assert result_root
    assert result_shows
    assert result_root == result_shows


def test_crazy_search(plex, movie):
    movies = plex.library.section('Movies')
    assert movie in movies.search(actor=movie.actors[0], sort='titleSort'), 'Unable to search movie by actor.'
    assert movie in movies.search(director=movie.directors[0]), 'Unable to search movie by director.'
    assert movie in movies.search(year=['2006', '2007']), 'Unable to search movie by year.'
    assert movie not in movies.search(year=2007), 'Unable to filter movie by year.'
    assert movie in movies.search(actor=movie.actors[0].tag)
