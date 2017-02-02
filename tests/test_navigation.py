# -*- coding: utf-8 -*-

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


def test_navigate_around_artist(plex_account, pms):
    artist = pms.library.section('Music').get('Infinite State')
    albums = artist.albums()
    album = artist.album('Unmastered Impulses')
    tracks = artist.tracks()
    track = artist.track('Mantra')
    print('Navigating around artist: %s' % artist)
    print('Albums: %s...' % albums[:3])
    print('Album: %s' % album)
    print('Tracks: %s...' % tracks[:3])
    print('Track: %s' % track)
    assert 'Unmastered Impulses' in [a.title for a in albums], 'Unable to list album.'
    assert 'Mantra' in [e.title for e in tracks], 'Unable to list track.'
    assert artist.album('Unmastered Impulses') == album, 'Unable to get artist album.'
    assert artist.track('Mantra') == track, 'Unable to get artist track.'
    assert album.track('Mantra') == track, 'Unable to get album track.'
    assert album.artist() == artist, 'album.artist() doesnt match expected artist.'
    assert track.artist() == artist, 'track.artist() doesnt match expected artist.'
    assert track.album() == album, 'track.album() doesnt match expected album.'
