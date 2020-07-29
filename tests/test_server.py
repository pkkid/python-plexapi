# -*- coding: utf-8 -*-
import re
import time

import pytest
from PIL import Image, ImageStat
from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer
from plexapi.utils import download
from requests import Session

from . import conftest as utils


def test_server_attr(plex, account):
    assert plex._baseurl == utils.SERVER_BASEURL
    assert len(plex.friendlyName) >= 1
    assert len(plex.machineIdentifier) == 40
    assert plex.myPlex is True
    # if you run the tests very shortly after server creation the state in rare cases may be `unknown`
    assert plex.myPlexMappingState in ("mapped", "unknown")
    assert plex.myPlexSigninState == "ok"
    assert utils.is_int(plex.myPlexSubscription, gte=0)
    assert re.match(utils.REGEX_EMAIL, plex.myPlexUsername)
    assert plex.platform in ("Linux", "Windows")
    assert len(plex.platformVersion) >= 5
    assert plex._token == account.authenticationToken
    assert utils.is_int(plex.transcoderActiveVideoSessions, gte=0)
    assert utils.is_datetime(plex.updatedAt)
    assert len(plex.version) >= 5


def test_server_alert_listener(plex, movies):
    try:
        messages = []
        listener = plex.startAlertListener(messages.append)
        movies.refresh()
        utils.wait_until(lambda: len(messages) >= 3, delay=1, timeout=30)
        assert len(messages) >= 3
    finally:
        listener.stop()


@pytest.mark.req_client
def test_server_session():
    # TODO: Implement test_server_session
    pass


def test_server_library(plex):
    # TODO: Implement test_server_library
    assert plex.library


def test_server_url(plex):
    assert "ohno" in plex.url("ohno")


def test_server_transcodeImage(tmpdir, plex, show):
    width, height = 500, 500
    imgurl = plex.transcodeImage(show.banner, height, width)
    gray = imgurl = plex.transcodeImage(show.banner, height, width, saturation=0)
    resized_img = download(
        imgurl, plex._token, savepath=str(tmpdir), filename="resize_image"
    )
    original_img = download(
        show._server.url(show.banner),
        plex._token,
        savepath=str(tmpdir),
        filename="original_img",
    )
    grayscale_img = download(
        gray, plex._token, savepath=str(tmpdir), filename="grayscale_img"
    )
    with Image.open(resized_img) as image:
        assert width, height == image.size
    with Image.open(original_img) as image:
        assert width, height != image.size
    assert _detect_color_image(grayscale_img, thumb_size=150) == "grayscale"


def _detect_color_image(file, thumb_size=150, MSE_cutoff=22, adjust_color_bias=True):
    # http://stackoverflow.com/questions/20068945/detect-if-image-is-color-grayscale-or-black-and-white-with-python-pil
    pilimg = Image.open(file)
    bands = pilimg.getbands()
    if bands == ("R", "G", "B") or bands == ("R", "G", "B", "A"):
        thumb = pilimg.resize((thumb_size, thumb_size))
        sse, bias = 0, [0, 0, 0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel) / 3
            sse += sum(
                (pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2]
            )
        mse = float(sse) / (thumb_size * thumb_size)
        return "grayscale" if mse <= MSE_cutoff else "color"
    elif len(bands) == 1:
        return "blackandwhite"


def test_server_fetchitem_notfound(plex):
    with pytest.raises(NotFound):
        plex.fetchItem(123456789)


def test_server_search(plex, movie):
    title = movie.title
    #  this search seem to fail on my computer but not at travis, wtf.
    assert plex.search(title)
    assert plex.search(title, mediatype="movie")


def test_server_playlist(plex, show):
    episodes = show.episodes()
    playlist = plex.createPlaylist("test_playlist", episodes[:3])
    try:
        assert playlist.title == "test_playlist"
        with pytest.raises(NotFound):
            plex.playlist("<playlist-not-found>")
    finally:
        playlist.delete()


def test_server_playlists(plex, show):
    playlists = plex.playlists()
    count = len(playlists)
    episodes = show.episodes()
    playlist = plex.createPlaylist("test_playlist", episodes[:3])
    try:
        playlists = plex.playlists()
        assert len(playlists) == count + 1
    finally:
        playlist.delete()


def test_server_history(plex, movie):
    movie.markWatched()
    history = plex.history()
    assert len(history)
    movie.markUnwatched()


def test_server_Server_query(plex):
    assert plex.query("/")
    with pytest.raises(NotFound):
        assert plex.query("/asdf/1234/asdf", headers={"random_headers": "1234"})


def test_server_Server_session(account):
    # Mock Sesstion
    class MySession(Session):
        def __init__(self):
            super(self.__class__, self).__init__()
            self.plexapi_session_test = True

    # Test Code
    plex = PlexServer(
        utils.SERVER_BASEURL, account.authenticationToken, session=MySession()
    )
    assert hasattr(plex._session, "plexapi_session_test")


