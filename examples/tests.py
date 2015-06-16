"""
Test Library Functions

As of Plex version 0.9.11 I noticed that you must be logged in
to browse even the plex server locatewd at localhost. You can
run this test suite with the following command:

>> python tests.py -u <USERNAME> -p <PASSWORD> -s <SERVERNAME>
"""
import argparse, sys, time
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
from utils import log, run_tests

SHOW_SECTION = 'TV Shows'
SHOW_TITLE = 'Game of Thrones'
SHOW_SEASON = 'Season 1'
SHOW_EPISODE = 'Winter Is Coming'
MOVIE_SECTION = 'Movies'
MOVIE_TITLE = 'Jurassic Park'
PLEX_CLIENT = "Michael's iPhone"


def test_001_server(plex, user=None):
    log(2, 'Username: %s' % plex.myPlexUsername)
    log(2, 'Platform: %s' % plex.platform)
    log(2, 'Version: %s' % plex.version)
    assert plex.myPlexUsername is not None, 'Unknown username.'
    assert plex.platform is not None, 'Unknown platform.'
    assert plex.version is not None, 'Unknown version.'


def test_002_list_sections(plex, user=None):
    sections = [s.title for s in plex.library.sections()]
    log(2, 'Sections: %s' % sections)
    assert SHOW_SECTION in sections, '%s not a library section.' % SHOW_SECTION
    assert MOVIE_SECTION in sections, '%s not a library section.' % MOVIE_SECTION
    plex.library.section(SHOW_SECTION)
    plex.library.section(MOVIE_SECTION)


def test_003_search_show(plex, user=None):
    result_server = plex.search(SHOW_TITLE)
    result_shows = plex.library.section(SHOW_SECTION).search(SHOW_TITLE)
    result_movies = plex.library.section(MOVIE_SECTION).search(SHOW_TITLE)
    log(2, 'Searching for: %s' % SHOW_TITLE)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Shows: %s' % result_shows)
    log(4, 'Result Movies: %s' % result_movies)
    assert result_server, 'Show not found.'
    assert result_server == result_shows, 'Show searches not consistent.'
    assert not result_movies, 'Movie search returned show title.'


def test_004_search_movie(plex, user=None):
    result_server = plex.search(MOVIE_TITLE)
    result_library = plex.library.search(MOVIE_TITLE)
    result_shows = plex.library.section(SHOW_SECTION).search(MOVIE_TITLE)
    result_movies = plex.library.section(MOVIE_SECTION).search(MOVIE_TITLE)
    log(2, 'Searching for: %s' % MOVIE_TITLE)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Library: %s' % result_library)
    log(4, 'Result Shows: %s' % result_shows)
    log(4, 'Result Movies: %s' % result_movies)
    assert result_server, 'Movie not found.'
    assert result_server == result_library == result_movies, 'Movie searches not consistent.'
    assert not result_shows, 'Show search returned show title.'


def test_005_navigate_to_show(plex, user=None):
    result_shows = plex.library.section(SHOW_SECTION).get(SHOW_TITLE)
    try:
        result_movies = plex.library.section(MOVIE_SECTION).get(SHOW_TITLE)
    except:
        result_movies = None
    log(2, 'Navigating to: %s' % SHOW_TITLE)
    log(4, 'Result Shows: %s' % result_shows)
    log(4, 'Result Movies: %s' % result_movies)
    assert result_shows, 'Show navigation not working.'
    assert not result_movies, 'Movie navigation returned show title.'


def test_006_navigate_to_movie(plex, user=None):
    result_library = plex.library.get(MOVIE_TITLE)
    result_movies = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    try:
        result_shows = plex.library.section(SHOW_SECTION).get(MOVIE_TITLE)
    except:
        result_shows = None
    log(2, 'Navigating to: %s' % MOVIE_TITLE)
    log(4, 'Result Library: %s' % result_library)
    log(4, 'Result Shows: %s' % result_shows)
    log(4, 'Result Movies: %s' % result_movies)
    assert result_library == result_movies, 'Movie navigation not consistent.'
    assert not result_shows, 'Show navigation returned show title.'


def test_007_navigate_around_show(plex, user=None):
    show = plex.library.section(SHOW_SECTION).get(SHOW_TITLE)
    seasons = show.seasons()
    season = show.season(SHOW_SEASON)
    episodes = show.episodes()
    episode = show.episode(SHOW_EPISODE)
    log(2, 'Navigating around show: %s' % show)
    log(4, 'Seasons: %s...' % seasons[:3])
    log(4, 'Season: %s' % season)
    log(4, 'Episodes: %s...' % episodes[:3])
    log(4, 'Episode: %s' % episode)
    assert SHOW_SEASON in [s.title for s in seasons], 'Unable to get season: %s' % SHOW_SEASON
    assert SHOW_EPISODE in [e.title for e in episodes], 'Unable to get episode: %s' % SHOW_EPISODE
    assert season.show() == show, 'season.show() doesnt match expected show.'
    assert episode.show() == show, 'episode.show() doesnt match expected show.'
    assert episode.season() == season, 'episode.season() doesnt match expected season.'


