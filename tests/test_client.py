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
    # Browse around a bit..
    client.moveDown(); time.sleep(0.5)
    client.moveDown(); time.sleep(0.5)
    client.moveDown(); time.sleep(0.5)
    client.select(); time.sleep(3)
    client.moveRight(); time.sleep(0.5)
    client.moveRight(); time.sleep(0.5)
    client.moveLeft(); time.sleep(0.5)
    client.select(); time.sleep(3)
    client.goBack(); time.sleep(1)
    client.goBack(); time.sleep(3)
    # Go directly to media
    client.goToMedia(episode); time.sleep(5)
    client.goToMedia(artist); time.sleep(5)
    client.goToHome(); time.sleep(5)
    client.moveUp(); time.sleep(0.5)
    client.moveUp(); time.sleep(0.5)
    client.moveUp(); time.sleep(0.5)
    # Show context menu
    client.contextMenu(); time.sleep(3)
    client.goBack(); time.sleep(5)


@pytest.mark.client
@pytest.mark.parametrize('proxy', [False, True])
def test_video_playback(plex, client, movie, proxy):
    _check_capabilities(client, ['playback'])
    _check_proxy(plex, client, proxy)
    try:
        # Need a movie with subtitles
        movie = plex.library.section('Movies').get('Moana').reload()
        mtype = 'video'
        subs = [stream for stream in movie.subtitleStreams() if stream.language == 'English']
        # Basic play ability
        print('Basic play ability')
        client.playMedia(movie); time.sleep(5)
        client.pause(mtype); time.sleep(2)
        # Step forward, back, seek in time
        print('Step forward, back, seek in time')
        client.stepForward(mtype); time.sleep(5)
        client.play(mtype); time.sleep(3)
        client.stepBack(mtype); time.sleep(5)
        client.play(mtype); time.sleep(3)
        client.seekTo(10*60*1000); time.sleep(5)
        # Enable subtitles
        print('Enable subtitles')
        client.setSubtitleStream(0, mtype); time.sleep(10)
        client.setSubtitleStream(subs[0].id, mtype); time.sleep(10)
        client.stop(mtype); time.sleep(1)
    finally:
        movie.markWatched()


@pytest.mark.client
def _test_client_PlexClient__loadData(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_connect(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_contextMenu(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_goBack(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_goToHome(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_goToMedia(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_goToMusic(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_headers(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_isPlayingMedia(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_moveDown(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_moveLeft(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_moveRight(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_moveUp(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_nextLetter(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_pageDown(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_pageUp(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_pause(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_play(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_playMedia(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_previousLetter(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_proxyThroughServer(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_query(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_refreshPlayQueue(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_seekTo(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_select(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_sendCommand(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setAudioStream(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setParameters(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setRepeat(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setShuffle(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setStreams(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setSubtitleStream(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setVideoStream(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_setVolume(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_skipNext(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_skipPrevious(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_skipTo(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_stepBack(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_stepForward(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_stop(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_timeline(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_toggleOSD(pms):
    pass


@pytest.mark.req_client
def _test_client_PlexClient_url(pms):
    pass
