# -*- coding: utf-8 -*-
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
from utils import log, register, safe_client, run_tests
from plexapi.myplex import MyPlexUser
from plexapi.utils import NA

SHOW_SECTION = 'TV Shows'
SHOW_TITLE = 'Game of Thrones'
SHOW_SEASON = 'Season 1'
SHOW_EPISODE = 'Winter Is Coming'
MOVIE_SECTION = 'Movies'
MOVIE_TITLE = 'Jurassic World'
AUDIO_SECTION = 'Music'
AUDIO_ARTIST = 'Beastie Boys'
AUDIO_ALBUM = 'Licensed To Ill'
AUDIO_TRACK = 'Brass Monkey'
CLIENT = 'pkkid-home'
CLIENT_BASEURL = 'http://192.168.1.131:3005'


#-----------------------
# Core
#-----------------------

@register('core,server')
def test_server(plex, user=None):
    log(2, 'Username: %s' % plex.myPlexUsername)
    log(2, 'Platform: %s' % plex.platform)
    log(2, 'Version: %s' % plex.version)
    assert plex.myPlexUsername is not None, 'Unknown username.'
    assert plex.platform is not None, 'Unknown platform.'
    assert plex.version is not None, 'Unknown version.'


@register('core')
def test_list_sections(plex, user=None):
    sections = [s.title for s in plex.library.sections()]
    log(2, 'Sections: %s' % sections)
    assert SHOW_SECTION in sections, '%s not a library section.' % SHOW_SECTION
    assert MOVIE_SECTION in sections, '%s not a library section.' % MOVIE_SECTION
    plex.library.section(SHOW_SECTION)
    plex.library.section(MOVIE_SECTION)


#-----------------------
# Search
#-----------------------

@register('search,show')
def test_search_show(plex, user=None):
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
    

@register('search,show')
def test_search_with_apostrophe(plex, user=None):
    show_title = "Marvel's Daredevil"  # Test ' in show title
    result_server = plex.search(show_title)
    result_shows = plex.library.section(SHOW_SECTION).search(show_title)
    log(2, 'Searching for: %s' % SHOW_TITLE)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Shows: %s' % result_shows)
    assert result_server, 'Show not found.'
    assert result_server == result_shows, 'Show searches not consistent.'


@register('search,movie')
def test_search_movie(plex, user=None):
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
    

@register('search,audio')
def test_search_audio(plex, user=None):
    result_server = plex.search(AUDIO_ARTIST)
    result_library = plex.library.search(AUDIO_ARTIST)
    result_music = plex.library.section(AUDIO_SECTION).search(AUDIO_ARTIST)
    log(2, 'Searching for: %s' % AUDIO_ARTIST)
    log(4, 'Result Server: %s' % result_server)
    log(4, 'Result Library: %s' % result_library)
    log(4, 'Result Music: %s' % result_music)
    assert result_server, 'Artist not found.'
    assert result_server == result_library == result_music, 'Audio searches not consistent.'
    

@register('search,audio')
def test_search_related(plex, user=None):
    movies = plex.library.section(MOVIE_SECTION)
    movie = movies.get(MOVIE_TITLE)
    related_by_actors = movies.search(actor=movie.actors, maxresults=3)
    log(2, u'Actors: %s..' % movie.actors)
    log(2, u'Related by Actors: %s..' % related_by_actors)
    assert related_by_actors, 'No related movies found by actor.'
    related_by_genre = movies.search(genre=movie.genres, maxresults=3)
    log(2, u'Genres: %s..' % movie.genres)
    log(2, u'Related by Genre: %s..' % related_by_genre)
    assert related_by_genre, 'No related movies found by genre.'
    related_by_director = movies.search(director=movie.directors, maxresults=3)
    log(2, 'Directors: %s..' % movie.directors)
    log(2, 'Related by Director: %s..' % related_by_director)
    assert related_by_director, 'No related movies found by director.'
    

