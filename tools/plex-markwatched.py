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

Example Crontab:
*/5 * * * * /home/atodd/plex-markwatched.py >> /home/atodd/plex-markwatched.log 2>&1
"""
from datetime import datetime
from plexapi.server import PlexServer


if __name__ == '__main__':
    datestr = lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('%s Starting plex-markwatched script..' % datestr())
    plex = PlexServer()
    for section in plex.library.sections():
        if section.type in ('show',):  # ('movie', 'artist', 'show'):
            for item in section.search(collection='markwatched'):
                for episode in item.episodes():
                    if not episode.isWatched:
                        print('%s Marking %s watched.' % (datestr(), episode.title))
                        episode.markWatched()
