# -*- coding: utf-8 -*-
import pytest, time


def test_list_clients(account, plex):
    # List resources from MyPlex
    print('\nResources listed on MyPlex')
    print('---------------------------')
    resources = account.resources()
    for resource in resources:
        print('%s (%s)' % (resource.name, resource.product))
        for connection in resource.connections:
            print("* baseurl='%s', token='%s'" % (connection.uri, resource.accessToken))
            print("* baseurl='%s', token='%s'" % (connection.httpuri, resource.accessToken))
    assert resources, 'MyPlex is not listing any devlices.'
    # List devices from MyPlex
    print('\nDevices listed on MyPlex')
    print('--------------------------')
    devices = account.devices()
    for device in devices:
        print('%s (%s)' % (device.name, device.product))
        for connection in device.connections:
            print("* baseurl='%s', token='%s'" % (connection, device.token))
    assert devices, 'MyPlex is not listing any devlices.'
    # List clients from PlexServer
    clients = plex.clients()
    print('\nClients listed on PlexServer')
    print('------------------------------')
    for client in clients:
        print('%s (%s)' % (client.title, client.product))
        print("* baseurl='%s', token='%s'" % (client._baseurl, plex._token))
    assert clients, 'PlexServer is not listing any clients.'


@pytest.mark.client
def test_client_navigation_direct(plex, client, episode, artist):
    _navigate(plex, client, episode, artist)
    

@pytest.mark.client
def test_client_navigation_via_proxy(plex, client, episode, artist):
    client.proxyThroughServer()
    _navigate(plex, client, episode, artist)


def _navigate(plex, client, episode, artist):
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
