#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-GetToken is a simple method to retrieve a Plex account token.
"""
from getpass import getpass
from plexapi.exceptions import TwoFactorRequired
from plexapi.myplex import MyPlexAccount

username = input("Plex username: ")
password = getpass("Plex password: ")

try:
    account = MyPlexAccount(username, password)
except TwoFactorRequired:
    code = input("Plex 2FA code: ")
    account = MyPlexAccount(username, password, code=code)

print(account.authenticationToken)
