# -*- coding: utf-8 -*-
"""
PlexAPI Examples
As of Plex version 0.9.11 I noticed that you must be logged in
to browse even the plex server locatewd at localhost. You can
run this example suite with the following command:

>> python examples.py -u <USERNAME> -p <PASSWORD> -s <SERVERNAME>
"""
import argparse, sys
from collections import defaultdict
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
from utils import fetch_server, iter_tests, register


@register()
def list_unwatched_movies(plex):
    """ Example 1: List all unwatched movies. """
    movies = plex.library.section('Movies')
    for video in movies.search(unwatched=True, maxresults=10, sort='addedAt:desc'):
        print('  %s' % video.title)


@register()
def mark_all_friends_episodes_watched(plex):
    """ Example 2: Mark all Friends episodes watched. """
    plex.library.section('TV Shows').get('Friends').markWatched()


@register()
def list_connected_clients(plex):
    """ Example 3: List clients connected to the server. """
    for client in plex.clients():
        print(client.title)


@register()
def play_avatar_on_client(plex):
    """ Example 4: Play the Movie Avatar on my iPhone.
        Note: Client must be on same network as server.
    """
    avatar = plex.library.section('Movies').get('Avatar')
    client = plex.client('iphone-mike')
    client.playMedia(avatar)


@register()
def list_animated_movies(plex):
    """ Example 5: List all animated movies from the 90s. """
    movies = plex.library.section('Movies')
    for video in movies.search(genre='animation', decade=1990):
        print('  %s (%s)' % (video.title, video.year))


@register()
def follow_the_talent(plex):
    """ Example 6: List all movies directed by the same person as Jurassic Park. """
    movies = plex.library.section('Movies')
    jurassic_park = movies.get('Jurassic Park')
    for movie in movies.search(director=jurassic_park.directors):
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
    print('vlc "%s"' % jurassic_park.getStreamURL(videoResolution='800x600'))
    

@register()
def most_streamed_titles(plex):
    """ Example 9: List the most played movies. """
    popular = defaultdict(int)
    for item in plex.history():
        if item.TYPE == 'movie':
            popular[item.title] += 1
    popular = sorted(popular.items(), key=lambda x:x[1], reverse=True)
    for title, count in popular[:5]:
        print('%s (%s plays)' % (title, count))
        

@register()
def most_active_users(plex):
    """ Example 10: List the most active users. """
    users = defaultdict(int)
    for item in plex.history():
        print(item.TYPE)
        users[item.username] += 1
    users = sorted(users.items(), key=lambda x:x[1], reverse=True)
    for user, count in users[:5]:
        print('%s (%s plays)' % (user, count))
    

if __name__ == '__main__':
    # There are three ways to authenticate:
    #  1. If the server is running on localhost, just run without any auth.
    #  2. Pass in --username, --password, and --resource.
    #  3. Pass in --baseurl, --token
    parser = argparse.ArgumentParser(description='Run PlexAPI examples.')
    parser.add_argument('-u', '--username', help='Username for your MyPlex account.')
    parser.add_argument('-p', '--password', help='Password for your MyPlex account.')
    parser.add_argument('-r', '--resource', help='Name of the Plex resource (requires user/pass).')
    parser.add_argument('-b', '--baseurl', help='Baseurl needed for auth token authentication')
    parser.add_argument('-t', '--token', help='Auth token (instead of user/pass)')
    parser.add_argument('-q', '--example', help='Only run the specified example.')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print verbose logging.')
    args = parser.parse_args()
    plex, account = fetch_server(args)
    for example in iter_tests(args.example):
        example['func'](plex)
