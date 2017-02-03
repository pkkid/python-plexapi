# -*- coding: utf-8 -*-
import time
from utils import log, register, getclient
from plexapi import CONFIG


@register()
def test_server(account, plex):
    log(2, 'Username: %s' % plex.myPlexUsername)
    log(2, 'Platform: %s' % plex.platform)
    log(2, 'Version: %s' % plex.version)
    assert plex.myPlexUsername is not None, 'Unknown username.'
    assert plex.platform is not None, 'Unknown platform.'
    assert plex.version is not None, 'Unknown version.'


@register()
def test_list_sections(account, plex):
    sections = [s.title for s in plex.library.sections()]
    log(2, 'Sections: %s' % sections)
    assert CONFIG.show_section in sections, '%s not a library section.' % CONFIG.show_section
    assert CONFIG.movie_section in sections, '%s not a library section.' % CONFIG.movie_section
    plex.library.section(CONFIG.show_section)
    plex.library.section(CONFIG.movie_section)


@register()
def test_history(account, plex):
    history = plex.history()
    for item in history[:20]:
        log(2, "%s: %s played %s '%s'" % (item.viewedAt, item.username, item.TYPE, item.title))
    assert len(history), 'No history items have been found.'


@register()
def test_sessions(account, plex):
    client, movie = None, None
    try:
        mtype = 'video'
        movie = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
        client = getclient(CONFIG.client, CONFIG.client_baseurl, plex)
        log(2, 'Playing %s..' % movie.title)
        client.playMedia(movie); time.sleep(5)
        sessions = plex.sessions()
        for item in sessions[:20]:
            log(2, "%s is playing %s '%s' on %s" % (item.username, item.TYPE, item.title, item.player.platform))
        assert len(sessions), 'No session items have been found.'
    finally:
        log(2, 'Stop..')
        if client: client.stop(mtype); time.sleep(1)
        log(2, 'Cleanup: Marking %s watched.' % movie.title)
        if movie: movie.markWatched()