@register('search,show')
def test_crazy_search(plex, user=None):
    movies = plex.library.section(MOVIE_SECTION)
    movie = movies.get('Jurassic World')
    log(2, u'Search by Actor: "Chris Pratt"')
    assert movie in movies.search(actor='Chris Pratt'), 'Unable to search movie by actor.'
    log(2, u'Search by Director: ["Trevorrow"]')
    assert movie in movies.search(director=['Trevorrow']), 'Unable to search movie by director.'
    log(2, u'Search by Year: ["2014", "2015"]')
    assert movie in movies.search(year=['2014', '2015']), 'Unable to search movie by year.'
    log(2, u'Filter by Year: 2014')
    assert movie not in movies.search(year=2014), 'Unable to filter movie by year.'
    judy = [a for a in movie.actors if 'Judy' in a.tag][0]
    log(2, u'Search by Unpopular Actor: %s' % judy)
    assert movie in movies.search(actor=judy.id), 'Unable to filter movie by year.'


#-----------------------
# Library Navigation
#-----------------------

@register('navigate,movie,show')
def test_navigate_to_movie(plex, user=None):
    result_library = plex.library.get(MOVIE_TITLE)
    result_movies = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    log(2, 'Navigating to: %s' % MOVIE_TITLE)
    log(2, 'Result Library: %s' % result_library)
    log(2, 'Result Movies: %s' % result_movies)
    assert result_movies, 'Movie navigation not working.'
    assert result_library == result_movies, 'Movie navigation not consistent.'


@register('navigate,movie,show')
def test_navigate_to_show(plex, user=None):
    result_shows = plex.library.section(SHOW_SECTION).get(SHOW_TITLE)
    log(2, 'Navigating to: %s' % SHOW_TITLE)
    log(2, 'Result Shows: %s' % result_shows)
    assert result_shows, 'Show navigation not working.'


@register('navigate,show')
def test_navigate_around_show(plex, user=None):
    show = plex.library.section(SHOW_SECTION).get(SHOW_TITLE)
    seasons = show.seasons()
    season = show.season(SHOW_SEASON)
    episodes = show.episodes()
    episode = show.episode(SHOW_EPISODE)
    log(2, 'Navigating around show: %s' % show)
    log(2, 'Seasons: %s...' % seasons[:3])
    log(2, 'Season: %s' % season)
    log(2, 'Episodes: %s...' % episodes[:3])
    log(2, 'Episode: %s' % episode)
    assert SHOW_SEASON in [s.title for s in seasons], 'Unable to list season: %s' % SHOW_SEASON
    assert SHOW_EPISODE in [e.title for e in episodes], 'Unable to list episode: %s' % SHOW_EPISODE
    assert show.season(SHOW_SEASON) == season, 'Unable to get show season: %s' % SHOW_SEASON
    assert show.episode(SHOW_EPISODE) == episode, 'Unable to get show episode: %s' % SHOW_EPISODE
    assert season.episode(SHOW_EPISODE) == episode, 'Unable to get season episode: %s' % SHOW_EPISODE
    assert season.show() == show, 'season.show() doesnt match expected show.'
    assert episode.show() == show, 'episode.show() doesnt match expected show.'
    assert episode.season() == season, 'episode.season() doesnt match expected season.'


@register('navigate,audio')
def test_navigate_around_artist(plex, user=None):
    artist = plex.library.section(AUDIO_SECTION).get(AUDIO_ARTIST)
    albums = artist.albums()
    album = artist.album(AUDIO_ALBUM)
    tracks = artist.tracks()
    track = artist.track(AUDIO_TRACK)
    log(2, 'Navigating around artist: %s' % artist)
    log(2, 'Albums: %s...' % albums[:3])
    log(2, 'Album: %s' % album)
    log(2, 'Tracks: %s...' % tracks[:3])
    log(2, 'Track: %s' % track)
    assert AUDIO_ALBUM in [a.title for a in albums], 'Unable to list album: %s' % AUDIO_ALBUM
    assert AUDIO_TRACK in [e.title for e in tracks], 'Unable to list track: %s' % AUDIO_TRACK
    assert artist.album(AUDIO_ALBUM) == album, 'Unable to get artist album: %s' % AUDIO_ALBUM
    assert artist.track(AUDIO_TRACK) == track, 'Unable to get artist track: %s' % AUDIO_TRACK
    assert album.track(AUDIO_TRACK) == track, 'Unable to get album track: %s' % AUDIO_TRACK
    assert album.artist() == artist, 'album.artist() doesnt match expected artist.'
    assert track.artist() == artist, 'track.artist() doesnt match expected artist.'
    assert track.album() == album, 'track.album() doesnt match expected album.'


