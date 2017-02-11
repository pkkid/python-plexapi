# -*- coding: utf-8 -*-
import os, pytest
from plexapi import CONFIG
from plexapi.exceptions import BadRequest, NotFound
from plexapi.utils import download


def test_server_attr(pms):
    assert pms._baseurl == 'http://138.68.157.5:32400'
    assert pms.friendlyName == 'PMS_API_TEST_SERVER'
    assert pms.machineIdentifier == 'e42470b5c527c7e5ebbdc017b5a32c8c683f6f8b'
    assert pms.myPlex is True
    assert pms.myPlexMappingState == 'mapped'
    assert pms.myPlexSigninState == 'ok'
    assert pms.myPlexSubscription == '0'
    assert pms.myPlexUsername == 'testplexapi@gmail.com'
    assert pms.platform == 'Linux'
    assert pms.platformVersion == '4.4.0-59-generic (#80-Ubuntu SMP Fri Jan 6 17:47:47 UTC 2017)'
    #assert pms.session == <requests.sessions.Session object at 0x029A5E10>
    assert pms._token == os.environ.get('PLEX_TEST_TOKEN') or CONFIG.get('authentication.server_token')
    assert pms.transcoderActiveVideoSessions == 0

    #assert str(pms.updatedAt.date()) == '2017-01-20'
    assert pms.version == '1.3.3.3148-b38628e'


@pytest.mark.req_client
def test_server_session():
    pass


def test_server_library(pms):
    assert pms.library


def test_server_url(pms):
    assert 'ohno' in pms.url('ohno')


def test_server_transcodeImage(tmpdir, pms, a_show):
    # Ideally we should also test the black white but this has to do for now.
    from PIL import Image
    width, height = 500, 500
    img_url_resize = pms.transcodeImage(a_show.banner, height, width)
    gray = img_url_resize = pms.transcodeImage(a_show.banner, height, width, saturation=0)
    resized_image = download(img_url_resize, savepath=str(tmpdir), filename='resize_image')
    org_image = download(a_show._server.url(a_show.banner), savepath=str(tmpdir), filename='org_image')
    gray_image = download(gray, savepath=str(tmpdir), filename='gray_image')
    with Image.open(resized_image) as im:
        assert width, height == im.size
    with Image.open(org_image) as im:
        assert width, height != im.size
    assert _detect_color_image(gray_image, thumb_size=150) == 'grayscale'


def _detect_color_image(file, thumb_size=150, MSE_cutoff=22, adjust_color_bias=True):
    # from http://stackoverflow.com/questions/20068945/detect-if-image-is-color-grayscale-or-black-and-white-with-python-pil
    from PIL import Image, ImageStat
    pil_img = Image.open(file)
    bands = pil_img.getbands()
    if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
        thumb = pil_img.resize((thumb_size, thumb_size))
        SSE, bias = 0, [0, 0, 0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel) / 3
            SSE += sum((pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2])
        MSE = float(SSE) / (thumb_size * thumb_size)
        if MSE <= MSE_cutoff:
            return 'grayscale'
        else:
            return 'color'
    elif len(bands) == 1:
        return 'blackandwhite'


def test_server_search(pms):
    # basic search. see test_search.py
    assert pms.search('16 Blocks')
    assert pms.search('16 blocks', mediatype='movie')


def test_server_playlist(pms):
    pl = pms.playlist('some_playlist')
    assert pl.title == 'some_playlist'
    with pytest.raises(NotFound):
        pms.playlist('124xxx11y')


def test_server_playlists(pms):
    playlists = pms.playlists()
    assert len(playlists)


def test_server_history(pms):
    history = pms.history()
    assert len(history)


def test_server_Server_query(pms):
    assert pms.query('/')
    from plexapi.server import PlexServer
    with pytest.raises(BadRequest):
        assert pms.query('/asdasdsada/12123127/aaaa', headers={'random_headers': '1337'})
    with pytest.raises(BadRequest):
        # This is really requests.exceptions.HTTPError:
        # 401 Client Error: Unauthorized for url:
        PlexServer('http://138.68.157.5:32400', '1234')


def test_server_Server_session():
    from requests import Session
    from plexapi.server import PlexServer

    class MySession(Session):
        def __init__(self):
            super(self.__class__, self).__init__()
            self.plexapi_session_test = True

    plex = PlexServer('http://138.68.157.5:32400',
        os.environ.get('PLEX_TEST_TOKEN'), session=MySession())
    assert hasattr(plex._session, 'plexapi_session_test')
    pl = plex.playlists()
    assert hasattr(pl[0]._server._session, 'plexapi_session_test')
    # TODO: Check client in test_server_Server_session.
    # TODO: Check myplex in test_server_Server_session.


def test_server_token_in_headers(pms):
    h = pms._headers()
    assert 'X-Plex-Token' in h and len(h['X-Plex-Token'])


def _test_server_createPlayQueue():
    # see test_playlists.py
    pass


def _test_server_createPlaylist():
    # see test_playlists.py
    pass


def test_server_client_not_found(pms):
    with pytest.raises(NotFound):
        pms.client('<This-client-should-not-be-found>')


@pytest.mark.req_client
def test_server_client(pms):
    assert pms.client('Plex Web (Chrome)')


def test_server_Server_sessions(pms):
    assert len(pms.sessions()) == 0


@pytest.mark.req_client
def test_server_clients(pms):
    assert len(pms.clients())
    m = pms.clients()[0]
    assert m._baseurl == 'http://127.0.0.1:32400'
    assert m.device is None
    assert m.deviceClass == 'pc'
    assert m.machineIdentifier == '89hgkrbqxaxmf45o1q2949ru'
    assert m.model is None
    assert m.platform is None
    assert m.platformVersion is None
    assert m.product == 'Plex Web'
    assert m.protocol == 'plex'
    assert m.protocolCapabilities == ['timeline', 'playback', 'navigation', 'mirror', 'playqueues']
    assert m.protocolVersion == '1'
    assert m._server._baseurl == 'http://138.68.157.5:32400'
    assert m.state is None
    assert m.title == 'Plex Web (Chrome)'
    assert m.token is None
    assert m.vendor is None
    assert m.version == '2.12.5'


def test_server_account(pms):
    acc = pms.account()
    assert acc.authToken
    # TODO: Figure out why this is missing from time to time.
    #assert acc.mappingError == 'publisherror'
    assert acc.mappingErrorMessage is None
    assert acc.mappingState == 'mapped'
    assert acc.privateAddress == '138.68.157.5'
    assert acc.privatePort == '32400'
    assert acc.publicAddress == '138.68.157.5'
    assert acc.publicPort == '32400'
    assert acc.signInState == 'ok'
    assert acc.subscriptionActive == False
    assert acc.subscriptionFeatures == []
    assert acc.subscriptionState == 'Unknown'
    assert acc.username == 'testplexapi@gmail.com'
