# -*- coding: utf-8 -*-
import pytest


def test_myplex_accounts(plex_account, pms):
    account = plex_account
    assert account, 'Must specify username, password & resource to run this test.'
    print('MyPlexAccount:')
    print('username: %s' % account.username)
    #print('authenticationToken: %s' % account.authenticationToken)
    print('email: %s' % account.email)
    print('home: %s' % account.home)
    print('queueEmail: %s' % account.queueEmail)
    assert account.username, 'Account has no username'
    assert account.authenticationToken, 'Account has no authenticationToken'
    assert account.email, 'Account has no email'
    assert account.home is not None, 'Account has no home'
    assert account.queueEmail, 'Account has no queueEmail'
    account = pms.account()
    print('Local PlexServer.account():')
    print('username: %s' % account.username)
    print('authToken: %s' % account.authToken)
    print('signInState: %s' % account.signInState)
    assert account.username, 'Account has no username'
    assert account.authToken, 'Account has no authToken'
    assert account.signInState, 'Account has no signInState'


def test_myplex_resources(plex_account):
    account = plex_account
    assert account, 'Must specify username, password & resource to run this test.'
    resources = account.resources()
    for resource in resources:
        name = resource.name or 'Unknown'
        connections = [c.uri for c in resource.connections]
        connections = ', '.join(connections) if connections else 'None'
        print('%s (%s): %s' % (name, resource.product, connections))
    assert resources, 'No resources found for account: %s' % account.name


def test_myplex_connect_to_resource(plex_account):
    for resource in plex_account.resources():
        if resource.name == 'PMS_API_TEST_SERVER':
            break
    server = resource.connect()
    assert 'Ohno' in server.url('Ohno')
    assert server


def test_myplex_devices(plex_account):
    account = plex_account
    devices = account.devices()
    for device in devices:
        name = device.name or 'Unknown'
        connections = ', '.join(device.connections) if device.connections else 'None'
        print('%s (%s): %s' % (name, device.product, connections))
    assert devices, 'No devices found for account: %s' % account.name


#@pytest.mark.req_client # this need to be recorded?
def _test_myplex_connect_to_device(plex_account):
    account = plex_account
    devices = account.devices()
    for device in devices:
        if device.name == 'some client name' and len(device.connections):
            break
    client = device.connect()
    assert client, 'Unable to connect to device'


def test_myplex_users(plex_account):
    account = plex_account
    users = account.users()
    assert users, 'Found no users on account: %s' % account.name
    print('Found %s users.' % len(users))
    user = account.user('Hellowlol')
    print('Found user: %s' % user)
    assert user, 'Could not find user Hellowlol'