#-----------------------
# Library Actions
#-----------------------

@register('action,movie')
def test_mark_movie_watched(plex, user=None):
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


@register('action')
def test_refresh_section(plex, user=None):
    shows = plex.library.section(MOVIE_SECTION)
    shows.refresh()
    

@register('action,movie')
def test_refresh_video(plex, user=None):
    result = plex.search(MOVIE_TITLE)
    result[0].refresh()


#-----------------------
# Metadata
#-----------------------

@register('meta,movie')
def test_partial_video(plex, user=None):
    movie_title = 'Bedside Detective'
    result = plex.search(movie_title)
    log(2, 'Title: %s' % result[0].title)
    log(2, 'Original Title: %s' % result[0].originalTitle)
    assert(result[0].originalTitle != NA)


@register('meta,movie,show')
def test_list_media_files(plex, user=None):
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


@register('meta,movie')
def test_list_video_tags(plex, user=None):
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


@register('client')
def test_list_video_streams(plex, user=None):
    movie = plex.library.section(MOVIE_SECTION).get('John Wick')
    videostreams = [s.language for s in movie.videoStreams]
    audiostreams = [s.language for s in movie.audioStreams]
    subtitlestreams = [s.language for s in movie.subtitleStreams]
    log(2, 'Video Streams: %s' % ', '.join(videostreams[0:5]))
    log(2, 'Audio Streams: %s' % ', '.join(audiostreams[0:5]))
    log(2, 'Subtitle Streams: %s' % ', '.join(subtitlestreams[0:5]))
    assert filter(None, videostreams), 'No video streams listed for movie.'
    assert filter(None, audiostreams), 'No audio streams listed for movie.'
    assert filter(None, subtitlestreams), 'No subtitle streams listed for movie.'


@register('meta,audio')
def test_list_audio_tags(plex, user=None):
    section = plex.library.section(AUDIO_SECTION)
    artist = section.get(AUDIO_ARTIST)
    track = artist.get(AUDIO_TRACK)
    log(2, 'Countries: %s' % artist.countries[0:3])
    log(2, 'Genres: %s' % artist.genres[0:3])
    log(2, 'Similar: %s' % artist.similar[0:3])
    log(2, 'Album Genres: %s' % track.album().genres[0:3])
    log(2, 'Moods: %s' % track.moods[0:3])
    log(2, 'Media: %s' % track.media[0:3])
    assert filter(None, artist.countries), 'No countries listed for artist.'
    assert filter(None, artist.genres), 'No genres listed for artist.'
    assert filter(None, artist.similar), 'No similar artists listed.'
    assert filter(None, track.album().genres), 'No genres listed for album.'
    assert filter(None, track.moods), 'No moods listed for track.'
    assert filter(None, track.media), 'No media listed for track.'


@register('meta,show')
def test_is_watched(plex, user=None):
    show = plex.library.section(SHOW_SECTION).get(SHOW_TITLE)
    episode = show.get(SHOW_EPISODE)
    log(2, '%s isWatched: %s' % (episode.title, episode.isWatched))
    movie = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    log(2, '%s isWatched: %s' % (movie.title, movie.isWatched))


@register('meta,movie')
def test_fetch_details_not_in_search_result(plex, user=None):
    # Search results only contain 3 actors per movie. This text checks there
    # are more than 3 results in the actor list (meaning it fetched the detailed
    # information behind the scenes).
    result = plex.search(MOVIE_TITLE)[0]
    actors = result.actors
    assert len(actors) >= 4, 'Unable to fetch detailed movie information'
    log(2, '%s actors found.' % len(actors))


@register('movie,audio')
def test_stream_url(plex, user=None):
    movie = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    episode = plex.library.section(SHOW_SECTION).get(SHOW_TITLE).episodes()[-1]
    track = plex.library.section(AUDIO_SECTION).get(AUDIO_ARTIST).get(AUDIO_TRACK)
    log(2, 'Movie: vlc "%s"' % movie.getStreamURL())
    log(2, 'Episode: vlc "%s"' % episode.getStreamURL())
    log(2, 'Track: cvlc "%s"' % track.getStreamURL())
    

