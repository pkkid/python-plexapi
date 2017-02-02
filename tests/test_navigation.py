# -*- coding: utf-8 -*-

import pytest


def test_navigate_around_show(plex_account, pms):
    show = pms.library.section('TV Shows').get('The 100')
    seasons = show.seasons()
    season = show.season('Season 1')

    episodes = show.episodes()
    episode = show.episode('Pilot')

    assert 'Season 1' in [s.title for s in seasons], 'Unable to list season:'
    assert 'Pilot' in [e.title for e in episodes], 'Unable to list episode:'
    assert show.season(1) == season
    assert show.episode('Pilot') == episode, 'Unable to get show episode:'
    assert season.episode('Pilot') == episode, 'Unable to get season episode:'
    assert season.show() == show, 'season.show() doesnt match expected show.'
    assert episode.show() == show, 'episode.show() doesnt match expected show.'
    assert episode.season() == season, 'episode.season() doesnt match expected season.'


def _test_navigate_around_artist(plex_account, pms):
    artist = pms.library.section(CONFIG.audio_section).get(CONFIG.audio_artist)
    albums = artist.albums()
    album = artist.album(CONFIG.audio_album)
    tracks = artist.tracks()
    track = artist.track(CONFIG.audio_track)
    print('Navigating around artist: %s' % artist)
    print('Albums: %s...' % albums[:3])
    print('Album: %s' % album)
    print('Tracks: %s...' % tracks[:3])
    print('Track: %s' % track)
    assert CONFIG.audio_album in [a.title for a in albums], 'Unable to list album: %s' % CONFIG.audio_album
    assert CONFIG.audio_track in [e.title for e in tracks], 'Unable to list track: %s' % CONFIG.audio_track
    assert artist.album(CONFIG.audio_album) == album, 'Unable to get artist album: %s' % CONFIG.audio_album
    assert artist.track(CONFIG.audio_track) == track, 'Unable to get artist track: %s' % CONFIG.audio_track
    assert album.track(CONFIG.audio_track) == track, 'Unable to get album track: %s' % CONFIG.audio_track
    assert album.artist() == artist, 'album.artist() doesnt match expected artist.'
    assert track.artist() == artist, 'track.artist() doesnt match expected artist.'
    assert track.album() == album, 'track.album() doesnt match expected album.'
