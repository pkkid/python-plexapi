# -*- coding: utf-8 -*-


def test_mark_movie_watched(movie):
    movie.markUnwatched()
    print('Marking movie watched: %s' % movie)
    print('View count: %s' % movie.viewCount)
    movie.markWatched()
    print('View count: %s' % movie.viewCount)
    assert movie.viewCount == 1, 'View count 0 after watched.'
    movie.markUnwatched()
    print('View count: %s' % movie.viewCount)
    assert movie.viewCount == 0, 'View count 1 after unwatched.'


def test_refresh_section(tvshows):
    tvshows.refresh()


def test_refresh_video(movie):
    movie.refresh()


def test_rate_movie(movie):
    oldrate = movie.userRating
    movie.rate(10.0)
    assert movie.userRating == 10.0, 'User rating 10.0 after rating five stars.'
    movie.rate(oldrate)
