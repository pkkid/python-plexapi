# -*- coding: utf-8 -*-
import time
import pytest



def test_list_playlists(pms):
    playlists = pms.playlists()
    print(playlists)
    assert len(playlists)


def test_create_playlist(pms, a_show):
    # create the playlist
    title = 'test_create_playlist_a_show'
    #print('Creating playlist %s..' % title)
    episodes = a_show.episodes()
    playlist = pms.createPlaylist(title, episodes[:3])
    try:
        items = playlist.items()
        #log(4, 'Title: %s' % playlist.title)
        #log(4, 'Items: %s' % items)
        #log(4, 'Duration: %s min' % int(playlist.duration / 60000.0))
        assert playlist.title == title, 'Playlist not created successfully.'
        assert len(items) == 3, 'Playlist does not contain 3 items.'
        assert items[0].ratingKey == episodes[0].ratingKey, 'Items not in proper order [0a].'
        assert items[1].ratingKey == episodes[1].ratingKey, 'Items not in proper order [1a].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2a].'
        # move items around (b)
        #print('Testing move items..')
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
        #print('Testing add item: %s' % episodes[3])
        playlist.addItems(episodes[3])
        items = playlist.items()
        #log(4, '4th Item: %s' % items[3])
        assert items[3].ratingKey == episodes[3].ratingKey, 'Missing added item: %s' % episodes[3]
        # add two items
        #print('Testing add item: %s' % episodes[4:6])
        playlist.addItems(episodes[4:6])
        items = playlist.items()
        #log(4, '5th+ Items: %s' % items[4:])
        assert items[4].ratingKey == episodes[4].ratingKey, 'Missing added item: %s' % episodes[4]
        assert items[5].ratingKey == episodes[5].ratingKey, 'Missing added item: %s' % episodes[5]
        assert len(items) == 6, 'Playlist should have 6 items, %s found' % len(items)
        # remove item
        toremove = items[3]
        #print('Testing remove item: %s' % toremove)
        playlist.removeItem(toremove)
        items = playlist.items()
        assert toremove not in items, 'Removed item still in playlist: %s' % items[3]
        assert len(items) == 5, 'Playlist should have 5 items, %s found' % len(items)
    finally:
        playlist.delete()


@pytest.mark.req_client
def test_playlist_play(pms):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    artist = plex.library.section(CONFIG.audio_section).get(CONFIG.audio_artist)
    album = artist.album(CONFIG.audio_album)
    pl_name = 'test_play_playlist'
    playlist = plex.createPlaylist(pl_name, album)
    try:
        #print('Playing playlist: %s' % playlist)
        client.playMedia(playlist); time.sleep(5)
        #print('stop..')
        client.stop('music'); time.sleep(1)
    finally:
        playlist.delete()

    assert pl_name not in [i.title for i in pms.playlists()]


def test_playlist_photos(pms, a_photo_album):
    album = a_photo_album
    photos = album.photos()
    pl_name = 'test_playlist_photos'
    playlist = pms.createPlaylist(pl_name, photos)

    try:
        assert len(playlist.items()) == 4
    finally:
        playlist.delete()

    assert pl_name not in [i.title for i in pms.playlists()]


@pytest.mark.req_client
def _test_play_photos(account, plex):
    client = getclient('iphone-mike', CONFIG.client_baseurl, plex)
    photosection = plex.library.section(CONFIG.photo_section)
    album = photosection.get(CONFIG.photo_album)
    photos = album.photos()
    for photo in photos[:4]:
        client.playMedia(photo)
        time.sleep(2)


def test_play_queues(pms):
    episode = pms.library.section('TV Shows').get('the 100').get('Pilot')
    playqueue = pms.createPlayQueue(episode)
    assert len(playqueue.items) == 1, 'No items in play queue.'
    assert playqueue.items[0].title == episode.title, 'Wrong show queued.'
    assert playqueue.playQueueID, 'Play queue ID not set.'
