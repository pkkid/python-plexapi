# -*- coding: utf-8 -*-
from datetime import datetime

import pytest
from plexapi.exceptions import BadRequest, NotFound

from . import conftest as utils


def test_history_Movie(movie):
    movie.markWatched()
    history = movie.history()
    assert len(history)
    movie.markUnwatched()


def test_history_Show(show):
    show.markWatched()
    history = show.history()
    assert len(history)
    show.markUnwatched()


def test_history_Season(show):
    season = show.season("Season 1")
    season.markWatched()
    history = season.history()
    assert len(history)
    season.markUnwatched()


def test_history_Episode(episode):
    episode.markWatched()
    history = episode.history()
    assert len(history)
    episode.markUnwatched()


def test_history_Artist(artist):
    history = artist.history()


def test_history_Album(album):
    history = album.history()


def test_history_Track(track):
    history = track.history()


def test_history_MyAccount(account, movie, show):
    movie.markWatched()
    show.markWatched()
    history = account.history()
    assert len(history)
    movie.markUnwatched()
    show.markUnwatched()


def test_history_MyLibrary(plex, movie, show):
    movie.markWatched()
    show.markWatched()
    history = plex.library.history()
    assert len(history)
    movie.markUnwatched()
    show.markUnwatched()


def test_history_MySection(plex, movie):
    movie.markWatched()
    history = plex.library.section("Movies").history()
    assert len(history)
    movie.markUnwatched()


def test_history_MyServer(plex, movie):
    movie.markWatched()
    history = plex.history()
    assert len(history)
    movie.markUnwatched()


def test_history_User(account, shared_username):
    user = account.user(shared_username)
    history = user.history()


def test_history_UserServer(account, shared_username, plex):
    userSharedServer = account.user(shared_username).server(plex.friendlyName)
    history = userSharedServer.history()


def test_history_UserSection(account, shared_username, plex):
    userSharedServerSection = (
        account.user(shared_username).server(plex.friendlyName).section("Movies")
    )
    history = userSharedServerSection.history()
