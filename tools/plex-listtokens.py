#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-ListTokens is a simple utility to fetch and list all known Plex
Server tokens your plex.tv account has access to. Because this information
comes from the plex.tv website, we need to ask for your username
and password. Alternatively, if you do not wish to enter your login
information below, you can retrieve the same information from plex.tv
at the URL: https://plex.tv/api/resources?includeHttps=1
"""
from getpass import getpass
from plexapi import utils
from plexapi.exceptions import BadRequest
from plexapi.myplex import MyPlexAccount, _connect
from plexapi.server import PlexServer

FORMAT = '  %-17s  %-25s  %-20s  %s'
FORMAT2 = '  %-17s  %-25s  %-20s  %-30s  (%s)'
SERVER = 'Plex Media Server'


def _list_resources(account, servers):
    print('\nHTTPS Resources:')
    resources = MyPlexAccount(username, password).resources()
    for r in resources:
        if r.accessToken:
            for connection in r.connections:
                print(FORMAT % (r.product, r.name, r.accessToken, connection.uri))
                servers[connection.uri] = r.accessToken
    print('\nDirect Resources:')
    for r in resources:
        if r.accessToken:
            for connection in r.connections:
                print(FORMAT % (r.product, r.name, r.accessToken, connection.httpuri))
                servers[connection.httpuri] = r.accessToken


def _list_devices(account, servers):
    print('\nDevices:')
    for d in MyPlexAccount(username, password).devices():
        if d.token:
            for conn in d.connections:
                print(FORMAT % (d.product, d.name, d.token, conn))
                servers[conn] = d.token


def _test_servers(servers):
    seen = set()
    print('\nServer Clients:')
    listargs = [[PlexServer, s, t, 5] for s,t in servers.items()]
    results = utils.threaded(_connect, listargs)
    for url, token, plex, runtime in results:
        clients = plex.clients() if plex else []
        if plex and clients:
            for c in plex.clients():
                if c._baseurl not in seen:
                    print(FORMAT2 % (c.product, c.title, token, c._baseurl, plex.friendlyName))
                    seen.add(c._baseurl)


if __name__ == '__main__':
    print(__doc__)
    username = input('What is your plex.tv username: ')
    password = getpass('What is your plex.tv password: ')
    try:
        servers = {}
        account = MyPlexAccount(username, password)
        _list_resources(account, servers)
        _list_devices(account, servers)
        _test_servers(servers)
    except BadRequest as err:
        print('Unable to login to plex.tv: %s' % err)
