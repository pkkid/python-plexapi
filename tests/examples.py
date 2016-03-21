# -*- coding: utf-8 -*-
"""
PlexAPI Examples
As of Plex version 0.9.11 I noticed that you must be logged in
to browse even the plex server locatewd at localhost. You can
run this example suite with the following command:

>> python examples.py -u <USERNAME> -p <PASSWORD> -s <SERVERNAME>
"""
import argparse, sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
from utils import fetch_server, iter_tests, register


@register()
def list_all_unwatched_content(plex):
    """ Example 1: List all unwatched content in library """
    for section in plex.library.sections():
        print('Unwatched content in %s:' % section.title)
        for video in section.unwatched():
            print('  %s' % video.title)


@register()
def mark_all_conan_episodes_watched(plex):
    """ Example 2: Mark all Friends episodes watched. """
    plex.library.section('TV Shows').get('Friends').markWatched()


@register()
def list_all_clients(plex):
    """ Example 3: List all Clients connected to the Server. """
    for client in plex.clients():
        print(client.name)
    else:
        print('No clients')


@register()
def play_avatar_on_iphone(plex):
    """ Example 4: Play the Movie Avatar on my iPhone.
        Note: Client must be on same network as server.
    """
    avatar = plex.library.section('Movies').get('Avatar')
    client = plex.client("iphone-mike")
    client.playMedia(avatar)


@register()
def search(plex):
    """ Example 5: List all content with the word 'Game' in the title. """
    for video in plex.search('Game'):
        print('%s (%s)' % (video.title, video.TYPE))


@register()
def follow_the_talent(plex):
    """ Example 6: List all movies directed by the same person as Jurassic Park. """
    movies = plex.library.section('Movies')
    jurassic_park = movies.get('Jurassic Park')
    director = jurassic_park.directors[0]
    for movie in movies.search(None, director=director):
        print(movie.title)


@register()
def list_files(plex):
    """ Example 7: List files for the latest episode of Friends. """
    thelastone = plex.library.section('TV Shows').get('Friends').episodes()[-1]
    for part in thelastone.iterParts():
        print(part.file)


@register()
def get_stream_url(plex):
    """ Example 8: Get a URL you can open in VLC, MPV, etc. """
    jurassic_park = plex.library.section('Movies').get('Jurassic Park')
    print('Try running the following command:')
    print('vlc "%s"' % jurassic_park.getStreamUrl(videoResolution='800x600'))


if __name__ == '__main__':
    # There are three ways to authenticate:
    #  1. If the server is running on localhost, just run without any auth.
    #  2. Pass in --username, --password, and --resource.
    #  3. Pass in --baseuri, --token
    parser = argparse.ArgumentParser(description='Run PlexAPI examples.')
    parser.add_argument('--username', help='Username for the Plex server.')
    parser.add_argument('--password', help='Password for the Plex server.')
    parser.add_argument('--resource', help='Name of the Plex resource (requires user/pass).')
    parser.add_argument('--baseuri', help='Baseuri needed for auth token authentication')
    parser.add_argument('--token', help='Auth token (instead of user/pass)')
    parser.add_argument('--example', help='Only run the specified example.')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print verbose logging.')
    args = parser.parse_args()
    plex, user = fetch_server(args)
    for example in iter_tests(args.example):
        example['func'](plex)
