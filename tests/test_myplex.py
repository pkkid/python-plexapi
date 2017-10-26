# -*- coding: utf-8 -*-
import pytest
from plexapi.exceptions import BadRequest
from . import conftest as utils


def test_myplex_accounts(account, plex):
    assert account, 'Must specify username, password & resource to run this test.'
    print('MyPlexAccount:')
    print('username: %s' % account.username)
    print('email: %s' % account.email)
    print('home: %s' % account.home)
    print('queueEmail: %s' % account.queueEmail)
    assert account.username, 'Account has no username'
    assert account.authenticationToken, 'Account has no authenticationToken'
    assert account.email, 'Account has no email'
    assert account.home is not None, 'Account has no home'
    assert account.queueEmail, 'Account has no queueEmail'
    account = plex.account()
    print('Local PlexServer.account():')
    print('username: %s' % account.username)
    #print('authToken: %s' % account.authToken)
    print('signInState: %s' % account.signInState)
    assert account.username, 'Account has no username'
    assert account.authToken, 'Account has no authToken'
    assert account.signInState, 'Account has no signInState'


def test_myplex_resources(account):
    assert account, 'Must specify username, password & resource to run this test.'
    resources = account.resources()
    for resource in resources:
        name = resource.name or 'Unknown'
        connections = [c.uri for c in resource.connections]
        connections = ', '.join(connections) if connections else 'None'
        print('%s (%s): %s' % (name, resource.product, connections))
    assert resources, 'No resources found for account: %s' % account.name


def test_myplex_connect_to_resource(plex, account):
    servername = plex.friendlyName
    for resource in account.resources():
        if resource.name == servername:
            break
    assert resource.connect(timeout=10)


def test_myplex_devices(account):
    devices = account.devices()
    for device in devices:
        name = device.name or 'Unknown'
        connections = ', '.join(device.connections) if device.connections else 'None'
        print('%s (%s): %s' % (name, device.product, connections))
    assert devices, 'No devices found for account: %s' % account.name


def test_myplex_device(account):
    assert account.device('pkkid-plexapi')


def _test_myplex_connect_to_device(account):
    devices = account.devices()
    for device in devices:
        if device.name == 'some client name' and len(device.connections):
            break
    client = device.connect()
    assert client, 'Unable to connect to device'


def test_myplex_users(account):
    users = account.users()
    assert users, 'Found no users on account: %s' % account.name
    print('Found %s users.' % len(users))
    user = account.user(users[0].title)
    print('Found user: %s' % user)
    assert user, 'Could not find user %s' % users[0].title

    assert len(users[0].servers[0].sections()) == 7, "Could'nt info about the shared libraries"


def test_myplex_resource(account):
    assert account.resource('pkkid-plexapi')


def test_myplex_webhooks(account):
    with pytest.raises(BadRequest):
        account.webhooks()


def test_myplex_addwebhooks(account):
    with pytest.raises(BadRequest):
        account.addWebhook('http://site.com')


def test_myplex_deletewebhooks(account):
    with pytest.raises(BadRequest):
        account.deleteWebhook('http://site.com')


def test_myplex_optout(account):
    def enabled():
        ele = account.query('https://plex.tv/api/v2/user/privacy')
        lib = ele.attrib.get('optOutLibraryStats')
        play = ele.attrib.get('optOutPlayback')
        return bool(int(lib)), bool(int(play))

    # This should be False False
    library_enabled, playback_enabled = enabled()

    account.optOut(library=True, playback=True)

    assert all(enabled())

    account.optOut(library=False, playback=False)

    assert not all(enabled())


def test_myplex_inviteFriend_remove(account, plex, mocker):
    inv_user = 'hellowlol'
    vid_filter = {'contentRating': ['G'], 'label': ['foo']}
    secs = plex.library.sections()

    ids = account._getSectionIds(plex.machineIdentifier, secs)
    with mocker.patch.object(account, '_getSectionIds', return_value=ids):
        with utils.callable_http_patch(mocker):

            account.inviteFriend(inv_user, plex, secs, allowSync=True, allowCameraUpload=True,
                         allowChannels=False, filterMovies=vid_filter, filterTelevision=vid_filter,
                         filterMusic={'label': ['foo']})

        assert inv_user not in [u.title for u in account.users()]

        with utils.callable_http_patch(mock):
            account.removeFriend(inv_user)
