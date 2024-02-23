# -*- coding: utf-8 -*-

def test_history_Movie(movie):
    movie.markPlayed()
    history = movie.history()
    assert not len(history)
    movie.markUnplayed()


def test_history_Show(show):
    show.markPlayed()
    history = show.history()
    assert not len(history)
    show.markUnplayed()


def test_history_Season(season):
    season.markPlayed()
    history = season.history()
    assert not len(history)
    season.markUnplayed()


def test_history_Episode(episode):
    episode.markPlayed()
    history = episode.history()
    assert not len(history)
    episode.markUnplayed()


def test_history_Artist(artist):
    artist.markPlayed()
    history = artist.history()
    assert not len(history)
    artist.markUnplayed()


def test_history_Album(album):
    album.markPlayed()
    history = album.history()
    assert not len(history)
    album.markUnplayed()


def test_history_Track(track):
    track.markPlayed()
    history = track.history()
    assert not len(history)
    track.markUnplayed()


def test_history_MyAccount(account, show):
    show.markPlayed()
    history = account.history()
    assert not len(history)
    show.markUnplayed()


def test_history_MyLibrary(plex, movie):
    movie.markPlayed()
    history = plex.library.history()
    assert not len(history)
    movie.markUnplayed()


def test_history_MySection(movies, movie):
    movie.markPlayed()
    history = movies.history()
    assert not len(history)
    movie.markUnplayed()


def test_history_MyServer(plex, show):
    show.markPlayed()
    history = plex.history()
    assert not len(history)
    show.markUnplayed()


def test_history_User(account, shared_username):
    user = account.user(shared_username)
    history = user.history()

    assert isinstance(history, list)


def test_history_UserServer(account, shared_username, plex):
    userSharedServer = account.user(shared_username).server(plex.friendlyName)
    history = userSharedServer.history()

    assert isinstance(history, list)


def test_history_UserSection(account, shared_username, plex):
    userSharedServerSection = (
        account.user(shared_username).server(plex.friendlyName).section("Movies")
    )
    history = userSharedServerSection.history()

    assert isinstance(history, list)
