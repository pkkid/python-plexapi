#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listen to plex alerts and print them to the console.
Because we're using print as a function, example only works in Python3.
"""
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi import X_PLEX_IDENTIFIER


if __name__ == '__main__':
    myplex = MyPlexAccount()
    plex = PlexServer(token=myplex.authenticationToken)
    for device in plex.myPlexAccount().devices():
        if device.clientIdentifier == plex.machineIdentifier:
            print('Removing device "%s", with id "%s"' % (device.name, device. clientIdentifier))
            device.delete()

    # If we suddenly remove the client first we wouldn't be able to authenticate to delete the server
    for device in plex.myPlexAccount().devices():
        if device.clientIdentifier == X_PLEX_IDENTIFIER:
            print('Removing device "%s", with id "%s"' % (device.name, device. clientIdentifier))
            device.delete()
            break
