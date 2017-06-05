#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This will find every item marked with the collection 'markwatched' and mark
it watched. Just set run every so often in a scheduled task. This will only
work for the user you connect to the PlexServer as.
"""
from plexapi.server import PlexServer

plex = PlexServer()
for section in plex.library.sections():
    if section.type in ('movie', 'artist', 'show'):
        for item in section.search(collection='markwatched'):
            print('Marking %s watched.' % item.title)
            item.watched()
