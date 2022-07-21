# -*- coding: utf-8 -*-


def test_mark_movie_watched(movie):
    movie.markUnplayed()
    print('Marking movie watched: %s' % movie)
    print('View count: %s' % movie.viewCount)
    movie.markPlayed()
    movie.reload()
    print('View count: %s' % movie.viewCount)
    assert movie.viewCount == 1, 'View count 0 after watched.'
    movie.markUnplayed()
    movie.reload()
    print('View count: %s' % movie.viewCount)
    assert movie.viewCount == 0, 'View count 1 after unwatched.'


def test_refresh_section(tvshows):
    tvshows.refresh()


def test_refresh_video(movie):
    movie.refresh()