#-----------------------
# Play Queue
#-----------------------

@register('queue')
def test_play_queues(plex, user=None):
    episode = plex.library.section(SHOW_SECTION).get(SHOW_TITLE).get(SHOW_EPISODE)
    playqueue = plex.createPlayQueue(episode)
    assert len(playqueue.items) == 1, 'No items in play queue.'
    assert playqueue.items[0].title == SHOW_EPISODE, 'Wrong show queued.'
    assert playqueue.playQueueID, 'Play queue ID not set.'


#-----------------------
# Client
#-----------------------

@register('client')
def test_list_clients(plex, user=None):
    clients = [c.title for c in plex.clients()]
    log(2, 'Clients: %s' % ', '.join(clients or []))
    assert clients, 'Server is not listing any clients.'


@register('client')
def test_client_navigation(plex, user=None):
    client = safe_client(CLIENT, CLIENT_BASEURL, plex)
    _navigate(plex, client)
    

@register('client,proxy')
def test_client_navigation_via_proxy(plex, user=None):
    client = safe_client(CLIENT, CLIENT_BASEURL, plex)
    client.proxyThroughServer()
    _navigate(plex, client)


def _navigate(plex, client):
    episode = plex.library.section(SHOW_SECTION).get(SHOW_TITLE).get(SHOW_EPISODE)
    artist = plex.library.section(AUDIO_SECTION).get(AUDIO_ARTIST)
    log(2, 'Client: %s (%s)' % (client.title, client.product))
    log(2, 'Capabilities: %s' % client.protocolCapabilities)
    # Move around a bit
    log(2, 'Browsing around..')
    client.moveDown(); time.sleep(0.5)
    client.moveDown(); time.sleep(0.5)
    client.moveDown(); time.sleep(0.5)
    client.select(); time.sleep(3)
    client.moveRight(); time.sleep(0.5)
    client.moveRight(); time.sleep(0.5)
    client.moveLeft(); time.sleep(0.5)
    client.select(); time.sleep(3)
    client.goBack(); time.sleep(1)
    client.goBack(); time.sleep(3)
    # Go directly to media
    log(2, 'Navigating to %s..' % episode.title)
    client.goToMedia(episode); time.sleep(5)
    log(2, 'Navigating to %s..' % artist.title)
    client.goToMedia(artist); time.sleep(5)
    log(2, 'Navigating home..')
    client.goToHome(); time.sleep(5)
    client.moveUp(); time.sleep(0.5)
    client.moveUp(); time.sleep(0.5)
    client.moveUp(); time.sleep(0.5)
    # Show context menu
    client.contextMenu(); time.sleep(3)
    client.goBack(); time.sleep(5)


@register('client')
def test_video_playback(plex, user=None):
    client = safe_client(CLIENT, CLIENT_BASEURL, plex)
    _video_playback(plex, client)


@register('client,proxy')
def test_video_playback_via_proxy(plex, user=None):
    client = safe_client(CLIENT, CLIENT_BASEURL, plex)
    client.proxyThroughServer()
    _video_playback(plex, client)


def _video_playback(plex, client):
    mtype = 'video'
    movie = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    subs = [s for s in movie.subtitleStreams if s.language == 'English']
    log(2, 'Client: %s (%s)' % (client.title, client.product))
    log(2, 'Capabilities: %s' % client.protocolCapabilities)
    log(2, 'Playing to %s..' % movie.title)
    client.playMedia(movie); time.sleep(5)
    log(2, 'Pause..')
    client.pause(mtype); time.sleep(2)
    log(2, 'Step Forward..')
    client.stepForward(mtype); time.sleep(5)
    log(2, 'Play..')
    client.play(mtype); time.sleep(3)
    log(2, 'Seek to 10m..')
    client.seekTo(10*60*1000); time.sleep(5)
    log(2, 'Disable Subtitles..')
    client.setSubtitleStream(0, mtype); time.sleep(10)
    log(2, 'Load English Subtitles %s..' % subs[0].id)
    client.setSubtitleStream(subs[0].id, mtype); time.sleep(10)
    log(2, 'Stop..')
    client.stop(mtype); time.sleep(1)


