# -*- coding: utf-8 -*-


def test_mark_movie_watched(movie):
    movie.markUnwatched()
    print(f'Marking movie watched: {movie}')
    print(f'View count: {movie.viewCount}')
    movie.markWatched()
    movie.reload()
    print(f'View count: {movie.viewCount}')
    assert movie.viewCount == 1, 'View count 0 after watched.'
    movie.markUnwatched()
    movie.reload()
    print(f'View count: {movie.viewCount}')
    assert movie.viewCount == 0, 'View count 1 after unwatched.'


def test_refresh_section(tvshows):
    tvshows.refresh()


def test_refresh_video(movie):
    movie.refresh()
