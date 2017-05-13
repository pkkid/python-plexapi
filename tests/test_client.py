# -*- coding: utf-8 -*-
import pytest, time


def _check_capabilities(client, capabilities):
    supported = client.protocolCapabilities
    for capability in capabilities:
        if capability not in supported:
            pytest.skip('Client doesnt support %s capability.', capability)


def _check_proxy(plex, client, proxy):
    if proxy:
        client.proxyThroughServer(server=plex)


@pytest.mark.client
def test_list_clients(account, plex):
    assert account.resources(), 'MyPlex is not listing any devlices.'
    assert account.devices(), 'MyPlex is not listing any devlices.'
    assert plex.clients(), 'PlexServer is not listing any clients.'


@pytest.mark.client
@pytest.mark.parametrize('proxy', [False, True])
def test_client_navigation(plex, client, episode, artist, proxy):
    _check_capabilities(client, ['navigation'])
    _check_proxy(plex, client, proxy)
    try:
        print('\nclient.moveUp()'); client.moveUp(); time.sleep(0.5)
        print('client.moveLeft()'); client.moveLeft(); time.sleep(0.5)
        print('client.moveDown()'); client.moveDown(); time.sleep(0.5)
        print('client.moveRight()'); client.moveRight(); time.sleep(0.5)
        print('client.select()'); client.select(); time.sleep(3)
        print('client.goBack()'); client.goBack(); time.sleep(1)
        print('client.goToMedia(episode)'); client.goToMedia(episode); time.sleep(5)
        print('client.goToMedia(artist)'); client.goToMedia(artist); time.sleep(5)
        #print('client.contextMenu'); client.contextMenu(); time.sleep(3)  # socket.timeout
    finally:
        print('client.goToHome()'); client.goToHome(); time.sleep(2)


@pytest.mark.client
@pytest.mark.parametrize('proxy', [False, True])
def test_client_playback(plex, client, movie, proxy):
    _check_capabilities(client, ['playback'])
    _check_proxy(plex, client, proxy)
    try:
        # Need a movie with subtitles
        print('mtype=video'); mtype = 'video'
        movie = plex.library.section('Movies').get('Moana').reload()
        subs = [stream for stream in movie.subtitleStreams() if stream.language == 'English']
        print('client.playMedia(movie)'); client.playMedia(movie); time.sleep(5)
        print('client.pause(mtype)'); client.pause(mtype); time.sleep(2)
        print('client.stepForward(mtype)'); client.stepForward(mtype); time.sleep(5)
        print('client.play(mtype)'); client.play(mtype); time.sleep(3)
        print('client.stepBack(mtype)'); client.stepBack(mtype); time.sleep(5)
        print('client.play(mtype)'); client.play(mtype); time.sleep(3)
        print('client.seekTo(10*60*1000)'); client.seekTo(10*60*1000); time.sleep(5)
        print('client.setSubtitleStream(0)'); client.setSubtitleStream(0, mtype); time.sleep(10)
        print('client.setSubtitleStream(subs[0])'); client.setSubtitleStream(subs[0].id, mtype); time.sleep(10)
        print('client.stop(mtype)'); client.stop(mtype); time.sleep(1)
    finally:
        print('movie.markWatched'); movie.markWatched(); time.sleep(2)


@pytest.mark.client
@pytest.mark.parametrize('proxy', [False, True])
def test_client_timeline(plex, client, movie, proxy):
    _check_capabilities(client, ['timeline'])
    _check_proxy(plex, client, proxy)
    try:
        # Note: We noticed the isPlaying flag could take up to a full
        # 30 seconds to be updated, hence the long sleeping.
        print('mtype=video'); mtype = 'video'
        print('time.sleep(30)'); time.sleep(30)  # clear isPlaying flag
        assert client.isPlayingMedia() is False
        print('client.playMedia(movie)'); client.playMedia(movie); time.sleep(30)
        assert client.isPlayingMedia() is True
        print('client.stop(mtype)'); client.stop(mtype); time.sleep(30)
        assert client.isPlayingMedia() is False
    finally:
        print('movie.markWatched()'); movie.markWatched(); time.sleep(2)
