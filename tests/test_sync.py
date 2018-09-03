from time import sleep

from plexapi.sync import Policy, MediaSettings, VIDEO_QUALITY_3_MBPS_720p


MAX_RETRIES = 3


def get_new_synclist(account, client_id, old_sync_items=[]):
    retry = 0
    old_ids = [i.id for i in old_sync_items]
    while retry < MAX_RETRIES:
        retry += 1
        sync_items = account.syncItems(client_id)
        new_ids = [i.id for i in sync_items.items]
        if new_ids != old_ids:
            return sync_items
        sleep(0.5)
    assert False, 'Unable to get updated SyncItems'


def test_current_device_got_sync_target(account_synctarget, device):
    assert 'sync-target' in device.provides


def test_delete_sync_item(account_synctarget, clear_sync_device, movie):
    movie.sync(clear_sync_device, Policy.create(1, False), MediaSettings.create(VIDEO_QUALITY_3_MBPS_720p))
    sync_items = get_new_synclist(account_synctarget, clear_sync_device.clientIdentifier)
    for item in sync_items.items:
        item.delete()
    sync_items = get_new_synclist(account_synctarget, clear_sync_device.clientIdentifier, sync_items.items)
    assert not sync_items.items


def test_add_movie_to_sync(account_synctarget, clear_sync_device, movie):
    movie.sync(clear_sync_device, Policy.create(1, False), MediaSettings.create(VIDEO_QUALITY_3_MBPS_720p))
    sync_items = get_new_synclist(account_synctarget, clear_sync_device.clientIdentifier)
    assert sync_items.items[0].getMedia()[0].ratingKey == movie.ratingKey


def test_add_show_to_sync(account_synctarget, clear_sync_device, show):
    show.sync(clear_sync_device, Policy.create(1, False), MediaSettings.create(VIDEO_QUALITY_3_MBPS_720p))
    sync_items = get_new_synclist(account_synctarget, clear_sync_device.clientIdentifier)
    assert sync_items.items[0].getMedia()[0].ratingKey == show.ratingKey


def test_add_season_to_sync(account_synctarget, clear_sync_device, show):
    season = show.season('Season 1')
    season.sync(clear_sync_device, Policy.create(1, False), MediaSettings.create(VIDEO_QUALITY_3_MBPS_720p))
    sync_items = get_new_synclist(account_synctarget, clear_sync_device.clientIdentifier)
    assert sync_items.items[0].getMedia()[0].ratingKey == season.ratingKey


def test_add_episode_to_sync(account_synctarget, clear_sync_device, episode):
    episode.sync(clear_sync_device, Policy.create(1, False), MediaSettings.create(VIDEO_QUALITY_3_MBPS_720p))
    sync_items = get_new_synclist(account_synctarget, clear_sync_device.clientIdentifier)
    assert sync_items.items[0].getMedia()[0].ratingKey == episode.ratingKey