@register('client')
def test_client_timeline(plex, user=None):
    client = safe_client(CLIENT, CLIENT_BASEURL, plex)
    _test_timeline(plex, client)


@register('client,proxy')
def test_client_timeline_via_proxy(plex, user=None):
    client = safe_client(CLIENT, CLIENT_BASEURL, plex)
    client.proxyThroughServer()
    _test_timeline(plex, client)


def _test_timeline(plex, client):
    mtype = 'video'
    client = safe_client(CLIENT, CLIENT_BASEURL, plex)
    movie = plex.library.section(MOVIE_SECTION).get(MOVIE_TITLE)
    time.sleep(30)  # previous test may have played media..
    playing = client.isPlayingMedia()
    log(2, 'Playing Media: %s' % playing)
    assert playing is False, 'isPlayingMedia() should have returned False.'
    client.playMedia(movie); time.sleep(30)
    playing = client.isPlayingMedia()
    log(2, 'Playing Media: %s' % playing)
    assert playing is True, 'isPlayingMedia() should have returned True.'
    client.stop(mtype); time.sleep(30)
    playing = client.isPlayingMedia()
    log(2, 'Playing Media: %s' % playing)
    assert playing is False, 'isPlayingMedia() should have returned False.'


# TODO: MAKE THIS WORK..
# @register('client')
def test_sync_items(plex, user=None):
    user = MyPlexUser('user', 'pass')
    device = user.getDevice('device-uuid')
    # fetch the sync items via the device sync list
    for item in device.sync_items():
        # fetch the media object associated with the sync item
        for video in item.get_media():
            # fetch the media parts (actual video/audio streams) associated with the media
            for part in video.iterParts():
                print('Found media to download!')
                # make the relevant sync id (media part) as downloaded
                # this tells the server that this device has successfully downloaded this media part of this sync item
                item.mark_as_done(part.sync_id)


#-----------------------
# MyPlex Resources
#-----------------------

@register('myplex,resource')
def test_myplex_resources(plex, user=None):
    assert user, 'Must specify username, password & resource to run this test.'
    resources = user.resources()
    for resource in resources:
        name = resource.name or 'Unknown'
        connections = [c.uri for c in resource.connections]
        connections = ', '.join(connections) if connections else 'None'
        log(2, '%s (%s): %s' % (name, resource.product, connections))
    assert resources, 'No resources found for user: %s' % user.name
    

@register('myplex,devices')
def test_myplex_devices(plex, user=None):
    assert user, 'Must specify username, password & resource to run this test.'
    devices = user.devices()
    for device in devices:
        name = device.name or 'Unknown'
        connections = ', '.join(device.connections) if device.connections else 'None'
        log(2, '%s (%s): %s' % (name, device.product, connections))
    assert devices, 'No devices found for user: %s' % user.name
    

@register('myplex,devices')
def test_myplex_connect_to_device(plex, user=None):
    assert user, 'Must specify username, password & resource to run this test.'
    devices = user.devices()
    for device in devices:
        if device.name == CLIENT and len(device.connections):
            break
    client = device.connect()
    log(2, 'Connected to client: %s (%s)' % (client.title, client.product))
    assert client, 'Unable to connect to device'


if __name__ == '__main__':
    # There are three ways to authenticate:
    #  1. If the server is running on localhost, just run without any auth.
    #  2. Pass in --username, --password, and --resource.
    #  3. Pass in --baseurl, --token
    parser = argparse.ArgumentParser(description='Run PlexAPI tests.')
    parser.add_argument('-u', '--username', help='Username for the Plex server.')
    parser.add_argument('-p', '--password', help='Password for the Plex server.')
    parser.add_argument('-r', '--resource', help='Name of the Plex resource (requires user/pass).')
    parser.add_argument('-b', '--baseurl', help='Baseurl needed for auth token authentication')
    parser.add_argument('-t', '--token', help='Auth token (instead of user/pass)')
    parser.add_argument('-q', '--query', help='Only run the specified tests.')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print verbose logging.')
    args = parser.parse_args()
    run_tests(__name__, args)
