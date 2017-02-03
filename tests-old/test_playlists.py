# -*- coding: utf-8 -*-
import time
from utils import log, register, getclient
from plexapi import CONFIG


@register()
def test_list_playlists(account, plex):
    playlists = plex.playlists()
    for playlist in playlists:
        log(2, playlist.title)


# TODO: Fix test_playlists/test_create_playlist
# FAIL: (500) internal_server_error
# @register()
def test_create_playlist(account, plex):
    # create the playlist
    title = 'test_create_playlist'
    log(2, 'Creating playlist %s..' % title)
    episodes = plex.library.section(CONFIG.show_section).get(CONFIG.show_title).episodes()
    playlist = plex.createPlaylist(title, episodes[:3])
    try:
        items = playlist.items()
        log(4, 'Title: %s' % playlist.title)
        log(4, 'Items: %s' % items)
        log(4, 'Duration: %s min' % int(playlist.duration / 60000.0))
        assert playlist.title == title, 'Playlist not created successfully.'
        assert len(items) == 3, 'Playlist does not contain 3 items.'
        assert items[0].ratingKey == episodes[0].ratingKey, 'Items not in proper order [0a].'
        assert items[1].ratingKey == episodes[1].ratingKey, 'Items not in proper order [1a].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2a].'
        # move items around (b)
        log(2, 'Testing move items..')
        playlist.moveItem(items[1])
        items = playlist.items()
        assert items[0].ratingKey == episodes[1].ratingKey, 'Items not in proper order [0b].'
        assert items[1].ratingKey == episodes[0].ratingKey, 'Items not in proper order [1b].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2b].'
        # move items around (c)
        playlist.moveItem(items[0], items[1])
        items = playlist.items()
        assert items[0].ratingKey == episodes[0].ratingKey, 'Items not in proper order [0c].'
        assert items[1].ratingKey == episodes[1].ratingKey, 'Items not in proper order [1c].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2c].'
        # add an item
        log(2, 'Testing add item: %s' % episodes[3])
        playlist.addItems(episodes[3])
        items = playlist.items()
        log(4, '4th Item: %s' % items[3])
        assert items[3].ratingKey == episodes[3].ratingKey, 'Missing added item: %s' % episodes[3]
        # add two items
        log(2, 'Testing add item: %s' % episodes[4:6])
        playlist.addItems(episodes[4:6])
        items = playlist.items()
        log(4, '5th+ Items: %s' % items[4:])
        assert items[4].ratingKey == episodes[4].ratingKey, 'Missing added item: %s' % episodes[4]
        assert items[5].ratingKey == episodes[5].ratingKey, 'Missing added item: %s' % episodes[5]
        assert len(items) == 6, 'Playlist should have 6 items, %s found' % len(items)
        # remove item
        toremove = items[3]
        log(2, 'Testing remove item: %s' % toremove)
        playlist.removeItem(toremove)
        items = playlist.items()
        assert toremove not in items, 'Removed item still in playlist: %s' % items[3]
        assert len(items) == 5, 'Playlist should have 5 items, %s found' % len(items)
    finally:
        playlist.delete()


@register()
def test_playlist(account, plex):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    artist = plex.library.section(CONFIG.audio_section).get(CONFIG.audio_artist)
    album = artist.album(CONFIG.audio_album)
    playlist = plex.createPlaylist('test_play_playlist', album)
    try:
        log(2, 'Playing playlist: %s' % playlist)
        client.playMedia(playlist); time.sleep(5)
        log(2, 'stop..')
        client.stop('music'); time.sleep(1)
    finally:
        playlist.delete()


@register()
def test_playlist_photos(account, plex):
    client = getclient('iphone-mike', CONFIG.client_baseurl, plex)
    photosection = plex.library.section(CONFIG.photo_section)
    album = photosection.get(CONFIG.photo_album)
    photos = album.photos()
    playlist = plex.createPlaylist('test_play_playlist2', photos)
    try:
        client.playMedia(playlist)
        for i in range(3):
            time.sleep(2)
            client.skipNext(mtype='photo')
    finally:
        playlist.delete()


@register()
def test_play_photos(account, plex):
    client = getclient('iphone-mike', CONFIG.client_baseurl, plex)
    photosection = plex.library.section(CONFIG.photo_section)
    album = photosection.get(CONFIG.photo_album)
    photos = album.photos()
    for photo in photos[:4]:
        client.playMedia(photo)
        time.sleep(2)


@register()
def test_play_queues(account, plex):
    episode = plex.library.section(CONFIG.show_section).get(CONFIG.show_title).get(CONFIG.show_episode)
    playqueue = plex.createPlayQueue(episode)
    assert len(playqueue.items) == 1, 'No items in play queue.'
    assert playqueue.items[0].title == CONFIG.show_episode, 'Wrong show queued.'
    assert playqueue.playQueueID, 'Play queue ID not set.'