def test_008_mark_movie_watched(plex, user=None):
    movie = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    movie.markUnwatched()
    log(2, 'Marking movie watched: %s' % movie)
    log(2, 'View count: %s' % movie.viewCount)
    movie.markWatched()
    log(2, 'View count: %s' % movie.viewCount)
    assert movie.viewCount == 1, 'View count 0 after watched.'
    movie.markUnwatched()
    log(2, 'View count: %s' % movie.viewCount)
    assert movie.viewCount == 0, 'View count 1 after unwatched.'


def test_009_refresh(plex, user=None):
    shows = plex.library.section(MOVIE_SECTION)
    shows.refresh()


def test_010_playQueues(plex, user=None):
    episode = plex.library.section(SHOW_SECTION).get(SHOW_TITLE).get(SHOW_EPISODE)
    playqueue = plex.createPlayQueue(episode)
    assert len(playqueue.items) == 1, 'No items in play queue.'
    assert playqueue.items[0].title == SHOW_EPISODE, 'Wrong show queued.'
    assert playqueue.playQueueID, 'Play queue ID not set.'


def test_011_play_media(plex, user=None):
    # Make sure the client is turned on!
    episode = plex.library.section(SHOW_SECTION).get(SHOW_TITLE).get(SHOW_EPISODE)
    client = plex.client(PLEX_CLIENT)
    client.playMedia(episode)
    time.sleep(10)
    client.pause()
    time.sleep(3)
    client.stepForward()
    time.sleep(3)
    client.play()
    time.sleep(3)
    client.stop()
    time.sleep(3)
    movie = plex.library.get(MOVIE_TITLE)
    movie.play(client)
    time.sleep(10)
    client.stop()


def test_012_myplex_account(plex, user=None):
    account = plex.account()
    print(account.__dict__)


def test_013_list_media_files(plex, user=None):
    # Fetch file names from the tv show
    episode_files = []
    episode = plex.library.section(SHOW_SECTION).get(SHOW_TITLE).episodes()[-1]
    log(2, 'Episode Files: %s' % episode)
    for media in episode.media:
        for part in media.parts:
            log(4, part.file)
            episode_files.append(part.file)
    assert filter(None, episode_files), 'No show files have been listed.'
    # Fetch file names from the movie
    movie_files = []
    movie = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    log(2, 'Movie Files: %s' % movie)
    for media in movie.media:
        for part in media.parts:
            log(4, part.file)
            movie_files.append(part.file)
    assert filter(None, movie_files), 'No movie files have been listed.'


def test_014_list_video_tags(plex, user=None):
    movies = plex.library.section(MOVIE_SECTION)
    movie = movies.get(MOVIE_TITLE)
    log(2, 'Countries: %s' % movie.countries[0:3])
    log(2, 'Directors: %s' % movie.directors[0:3])
    log(2, 'Genres: %s' % movie.genres[0:3])
    log(2, 'Producers: %s' % movie.producers[0:3])
    log(2, 'Actors: %s' % movie.actors[0:3])
    log(2, 'Writers: %s' % movie.writers[0:3])
    assert filter(None, movie.countries), 'No countries listed for movie.'
    assert filter(None, movie.directors), 'No directors listed for movie.'
    assert filter(None, movie.genres), 'No genres listed for movie.'
    assert filter(None, movie.producers), 'No producers listed for movie.'
    assert filter(None, movie.actors), 'No actors listed for movie.'
    assert filter(None, movie.writers), 'No writers listed for movie.'
    log(2, 'List movies with same director: %s' % movie.directors[0])
    related = movies.search(None, director=movie.directors[0])
    log(4, related[0:3])
    assert movie in related, 'Movie was not found in related directors search.'


def test_015_list_devices(plex, user=None):
    assert user, 'Must specify username, password & resource to run this test.'
    for device in user.resources():
        log(2, device.name or device.product)


# def test_016_sync_items(plex, user=None):
#     user = MyPlexUser('user', 'pass')
#     device = user.getDevice('device-uuid')
#     # fetch the sync items via the device sync list
#     for item in device.sync_items():
#         # fetch the media object associated with the sync item
#         for video in item.get_media():
#             # fetch the media parts (actual video/audio streams) associated with the media
#             for part in video.iter_parts():
#                 print('Found media to download!')
#                 # make the relevant sync id (media part) as downloaded
#                 # this tells the server that this device has successfully downloaded this media part of this sync item
#                 item.mark_as_done(part.sync_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run PlexAPI tests.')
    parser.add_argument('-r', '--resource', help='Name of the Plex resource (requires user/pass).')
    parser.add_argument('-u', '--username', help='Username for the Plex server.')
    parser.add_argument('-p', '--password', help='Password for the Plex server.')
    parser.add_argument('-n', '--name', help='Only run tests containing this string. Leave blank to run all tests.')
    args = parser.parse_args()
    run_tests(__name__, args)
