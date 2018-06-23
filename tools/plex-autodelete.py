#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-AutoDelete is a useful to delete all but the last X episodes of a show.
This comes in handy when you have a show you keep downloaded, but do not
religiously keep every single episode that is downloaded.

Usage:
Intended usage is to add one of the tags keep5', keep10, keep15, to any show
you want to have this behaviour. Then simply add this script to run on a schedule
and you should be all set.

Example Crontab:
*/5 * * * * /home/atodd/plex-autodelete.py >> /home/atodd/plex-autodelete.log 2>&1
"""
import os
from datetime import datetime
from plexapi.server import PlexServer

TAGS = {'keep5':5, 'keep10':10, 'keep15':15}
datestr = lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def delete_episode(episode):
    for media in episode.media:
        for mediapart in media.parts:
            try:
                filepath = mediapart.file
                print('%s Deleting %s.' % (datestr(), filepath))
                os.unlink(filepath)
                # Check the parent directory is empty
                dirname = os.path.dirname(filepath)
                if not os.listdir(dirname):
                    print('%s Removing empty directory %s.' % (datestr(), dirname))
                    os.rmdir(dirname)
            except Exception as err:
                print('%s Error deleting %s; %s' % (datestr(), filepath, err))


if __name__ == '__main__':
    print('%s Starting plex-markwatched script..' % datestr())
    plex = PlexServer()
    for section in plex.library.sections():
        if section.type in ('show',):
            episodes_deleted = 0
            for tag, keep in TAGS.items():
                for show in section.search(collection=tag):
                    print('%s Cleaning %s to %s items.' % (datestr(), show.title, keep))
                    items = sorted(show.episodes(), key=lambda x:x.originallyAvailableAt or x.addedAt, reverse=True)
                    for episode in items[keep:]:
                        delete_episode(episode)
                        episodes_deleted += 1
            if episodes_deleted:
                section.update()
