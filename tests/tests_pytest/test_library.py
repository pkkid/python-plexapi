import os

import pytest
import requests


from plexapi.server import PlexServer


for k, v in os.environ.items():
    print k, v

print os.environ.get('kek')
@pytest.fixture
def session():
    return requests.Session()


@pytest.fixture(scope='module')
def pms():
    #username = os.environ.get('plex_username')
    #password = os.environ.get('plex_password')
    token = os.environ.get('PLEX_TOKEN')
    url = 'http://10.0.0.97:32400'

    assert token
    assert url

    pms = PlexServer(url, token, session=requests.Session())
    return pms

#@pms
def test_library(pms):
    sections = pms.library.sections()
    print len(sections)


