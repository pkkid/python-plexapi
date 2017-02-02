# -*- coding: utf-8 -*-
from utils import log, register
from plexapi import CONFIG


# TODO: test_navigation/test_navigate_to_movie
# FAIL: (500) internal_server_error
# @register()
def test_navigate_to_movie(account, plex):
    result_library = plex.library.get(CONFIG.movie_title)
    result_movies = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
    log(2, 'Navigating to: %s' % CONFIG.movie_title)
    log(2, 'Result Library: %s' % result_library)
    log(2, 'Result Movies: %s' % result_movies)
    assert result_movies, 'Movie navigation not working.'
    assert result_library == result_movies, 'Movie navigation not consistent.'


@register()
def test_navigate_to_show(account, plex):
    result_shows = plex.library.section(CONFIG.show_section).get(CONFIG.show_title)
    log(2, 'Navigating to: %s' % CONFIG.show_title)
    log(2, 'Result Shows: %s' % result_shows)
    assert result_shows, 'Show navigation not working.'


# TODO: Fix test_navigation/test_navigate_around_show
# FAIL: Unable to list season: Season 1
# @register()
def test_navigate_around_show(account, plex):
    show = plex.library.section(CONFIG.show_section).get(CONFIG.show_title)
    seasons = show.seasons()
    season = show.season(CONFIG.show_season)
    episodes = show.episodes()
    episode = show.episode(CONFIG.show_episode)
    log(2, 'Navigating around show: %s' % show)
    log(2, 'Seasons: %s...' % seasons[:3])
    log(2, 'Season: %s' % season)
    log(2, 'Episodes: %s...' % episodes[:3])
    log(2, 'Episode: %s' % episode)
    assert CONFIG.show_season in [s.title for s in seasons], 'Unable to list season: %s' % CONFIG.show_season
    assert CONFIG.show_episode in [e.title for e in episodes], 'Unable to list episode: %s' % CONFIG.show_episode
    assert show.season(CONFIG.show_season) == season, 'Unable to get show season: %s' % CONFIG.show_season
    assert show.episode(CONFIG.show_episode) == episode, 'Unable to get show episode: %s' % CONFIG.show_episode
    assert season.episode(CONFIG.show_episode) == episode, 'Unable to get season episode: %s' % CONFIG.show_episode
    assert season.show() == show, 'season.show() doesnt match expected show.'
    assert episode.show() == show, 'episode.show() doesnt match expected show.'
    assert episode.season() == season, 'episode.season() doesnt match expected season.'


@register()
def test_navigate_around_artist(account, plex):
    artist = plex.library.section(CONFIG.audio_section).get(CONFIG.audio_artist)
    albums = artist.albums()
    album = artist.album(CONFIG.audio_album)
    tracks = artist.tracks()
    track = artist.track(CONFIG.audio_track)
    log(2, 'Navigating around artist: %s' % artist)
    log(2, 'Albums: %s...' % albums[:3])
    log(2, 'Album: %s' % album)
    log(2, 'Tracks: %s...' % tracks[:3])
    log(2, 'Track: %s' % track)
    assert CONFIG.audio_album in [a.title for a in albums], 'Unable to list album: %s' % CONFIG.audio_album
    assert CONFIG.audio_track in [e.title for e in tracks], 'Unable to list track: %s' % CONFIG.audio_track
    assert artist.album(CONFIG.audio_album) == album, 'Unable to get artist album: %s' % CONFIG.audio_album
    assert artist.track(CONFIG.audio_track) == track, 'Unable to get artist track: %s' % CONFIG.audio_track
    assert album.track(CONFIG.audio_track) == track, 'Unable to get album track: %s' % CONFIG.audio_track
    assert album.artist() == artist, 'album.artist() doesnt match expected artist.'
    assert track.artist() == artist, 'track.artist() doesnt match expected artist.'
    assert track.album() == album, 'track.album() doesnt match expected album.'