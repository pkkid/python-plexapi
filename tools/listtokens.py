#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from getpass import getpass
from plexapi.exceptions import BadRequest
from plexapi.myplex import MyPlexAccount, MyPlexResource


if __name__ == '__main__':
    print('List Plex Tokens')
    print('----------------')
    print('This is a simple utility to fetch and list all known Plex Server')
    print('tokens your plex.tv account has access to. Because this information')
    print('comes from the plex.tv website, we need to ask for your username')
    print('and password. Alternatively, if you do not wish to enter your login')
    print('information below, you can retrieve the same information from plex.tv')
    print('directly at the URL: %s\n' % MyPlexResource.key)
    username = input('What is your plex.tv username: ')
    password = getpass('What is your plex.tv password: ')
    try:
        count = 0; print()
        for resource in MyPlexAccount(username, password).resources():
            if resource.accessToken:
                print('%s  %s' % (resource.accessToken, resource.name))
                count += 1
        if not count:
            print('Did not found any resources on your account.')
    except BadRequest as err:
        print('Unable to login to plex.tv: %s' % err)
