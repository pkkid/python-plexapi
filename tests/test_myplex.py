# -*- coding: utf-8 -*-
import pytest
from plexapi.exceptions import BadRequest, NotFound

from . import conftest as utils


def test_myplex_accounts(account, plex):
    assert account, "Must specify username, password & resource to run this test."
    print("MyPlexAccount:")
    print("username: %s" % account.username)
    print("email: %s" % account.email)
    print("home: %s" % account.home)
    print("queueEmail: %s" % account.queueEmail)
    assert account.username, "Account has no username"
    assert account.authenticationToken, "Account has no authenticationToken"
    assert account.email, "Account has no email"
    assert account.home is not None, "Account has no home"
    assert account.queueEmail, "Account has no queueEmail"
    account = plex.account()
    print("Local PlexServer.account():")
    print("username: %s" % account.username)
    # print('authToken: %s' % account.authToken)
    print("signInState: %s" % account.signInState)
    assert account.username, "Account has no username"
    assert account.authToken, "Account has no authToken"
    assert account.signInState, "Account has no signInState"


def test_myplex_resources(account):
    assert account, "Must specify username, password & resource to run this test."
    resources = account.resources()
    for resource in resources:
        name = resource.name or "Unknown"
        connections = [c.uri for c in resource.connections]
        connections = ", ".join(connections) if connections else "None"
        print("%s (%s): %s" % (name, resource.product, connections))
    assert resources, "No resources found for account: %s" % account.name


def test_myplex_connect_to_resource(plex, account):
    servername = plex.friendlyName
    for resource in account.resources():
        if resource.name == servername:
            break
    assert resource.connect(timeout=10)


def test_myplex_devices(account):
    devices = account.devices()
    for device in devices:
        name = device.name or "Unknown"
        connections = ", ".join(device.connections) if device.connections else "None"
        print("%s (%s): %s" % (name, device.product, connections))
    assert devices, "No devices found for account: %s" % account.name


def test_myplex_device(account, plex):
    from plexapi import X_PLEX_DEVICE_NAME

    assert account.device(plex.friendlyName)
    assert account.device(X_PLEX_DEVICE_NAME)


def _test_myplex_connect_to_device(account):
    devices = account.devices()
    for device in devices:
        if device.name == "some client name" and len(device.connections):
            break
    client = device.connect()
    assert client, "Unable to connect to device"


def test_myplex_users(account):
    users = account.users()
    if not len(users):
        return pytest.skip("You have to add a shared account into your MyPlex")
    print("Found %s users." % len(users))
    user = account.user(users[0].title)
    print("Found user: %s" % user)
    assert user, "Could not find user %s" % users[0].title

    assert (
        len(users[0].servers[0].sections()) > 0
    ), "Couldn't info about the shared libraries"


def test_myplex_resource(account, plex):
    assert account.resource(plex.friendlyName)


def test_myplex_webhooks(account):
    if account.subscriptionActive:
        assert isinstance(account.webhooks(), list)
    else:
        with pytest.raises(BadRequest):
            account.webhooks()


def test_myplex_addwebhooks(account):
    if account.subscriptionActive:
        assert "http://example.com" in account.addWebhook("http://example.com")
    else:
        with pytest.raises(BadRequest):
            account.addWebhook("http://example.com")


def test_myplex_deletewebhooks(account):
    if account.subscriptionActive:
        assert "http://example.com" not in account.deleteWebhook("http://example.com")
    else:
        with pytest.raises(BadRequest):
            account.deleteWebhook("http://example.com")


def test_myplex_optout(account_once):
    def enabled():
        ele = account_once.query("https://plex.tv/api/v2/user/privacy")
        lib = ele.attrib.get("optOutLibraryStats")
        play = ele.attrib.get("optOutPlayback")
        return bool(int(lib)), bool(int(play))

    account_once.optOut(library=True, playback=True)
    utils.wait_until(lambda: enabled() == (True, True))
    account_once.optOut(library=False, playback=False)
    utils.wait_until(lambda: enabled() == (False, False))


def test_myplex_inviteFriend_remove(account, plex, mocker):
    inv_user = "hellowlol"
    vid_filter = {"contentRating": ["G"], "label": ["foo"]}
    secs = plex.library.sections()

    ids = account._getSectionIds(plex.machineIdentifier, secs)
    with mocker.patch.object(account, "_getSectionIds", return_value=ids):
        with utils.callable_http_patch():

            account.inviteFriend(
                inv_user,
                plex,
                secs,
                allowSync=True,
                allowCameraUpload=True,
                allowChannels=False,
                filterMovies=vid_filter,
                filterTelevision=vid_filter,
                filterMusic={"label": ["foo"]},
            )

        assert inv_user not in [u.title for u in account.users()]

        with pytest.raises(NotFound):
            with utils.callable_http_patch():
                account.removeFriend(inv_user)


def test_myplex_updateFriend(account, plex, mocker, shared_username):
    vid_filter = {"contentRating": ["G"], "label": ["foo"]}
    secs = plex.library.sections()
    user = account.user(shared_username)

    ids = account._getSectionIds(plex.machineIdentifier, secs)
    with mocker.patch.object(account, "_getSectionIds", return_value=ids):
        with mocker.patch.object(account, "user", return_value=user):
            with utils.callable_http_patch():

                account.updateFriend(
                    shared_username,
                    plex,
                    secs,
                    allowSync=True,
                    removeSections=True,
                    allowCameraUpload=True,
                    allowChannels=False,
                    filterMovies=vid_filter,
                    filterTelevision=vid_filter,
                    filterMusic={"label": ["foo"]},
                )


def test_myplex_createExistingUser(account, plex, shared_username):
    user = account.user(shared_username)
    url = "https://plex.tv/api/invites/requested/{}?friend=0&server=0&home=1".format(
        user.id
    )

    account.createExistingUser(user, plex)
    assert shared_username in [u.username for u in account.users() if u.home is True]
    # Remove Home invite
    account.query(url, account._session.delete)
    # Confirm user was removed from home and has returned to friend
    assert shared_username not in [
        u.username for u in plex.myPlexAccount().users() if u.home is True
    ]
    assert shared_username in [
        u.username for u in plex.myPlexAccount().users() if u.home is False
    ]


@pytest.mark.skip(reason="broken test?")
def test_myplex_createHomeUser_remove(account, plex):
    homeuser = "New Home User"
    account.createHomeUser(homeuser, plex)
    assert homeuser in [u.title for u in plex.myPlexAccount().users() if u.home is True]
    account.removeHomeUser(homeuser)
    assert homeuser not in [
        u.title for u in plex.myPlexAccount().users() if u.home is True
    ]


def test_myplex_plexpass_attributes(account_plexpass):
    assert account_plexpass.subscriptionActive
    assert account_plexpass.subscriptionStatus == "Active"
    assert account_plexpass.subscriptionPlan
    assert "sync" in account_plexpass.subscriptionFeatures
    assert "premium_music_metadata" in account_plexpass.subscriptionFeatures
    assert "plexpass" in account_plexpass.roles
    assert set(account_plexpass.entitlements) == utils.ENTITLEMENTS


def test_myplex_claimToken(account):
    assert account.claimToken().startswith("claim-")