@pytest.mark.authenticated
def test_server_token_in_headers(plex):
    headers = plex._headers()
    assert "X-Plex-Token" in headers
    assert len(headers["X-Plex-Token"]) >= 1


def test_server_createPlayQueue(plex, movie):
    playqueue = plex.createPlayQueue(movie, shuffle=1, repeat=1)
    assert "shuffle=1" in playqueue._initpath
    assert "repeat=1" in playqueue._initpath
    assert playqueue.playQueueShuffled is True


def test_server_client_not_found(plex):
    with pytest.raises(NotFound):
        plex.client("<This-client-should-not-be-found>")


def test_server_sessions(plex):
    assert len(plex.sessions()) >= 0


def test_server_isLatest(plex, mocker):
    from os import environ

    is_latest = plex.isLatest()
    if environ.get("PLEX_CONTAINER_TAG") and environ["PLEX_CONTAINER_TAG"] != "latest":
        assert not is_latest
    else:
        return pytest.skip(
            "Do not forget to run with PLEX_CONTAINER_TAG != latest to ensure that update is available"
        )


def test_server_installUpdate(plex, mocker):
    m = mocker.MagicMock(release="aa")
    with utils.patch('plexapi.server.PlexServer.check_for_update', return_value=m):
        with utils.callable_http_patch():
            plex.installUpdate()


def test_server_check_for_update(plex, mocker):
    class R:
        def __init__(self, **kwargs):
            self.download_key = "plex.tv/release/1337"
            self.version = "1337"
            self.added = "gpu transcode"
            self.fixed = "fixed rare bug"
            self.downloadURL = "http://path-to-update"
            self.state = "downloaded"

    with utils.patch('plexapi.server.PlexServer.check_for_update', return_value=R()):
        rel = plex.check_for_update(force=False, download=True)
        assert rel.download_key == "plex.tv/release/1337"
        assert rel.version == "1337"
        assert rel.added == "gpu transcode"
        assert rel.fixed == "fixed rare bug"
        assert rel.downloadURL == "http://path-to-update"
        assert rel.state == "downloaded"


@pytest.mark.client
def test_server_clients(plex):
    assert len(plex.clients())
    client = plex.clients()[0]
    assert client._baseurl == utils.CLIENT_BASEURL
    assert client._server._baseurl == utils.SERVER_BASEURL
    assert client.protocol == 'plex'
    assert int(client.protocolVersion) in range(4)
    assert isinstance(client.machineIdentifier, str)
    assert client.deviceClass in ['phone', 'tablet', 'stb', 'tv', 'pc']
    assert set(client.protocolCapabilities).issubset({'timeline', 'playback', 'navigation', 'mirror', 'playqueues'})


@pytest.mark.authenticated
@pytest.mark.xfail(strict=False)
def test_server_account(plex):
    account = plex.account()
    assert account.authToken
    # TODO: Figure out why this is missing from time to time.
    # assert account.mappingError == 'publisherror'
    assert account.mappingErrorMessage is None
    assert account.mappingState == "mapped"
    if account.mappingError != "unreachable":
        if account.privateAddress is not None:
            # This seems to fail way to often..
            if len(account.privateAddress):
                assert re.match(utils.REGEX_IPADDR, account.privateAddress)
            else:
                assert account.privateAddress == ""

        assert int(account.privatePort) >= 1000
        assert re.match(utils.REGEX_IPADDR, account.publicAddress)
        assert int(account.publicPort) >= 1000
    else:
        assert account.privateAddress == ""
        assert int(account.privatePort) == 0
        assert account.publicAddress == ""
        assert int(account.publicPort) == 0
    assert account.signInState == "ok"
    assert isinstance(account.subscriptionActive, bool)
    if account.subscriptionActive:
        assert len(account.subscriptionFeatures)
    # Below check keeps failing.. it should go away.
    # else: assert sorted(account.subscriptionFeatures) == ['adaptive_bitrate',
    #     'download_certificates', 'federated-auth', 'news']
    assert (
        account.subscriptionState == "Active"
        if account.subscriptionActive
        else "Unknown"
    )
    assert re.match(utils.REGEX_EMAIL, account.username)


def test_server_downloadLogs(tmpdir, plex):
    plex.downloadLogs(savepath=str(tmpdir), unpack=True)
    assert len(tmpdir.listdir()) > 1


def test_server_downloadDatabases(tmpdir, plex):
    plex.downloadDatabases(savepath=str(tmpdir), unpack=True)
    assert len(tmpdir.listdir()) > 1


def test_server_allowMediaDeletion(account):
    plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
    # Check server current allowMediaDeletion setting
    if plex.allowMediaDeletion:
        # If allowed then test disallowed
        plex._allowMediaDeletion(False)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is None
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(False)

        plex._allowMediaDeletion(True)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is True
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(True)
    else:
        # If disallowed then test allowed
        plex._allowMediaDeletion(True)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is True
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(True)

        plex._allowMediaDeletion(False)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is None
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(False)
