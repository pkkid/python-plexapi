#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Allows downloading a Plex media item from a local or shared library. You
may specify the item by the PlexWeb url (everything after !) or by
manually searching the items from the command line wizard.

Original contribution by lad1337.
"""
import argparse, re
from plexapi import utils
from plexapi.compat import unquote
from plexapi.video import Episode, Movie, Show

VALID_TYPES = (Movie, Episode, Show)


def search_for_item(url=None):
    if url: return get_item_from_url(opts.url)
    server = utils.choose('Choose a Server', account.resources(), 'name').connect()
    query = input('What are you looking for?: ')
    items = [i for i in server.search(query) if i.__class__ in VALID_TYPES]
    item = utils.choose('Choose result', items, lambda x: '(%s) %s' % (x.type.title(), x.title[0:60]))
    if isinstance(item, Show):
        display = lambda i: '%s %s %s' % (i.grandparentTitle, i.seasonEpisode, i.title)
        item = utils.choose('Choose episode', item.episodes(), display)
    if not isinstance(item, (Movie, Episode)):
        raise SystemExit('Unable to download %s' % item.__class__.__name__)
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--username', help='Your Plex username')
    parser.add_argument('--password', help='Your Plex password')
    parser.add_argument('--url', default=None, help='Download from URL (only paste after !)')
    opts = parser.parse_args()
    # Search item to download
    account = utils.getMyPlexAccount(opts)
    item = search_for_item(opts.url)
    # Download the item
    print("Downloading '%s' from %s.." % (item._prettyfilename(), item._server.friendlyName))
    filepaths = item.download('./', showstatus=True)
    for filepath in filepaths:
        print('  %s' % filepath)
