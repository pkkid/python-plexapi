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
from utils import fetch_server, iter_tests


def example_001_list_all_unwatched_content(plex):
    """ Example 1: List all unwatched content in library """
    for section in plex.library.sections():
        print 'Unwatched content in %s:' % section.title
        for video in section.unwatched():
            print '  %s' % video.title


def example_002_mark_all_conan_episodes_watched(plex):
    """ Example 2: Mark all Conan episodes watched. """
    plex.library.get('Conan (2010)').markWatched()


def example_003_list_all_clients(plex):
    """ Example 3: List all Clients connected to the Server. """
    for client in plex.clients():
        print client.name


def example_004_play_avatar_on_iphone(plex):
    """ Example 4: Play the Movie Avatar on my iPhone. """
    avatar = plex.library.section('Movies').get('Avatar')
    client = plex.client("Michael's iPhone")
    client.playMedia(avatar)


def example_005_search(plex):
    """ Example 5: List all content with the word 'Game' in the title. """
    for video in plex.search('Game'):
        print '%s (%s)' % (video.title, video.TYPE)


def example_006_follow_the_talent(plex):
    """ Example 6: List all movies directed by the same person as Jurassic Park. """
    jurassic_park = plex.library.section('Movies').get('Jurassic Park')
    director = jurassic_park.directors[0]
    for movie in director.related():
        print movie.title


def example_007_list_files(plex):
    """ Example 7: List files for the latest episode of Friends. """
    the_last_one = plex.library.section('TV Shows').get('Friends').episodes()[-1]
    for part in the_last_one.iter_parts():
        print part.file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run PlexAPI examples.')
    parser.add_argument('-s', '--server', help='Name of the Plex server (requires user/pass).')
    parser.add_argument('-u', '--username', help='Username for the Plex server.')
    parser.add_argument('-p', '--password', help='Password for the Plex server.')
    parser.add_argument('-n', '--name', help='Only run tests containing this string. Leave blank to run all examples.')
    args = parser.parse_args()
    plex = fetch_server(args)
    for example in iter_tests(__name__, args):
        example(plex)
        