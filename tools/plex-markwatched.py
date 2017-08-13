#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-MarkWatched is a useful to always mark a show as watched. This comes in
handy when you have a show you keep downloaded, but do not religiously watch
every single episode that is downloaded. By marking everything watched, it
will keep the show out of your OnDeck list inside Plex.

Usage:
Intended usage is to add the tak 'markwatched' to any show you want to have
this behaviour. Then simply add this script to run on a schedule and you
should be all set.
"""
from plexapi.server import PlexServer


if __name__ == '__main__':
    plex = PlexServer()
    for section in plex.library.sections():
        if section.type in ('movie', 'artist', 'show'):
            for item in section.search(collection='markwatched'):
                print('Marking %s watched.' % item.title)
                item.watched()
