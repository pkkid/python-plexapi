# -*- coding: utf-8 -*-
from utils import log, register
from plexapi import CONFIG


@register()
def test_mark_movie_watched(account, plex):
    movie = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
    movie.markUnwatched()
    log(2, 'Marking movie watched: %s' % movie)
    log(2, 'View count: %s' % movie.viewCount)
    movie.markWatched()
    log(2, 'View count: %s' % movie.viewCount)
    assert movie.viewCount == 1, 'View count 0 after watched.'
    movie.markUnwatched()
    log(2, 'View count: %s' % movie.viewCount)
    assert movie.viewCount == 0, 'View count 1 after unwatched.'


@register()
def test_refresh_section(account, plex):
    shows = plex.library.section(CONFIG.movie_section)
    shows.refresh()
    

@register()
def test_refresh_video(account, plex):
    result = plex.search(CONFIG.movie_title)
    result[0].refresh()