#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from plexapi.server import PlexServer

plex = PlexServer()
for section in plex.library.sections():
    if section.type in ('movie', 'artist', 'show'):
        for item in section.search(collection='markwatched'):
            print('Marking %s watched.' % item.title)
            item.watched()
