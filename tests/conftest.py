from functools import partial
import os
import betamax
from betamax_serializers import pretty_json
import pytest
import requests

import plexapi

token = os.environ.get('PLEX_TOKEN')
test_token = os.environ.get('PLEX_TEST_TOKEN')
test_username = os.environ.get('PLEX_TEST_USERNAME')
test_password = os.environ.get('PLEX_TEST_PASSWORD')


@pytest.fixture(scope='session')
def pms(request):
    from plexapi.server import PlexServer

    sess = requests.Session()

    """
    CASSETTE_LIBRARY_DIR = 'response/'

    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    config = betamax.Betamax.configure()
    config.define_cassette_placeholder('MASKED', token)
    config.define_cassette_placeholder('MASKED', test_token)

    recorder = betamax.Betamax(sess, cassette_library_dir=CASSETTE_LIBRARY_DIR)
    recorder.use_cassette('http_responses', serialize_with='prettyjson') # record='new_episodes'
    recorder.start()
    """
    url = 'http://138.68.157.5:32400'
    assert test_token
    assert url

    pms = PlexServer(url, test_token, session=sess)
    #request.addfinalizer(recorder.stop)
    return pms


@pytest.fixture()
def freshpms():
    from plexapi.server import PlexServer

    sess = requests.Session()

    url = 'http://138.68.157.5:32400'
    assert test_token
    assert url

    pms = PlexServer(url, test_token, session=sess)
    return pms


def pytest_addoption(parser):
    parser.addoption("--req_client", action="store_true",
                     help="Run tests that interact with a client")


def pytest_runtest_setup(item):
    if 'req_client' in item.keywords and not item.config.getvalue("req_client"):
        pytest.skip("need --req_client option to run")
    else:
        item.config.getvalue("req_client")

@pytest.fixture()
def plex_account():
    from plexapi.myplex import MyPlexAccount
    username = test_username
    password = test_password
    assert username and password
    account = MyPlexAccount.signin(username, password)
    assert account
    return account


@pytest.fixture()
def a_movie(pms):
    m = pms.library.search('16 blocks')
    assert m
    return m[0]



@pytest.fixture()
def a_tv_section(pms):
    sec = pms.library.section('TV Shows')
    assert sec
    return sec


@pytest.fixture()
def a_movie_section(pms):
    sec = pms.library.section('Movies')
    assert sec
    return sec


@pytest.fixture()
def a_music_section(pms):
    sec = pms.library.section('Music')
    assert sec
    return sec

@pytest.fixture()
def a_photo_section(pms):
    sec = pms.library.section('Photos')
    assert sec
    return sec


@pytest.fixture()
def a_artist(a_music_section):
    sec = a_music_section.get('Infinite State')
    assert sec
    return sec


@pytest.fixture()
def a_music_album(a_music_section):
    sec = a_music_section.get('Infinite State').album('Unmastered Impulses')
    assert sec
    return sec


@pytest.fixture()
def a_track(a_music_album):
    track = a_music_album.track('Holy Moment')
    assert track
    return track


@pytest.fixture()
def a_show(a_tv_section):
    sec = a_tv_section.get('The 100')
    assert sec
    return sec


@pytest.fixture()
def a_episode(a_show):
    ep = a_show.get('Pilot')
    assert ep
    return ep



@pytest.fixture()
def a_photo_album(pms):
    sec = pms.library.section('Photos')
    assert sec
    album = sec.get('photo_album1')
    assert album
    return album


@pytest.fixture()
def monkeydownload(request, monkeypatch):
    monkeypatch.setattr('plexapi.utils.download', partial(plexapi.utils.download, mocked=True))
    yield
    monkeypatch.undo()
