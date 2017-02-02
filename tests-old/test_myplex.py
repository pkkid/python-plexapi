# -*- coding: utf-8 -*-
from utils import log, register
from plexapi import CONFIG


@register()
def test_myplex_accounts(account, plex):
    assert account, 'Must specify username, password & resource to run this test.'
    log(2, 'MyPlexAccount:')
    log(4, 'username: %s' % account.username)
    log(4, 'authenticationToken: %s' % account.authenticationToken)
    log(4, 'email: %s' % account.email)
    log(4, 'home: %s' % account.home)
    log(4, 'queueEmail: %s' % account.queueEmail)
    assert account.username, 'Account has no username'
    assert account.authenticationToken, 'Account has no authenticationToken'
    assert account.email, 'Account has no email'
    assert account.home is not None, 'Account has no home'
    assert account.queueEmail, 'Account has no queueEmail'
    account = plex.account()
    log(2, 'Local PlexServer.account():')
    log(4, 'username: %s' % account.username)
    log(4, 'authToken: %s' % account.authToken)
    log(4, 'signInState: %s' % account.signInState)
    assert account.username, 'Account has no username'
    assert account.authToken, 'Account has no authToken'
    assert account.signInState, 'Account has no signInState'


@register()
def test_myplex_resources(account, plex):
    assert account, 'Must specify username, password & resource to run this test.'
    resources = account.resources()
    for resource in resources:
        name = resource.name or 'Unknown'
        connections = [c.uri for c in resource.connections]
        connections = ', '.join(connections) if connections else 'None'
        log(2, '%s (%s): %s' % (name, resource.product, connections))
    assert resources, 'No resources found for account: %s' % account.name
    

@register()
def test_myplex_devices(account, plex):
    assert account, 'Must specify username, password & resource to run this test.'
    devices = account.devices()
    for device in devices:
        name = device.name or 'Unknown'
        connections = ', '.join(device.connections) if device.connections else 'None'
        log(2, '%s (%s): %s' % (name, device.product, connections))
    assert devices, 'No devices found for account: %s' % account.name


@register()
def test_myplex_users(account, plex):
    users = account.users()
    assert users, 'Found no users on account: %s' % account.name
    log(2, 'Found %s users.' % len(users))
    user = account.user('sdfsdfplex')
    log(2, 'Found user: %s' % user)
    assert users, 'Could not find user sdfsdfplex'
    

@register()
def test_myplex_connect_to_device(account, plex):
    assert account, 'Must specify username, password & resource to run this test.'
    devices = account.devices()
    for device in devices:
        if device.name == CONFIG.client and len(device.connections):
            break
    client = device.connect()
    log(2, 'Connected to client: %s (%s)' % (client.title, client.product))
    assert client, 'Unable to connect to device'
