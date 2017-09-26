#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Allows downloading a Plex media item from a local or shared library. You
may specify the item by the PlexWeb url (everything after !) or by
manually searching the items from the command line wizard.

Original contribution by lad1337.
"""
import argparse
import os
import re
import shutil

from plexapi import utils
from plexapi.compat import unquote
from plexapi.video import Episode, Movie, Show

VALID_TYPES = (Movie, Episode, Show)


def search_for_item(url=None):
    if url: return get_item_from_url(opts.url)
    servers = [s for s in account.resources() if 'server' in s.provides]
    server = utils.choose('Choose a Server', servers, 'name').connect()
    query = input('What are you looking for?: ')
    item  = []
    items = [i for i in server.search(query) if i.__class__ in VALID_TYPES]
    items = utils.choose('Choose result', items, lambda x: '(%s) %s' % (x.type.title(), x.title[0:60]))

    if not isinstance(items, list):
        items = [items]

    for i in items:
        if isinstance(i, Show):
            display = lambda i: '%s %s %s' % (i.grandparentTitle, i.seasonEpisode, i.title)
            item = utils.choose('Choose episode', i.episodes(), display)

    if not isinstance(item, list):
        item = [item]

    return item


def get_item_from_url(url):
    # Parse the ClientID and Key from the URL
    clientid = re.findall('[a-f0-9]{40}', url)
    key = re.findall('key=(.*?)(&.*)?$', url)
    if not clientid or not key:
        raise SystemExit('Cannot parse URL: %s' % url)
    clientid = clientid[0]
    key = unquote(key[0][0])
    # Connect to the server and fetch the item
    servers = [r for r in account.resources() if r.clientIdentifier == clientid]
    if len(servers) != 1:
        raise SystemExit('Unknown or ambiguous client id: %s' % clientid)
    server = servers[0].connect()
    return server.fetchItem(key)


if __name__ == '__main__':
    # Command line parser
    from plexapi import CONFIG
    from tqdm import tqdm
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--username', help='Your Plex username',
                        default=CONFIG.get('auth.myplex_username'))
    parser.add_argument('-p', '--password', help='Your Plex password',
                        default=CONFIG.get('auth.myplex_password'))
    parser.add_argument('--url', default=None, help='Download from URL (only paste after !)')
    opts = parser.parse_args()
    # Search item to download
    account = utils.getMyPlexAccount(opts)
    items = search_for_item(opts.url)
    for i in items:
        for z in i.media:
            for f in z.parts:
                try:
                    # lets see if we can get the file without using pms.
                    if os.path.exists(f.file):
                        size = os.path.getsize(f.file)
                        bar = tqdm(unit='B', unit_scale=True, total=size)

                        def copy(src, dest, length=16 * 1024):
                            try:
                                fdest = os.path.join(dest, os.path.basename(src))
                                with open(src, 'rb') as f_from:
                                    with open(fdest, 'wb') as to:
                                        while True:
                                            buf = f_from.read(length)
                                            bar.update(length)
                                            if not buf:
                                                break
                                            to.write(buf)

                                return fdest
                            except Exception as e:
                                raise IOError
                            finally:
                                bar.close()

                        copy(f.file, os.getcwd())

                    else:
                        raise IOError

                except IOError as e:
                    print('Downloading from pms')
                    # We do this manually since we dont want to add a progress to Episode etc
                    filename = '%s.%s' % (i._prettyfilename(), f.container)
                    url = i._server.url('%s?download=1' % f.key)
                    filepath = utils.download(url, filename=filename, savepath=os.getcwd(),
                                              session=i._server._session, showstatus=True)
                    print('  %s' % filepath)


