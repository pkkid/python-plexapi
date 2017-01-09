# -*- coding: utf-8 -*-
from utils import log, register
from plexapi import CONFIG


@register()
def test_search_show(account, plex):
    result_server = plex.search(CONFIG.show_title)
    result_shows = plex.library.section(CONFIG.show_section).search(CONFIG.show_title)
    result_movies = plex.library.section(CONFIG.movie_section).search(CONFIG.show_title)
    log(2, 'Searching for: %s' % CONFIG.show_title)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Shows: %s' % result_shows)
    log(4, 'Result Movies: %s' % result_movies)
    assert result_server, 'Show not found.'
    assert result_server == result_shows, 'Show searches not consistent.'
    assert not result_movies, 'Movie search returned show title.'
    

@register()
def test_search_with_apostrophe(account, plex):
    show_title = "Marvel's Daredevil"  # Test ' in show title
    result_server = plex.search(show_title)
    result_shows = plex.library.section(CONFIG.show_section).search(show_title)
    log(2, 'Searching for: %s' % CONFIG.show_title)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Shows: %s' % result_shows)
    assert result_server, 'Show not found.'
    assert result_server == result_shows, 'Show searches not consistent.'


@register()
def test_search_movie(account, plex):
    result_server = plex.search(CONFIG.movie_title)
    result_library = plex.library.search(CONFIG.movie_title)
    result_shows = plex.library.section(CONFIG.show_section).search(CONFIG.movie_title)
    result_movies = plex.library.section(CONFIG.movie_section).search(CONFIG.movie_title)
    log(2, 'Searching for: %s' % CONFIG.movie_title)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Library: %s' % result_library)
    log(4, 'Result Shows: %s' % result_shows)
    log(4, 'Result Movies: %s' % result_movies)
    assert result_server, 'Movie not found.'
    assert result_server == result_library == result_movies, 'Movie searches not consistent.'
    assert not result_shows, 'Show search returned show title.'
    

@register()
def test_search_audio(account, plex):
    result_server = plex.search(CONFIG.audio_artist)
    result_library = plex.library.search(CONFIG.audio_artist)
    result_music = plex.library.section(CONFIG.audio_section).search(CONFIG.audio_artist)
    log(2, 'Searching for: %s' % CONFIG.audio_artist)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Library: %s' % result_library)
    log(4, 'Result Music: %s' % result_music)
    assert result_server, 'Artist not found.'
    assert result_server == result_library == result_music, 'Audio searches not consistent.'
    

@register()
def test_search_related(account, plex):
    movies = plex.library.section(CONFIG.movie_section)
    movie = movies.get(CONFIG.movie_title)
    related_by_actors = movies.search(actor=movie.actors, maxresults=3)
    log(2, u'Actors: %s..' % movie.actors)
    log(2, u'Related by Actors: %s..' % related_by_actors)
    assert related_by_actors, 'No related movies found by actor.'
    related_by_genre = movies.search(genre=movie.genres, maxresults=3)
    log(2, u'Genres: %s..' % movie.genres)
    log(2, u'Related by Genre: %s..' % related_by_genre)
    assert related_by_genre, 'No related movies found by genre.'
    related_by_director = movies.search(director=movie.directors, maxresults=3)
    log(2, 'Directors: %s..' % movie.directors)
    log(2, 'Related by Director: %s..' % related_by_director)
    assert related_by_director, 'No related movies found by director.'
    

# TODO: Fix test_search/test_crazy_search
# FAIL: Unable to search movie by director.
# @register()
def test_crazy_search(account, plex):
    movies = plex.library.section(CONFIG.movie_section)
    movie = movies.get('Jurassic World')
    log(2, u'Search by Actor: "Chris Pratt"')
    assert movie in movies.search(actor='Chris Pratt'), 'Unable to search movie by actor.'
    log(2, u'Search by Director: ["Trevorrow"]')
    assert movie in movies.search(director=['Trevorrow']), 'Unable to search movie by director.'
    log(2, u'Search by Year: ["2014", "2015"]')
    assert movie in movies.search(year=['2014', '2015']), 'Unable to search movie by year.'
    log(2, u'Filter by Year: 2014')
    assert movie not in movies.search(year=2014), 'Unable to filter movie by year.'
    judy = [a for a in movie.actors if 'Judy' in a.tag][0]
    log(2, u'Search by Unpopular Actor: %s' % judy)
    assert movie in movies.search(actor=judy.id), 'Unable to filter movie by year.'