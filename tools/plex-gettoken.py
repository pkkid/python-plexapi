#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-GetToken is a simple method to retrieve a Plex account token.
"""
from getpass import getpass
from plexapi.myplex import MyPlexAccount

username = input("Plex username: ")
password = getpass("Plex password: ")
code = input("Plex 2FA code (leave blank for none): ")

account = MyPlexAccount(username, password, code=code)
print(account.authenticationToken)
