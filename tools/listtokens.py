#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from getpass import getpass
from plexapi.exceptions import BadRequest
from plexapi.myplex import MyPlexAccount, MyPlexResource


if __name__ == '__main__':
    username = input('What is your plex.tv username: ')
    password = getpass('What is your plex.tv password: ')
    try:
        print('\nLogging into plex.tv..')
        account = MyPlexAccount(username, password)
        print('Fetching resources from: %s\n' % MyPlexResource.key)
        count = 0
        for resource in account.resources():
            if resource.accessToken:
                print('%s  %s' % (resource.accessToken, resource.name))
                count += 1
        if not count:
            print('Did not found any resources on your account.')
    except BadRequest as err:
        print('Unable to login to plex.tv: %s' % err)
