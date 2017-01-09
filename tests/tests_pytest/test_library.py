# -*- coding: utf-8 -*-
import pytest


def test_section(pms):
    sections = pms.library.sections()
    assert len(sections) == 4

    lfs = 'TV Shows'
    section_name = pms.library.section(lfs)
    assert section_name.title == lfs


def test_library_sectionByID_is_equal_section(pms):
    assert pms.library.sectionByID('1').uuid == pms.library.section('Movies').uuid


def test_library_sectionByID_with_attrs(pms):
    m = pms.library.sectionByID('1')
    assert m.agent == 'com.plexapp.agents.imdb'
    assert m.allowSync is False
    assert m.art == '/:/resources/movie-fanart.jpg'
    assert m.composite == '/library/sections/1/composite/1484690696'
    assert str(m.createdAt.date()) == '2017-01-17'
    assert m.filters == '1'
    assert m.initpath == '/library/sections'
    assert m.key == '1'
    assert m.language == 'en'
    assert m.locations == ['/media/movies']
    assert m.refreshing is False
    assert m.scanner == 'Plex Movie Scanner'
    assert m.server.baseurl == 'http://138.68.157.5:32400'
    assert m.thumb == '/:/resources/movie.png'
    assert m.title == 'Movies'
    assert m.type == 'movie'
    assert str(m.updatedAt.date()) == '2017-01-17'
    assert m.uuid == '2b72d593-3881-43f4-a8b8-db541bd3535a'


def test_library_section_get_movie(pms): # fix me
    m = pms.library.section('Movies').get('16 blocks')
    assert m


def test_library_getByKey(pms):
    m = pms.library.getByKey('1')
    assert m.title == '16 Blocks'


def test_library_onDeck(pms):
    assert len(list(pms.library.onDeck()))


def test_library_recentlyAdded(pms):
    assert len(list(pms.library.recentlyAdded()))


def test_library_get(pms):
    m = pms.library.get('16 blocks')
    assert m.title == '16 Blocks'


#### Start on library search

def test_library_and_section_search_for_movie(pms):
    find = '16 blocks'
    l_search = pms.library.search(find)
    s_search = pms.library.section('Movies').search(find)
    assert l_search == s_search


def test_search_with_apostrophe(pms):
    show_title = "Marvel's Daredevil"  # Test ' in show title
    result_server = pms.search(show_title)
    result_shows = pms.library.section('TV Shows').search(show_title)

    assert result_server
    assert result_shows
    assert result_server == result_shows


def test_crazy_search(pms, a_movie):
    movie = a_movie
    movies = pms.library.section('Movies')
    assert movie in movies.search(actor=movie.actors[0]), 'Unable to search movie by actor.'
    assert movie in movies.search(director=movie.directors[0]), 'Unable to search movie by director.'
    assert movie in movies.search(year=['2006', '2007']), 'Unable to search movie by year.'
    assert movie not in movies.search(year=2007), 'Unable to filter movie by year.'
    assert movie in movies.search(actor=movie.actors[0].id)
