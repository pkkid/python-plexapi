# -*- coding: utf-8 -*-
from utils import log, register


# TODO: Fix test_sync/test_sync_items
# I don't know if this ever worked. It was contributed by the guy that added sync support.
# @register()
def test_sync_items(account, plex):
    device = account.getDevice('device-uuid')
    # fetch the sync items via the device sync list
    for item in device.sync_items():
        # fetch the media object associated with the sync item
        for video in item.get_media():
            # fetch the media parts (actual video/audio streams) associated with the media
            for part in video.iterParts():
                log(2, 'Found media to download!')
                # make the relevant sync id (media part) as downloaded
                # this tells the server that this device has successfully downloaded this media part of this sync item
                item.mark_as_done(part.sync_id)