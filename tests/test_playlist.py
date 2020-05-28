# -*- coding: utf-8 -*-
import time

import pytest


def test_create_playlist(plex, show):
    # create the playlist
    title = 'test_create_playlist_show'
    #print('Creating playlist %s..' % title)
    episodes = show.episodes()
    playlist = plex.createPlaylist(title, episodes[:3])
    try:
        items = playlist.items()
        # Test create playlist
        assert playlist.title == title, 'Playlist not created successfully.'
        assert len(items) == 3, 'Playlist does not contain 3 items.'
        assert items[0].ratingKey == episodes[0].ratingKey, 'Items not in proper order [0a].'
        assert items[1].ratingKey == episodes[1].ratingKey, 'Items not in proper order [1a].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2a].'
        # Test move items around (b)
        playlist.moveItem(items[1])
        items = playlist.items()
        assert items[0].ratingKey == episodes[1].ratingKey, 'Items not in proper order [0b].'
        assert items[1].ratingKey == episodes[0].ratingKey, 'Items not in proper order [1b].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2b].'
        # Test move items around (c)
        playlist.moveItem(items[0], items[1])
        items = playlist.items()
        assert items[0].ratingKey == episodes[0].ratingKey, 'Items not in proper order [0c].'
        assert items[1].ratingKey == episodes[1].ratingKey, 'Items not in proper order [1c].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2c].'
        # Test add item
        playlist.addItems(episodes[3])
        items = playlist.items()
        assert items[3].ratingKey == episodes[3].ratingKey, 'Missing added item: %s' % episodes[3]
        # Test add two items
        playlist.addItems(episodes[4:6])
        items = playlist.items()
        assert items[4].ratingKey == episodes[4].ratingKey, 'Missing added item: %s' % episodes[4]
        assert items[5].ratingKey == episodes[5].ratingKey, 'Missing added item: %s' % episodes[5]
        assert len(items) == 6, 'Playlist should have 6 items, %s found' % len(items)
        # Test remove item
        toremove = items[3]
        playlist.removeItem(toremove)
        items = playlist.items()
        assert toremove not in items, 'Removed item still in playlist: %s' % items[3]
        assert len(items) == 5, 'Playlist should have 5 items, %s found' % len(items)
    finally:
        playlist.delete()


@pytest.mark.client
def test_playlist_play(plex, client, artist, album):
    try:
        playlist_name = 'test_play_playlist'
        playlist = plex.createPlaylist(playlist_name, album)
        client.playMedia(playlist); time.sleep(5)
        client.stop('music'); time.sleep(1)
    finally:
        playlist.delete()
    assert playlist_name not in [i.title for i in plex.playlists()]


def test_playlist_photos(plex, photoalbum):
    album = photoalbum
    photos = album.photos()
    try:
        playlist_name = 'test_playlist_photos'
        playlist = plex.createPlaylist(playlist_name, photos)
        assert len(playlist.items()) >= 1
    finally:
        playlist.delete()
    assert playlist_name not in [i.title for i in plex.playlists()]


def test_playlist_playQueue(plex, album):
    try:
        playlist = plex.createPlaylist('test_playlist', album)
        playqueue = playlist.playQueue(**dict(shuffle=1))
        assert 'shuffle=1' in playqueue._initpath
        assert playqueue.playQueueShuffled is True
    finally:
        playlist.delete()


@pytest.mark.client
def test_play_photos(plex, client, photoalbum):
    photos = photoalbum.photos()
    for photo in photos[:4]:
        client.playMedia(photo)
        time.sleep(2)


def test_playqueues(plex):
    episode = plex.library.section('TV Shows').get('the 100').get('Pilot')
    playqueue = plex.createPlayQueue(episode)
    assert len(playqueue.items) == 1, 'No items in play queue.'
    assert playqueue.items[0].title == episode.title, 'Wrong show queued.'
    assert playqueue.playQueueID, 'Play queue ID not set.'


def test_copyToUser(plex, show, fresh_plex, shared_username):
    episodes = show.episodes()
    playlist = plex.createPlaylist('shared_from_test_plexapi', episodes)
    try:
        playlist.copyToUser(shared_username)
        user = plex.myPlexAccount().user(shared_username)
        user_plex = fresh_plex(plex._baseurl, user.get_token(plex.machineIdentifier))
        assert playlist.title in [p.title for p in user_plex.playlists()]
    finally:
        playlist.delete()


def test_smart_playlist(plex, movies):
    pl = plex.createPlaylist(title='smart_playlist', smart=True, limit=1, section=movies, year=2008)
    assert len(pl.items()) == 1
    assert pl.smart
