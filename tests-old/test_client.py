# -*- coding: utf-8 -*-
import time
from utils import log, register, getclient
from plexapi import CONFIG


@register()
def test_list_clients(account, plex):
    clients = [c.title for c in plex.clients()]
    log(2, 'Clients: %s' % ', '.join(clients or []))
    assert clients, 'Server is not listing any clients.'


@register()
def test_client_navigation(account, plex):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    _navigate(plex, client)
    

@register()
def test_client_navigation_via_proxy(account, plex):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    client.proxyThroughServer()
    _navigate(plex, client)


def _navigate(plex, client):
    episode = plex.library.section(CONFIG.show_section).get(CONFIG.show_title).get(CONFIG.show_episode)
    artist = plex.library.section(CONFIG.audio_section).get(CONFIG.audio_artist)
    log(2, 'Client: %s (%s)' % (client.title, client.product))
    log(2, 'Capabilities: %s' % client.protocolCapabilities)
    # Move around a bit
    log(2, 'Browsing around..')
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
    log(2, 'Navigating to %s..' % episode.title)
    client.goToMedia(episode); time.sleep(5)
    log(2, 'Navigating to %s..' % artist.title)
    client.goToMedia(artist); time.sleep(5)
    log(2, 'Navigating home..')
    client.goToHome(); time.sleep(5)
    client.moveUp(); time.sleep(0.5)
    client.moveUp(); time.sleep(0.5)
    client.moveUp(); time.sleep(0.5)
    # Show context menu
    client.contextMenu(); time.sleep(3)
    client.goBack(); time.sleep(5)


@register()
def test_video_playback(account, plex):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    _video_playback(plex, client)


@register()
def test_video_playback_via_proxy(account, plex):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    client.proxyThroughServer()
    _video_playback(plex, client)


def _video_playback(plex, client):
    try:
        mtype = 'video'
        movie = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
        subs = [s for s in movie.subtitleStreams if s.language == 'English']
        log(2, 'Client: %s (%s)' % (client.title, client.product))
        log(2, 'Capabilities: %s' % client.protocolCapabilities)
        log(2, 'Playing to %s..' % movie.title)
        client.playMedia(movie); time.sleep(5)
        log(2, 'Pause..')
        client.pause(mtype); time.sleep(2)
        log(2, 'Step Forward..')
        client.stepForward(mtype); time.sleep(5)
        log(2, 'Play..')
        client.play(mtype); time.sleep(3)
        log(2, 'Seek to 10m..')
        client.seekTo(10*60*1000); time.sleep(5)
        log(2, 'Disable Subtitles..')
        client.setSubtitleStream(0, mtype); time.sleep(10)
        log(2, 'Load English Subtitles %s..' % subs[0].id)
        client.setSubtitleStream(subs[0].id, mtype); time.sleep(10)
        log(2, 'Stop..')
        client.stop(mtype); time.sleep(1)
    finally:
        log(2, 'Cleanup: Marking %s watched.' % movie.title)
        movie.markWatched()


@register()
def test_client_timeline(account, plex):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    _test_timeline(plex, client)


@register()
def test_client_timeline_via_proxy(account, plex):
    client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
    client.proxyThroughServer()
    _test_timeline(plex, client)


def _test_timeline(plex, client):
    try:
        mtype = 'video'
        client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
        movie = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
        time.sleep(30)  # previous test may have played media..
        playing = client.isPlayingMedia()
        log(2, 'Playing Media: %s' % playing)
        assert playing is False, 'isPlayingMedia() should have returned False.'
        client.playMedia(movie); time.sleep(30)
        playing = client.isPlayingMedia()
        log(2, 'Playing Media: %s' % playing)
        assert playing is True, 'isPlayingMedia() should have returned True.'
        client.stop(mtype); time.sleep(30)
        playing = client.isPlayingMedia()
        log(2, 'Playing Media: %s' % playing)
        assert playing is False, 'isPlayingMedia() should have returned False.'
    finally:
        log(2, 'Cleanup: Marking %s watched.' % movie.title)
        movie.markWatched()