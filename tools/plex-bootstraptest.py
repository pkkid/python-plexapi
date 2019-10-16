#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The script is used to bootstrap a docker container with Plex and with
all the libraries required for testing.
"""
import argparse
import os
import plexapi
import socket
import time
import zipfile
from glob import glob
from shutil import copyfile, rmtree
from subprocess import call
from tqdm import tqdm
from uuid import uuid4
from plexapi.compat import which, makedirs
from plexapi.exceptions import BadRequest, NotFound
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.utils import download, SEARCHTYPES

DOCKER_CMD = [
    'docker', 'run', '-d',
    '--name', 'plex-test-%(container_name_extra)s%(image_tag)s',
    '--restart', 'on-failure',
    '-p', '32400:32400/tcp',
    '-p', '3005:3005/tcp',
    '-p', '8324:8324/tcp',
    '-p', '32469:32469/tcp',
    '-p', '1900:1900/udp',
    '-p', '32410:32410/udp',
    '-p', '32412:32412/udp',
    '-p', '32413:32413/udp',
    '-p', '32414:32414/udp',
    '-e', 'TZ="Europe/London"',
    '-e', 'PLEX_CLAIM=%(claim_token)s',
    '-e', 'ADVERTISE_IP=http://%(advertise_ip)s:32400/',
    '-h', '%(hostname)s',
    '-e', 'TZ="%(timezone)s"',
    '-v', '%(destination)s/db:/config',
    '-v', '%(destination)s/transcode:/transcode',
    '-v', '%(destination)s/media:/data',
    'plexinc/pms-docker:%(image_tag)s'
]


def get_default_ip():
    """ Return the first IP address of the current machine if available. """
    available_ips = list(set([i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)
        if i[4][0] not in ('127.0.0.1', '::1') and not i[4][0].startswith('fe80:')]))
    return available_ips[0] if len(available_ips) else None


def get_plex_account(opts):
    """ Authenitcate with Plex using the command line options. """
    if not opts.unclaimed:
        if opts.token:
            return MyPlexAccount(token=opts.token)
        return plexapi.utils.getMyPlexAccount(opts)
    return None


def get_movie_path(name, year):
    """ Return a movie path given its title and year. """
    return os.path.join(movies_path, '%s (%d).mp4' % (name, year))


def get_tvshow_path(name, season, episode):
    """ Return a TV show path given its title, season, and episode. """
    return os.path.join(tvshows_path, name, 'S%02dE%02d.mp4' % (season, episode))


def add_library_section(server, section):
    """ Add the specified section to our Plex instance. This tends to be a bit
        flaky, so we retry a few times here.
    """
    start = time.time()
    runtime = 0
    while runtime < 60:
        try:
            server.library.add(**section)
            return True
        except BadRequest as err:
            if 'server is still starting up. Please retry later' in str(err):
                time.sleep(1)
                continue
            raise
        runtime = time.time() - start
    raise SystemExit('Timeout adding section to Plex instance.')


def create_section(server, section, opts):
    processed_media = 0
    expected_media_count = section.pop('expected_media_count', 0)
    expected_media_type = (section['type'], )
    if section['type'] == 'artist':
        expected_media_type = ('artist', 'album', 'track')
    expected_media_type = tuple(SEARCHTYPES[t] for t in expected_media_type)

    def alert_callback(data):
        """ Listen to the Plex notifier to determine when metadata scanning is complete.
            * state=1 means record processed, when no metadata source was set
            * state=5 means record processed, applicable only when metadata source was set
        """
        global processed_media
        print(data)
        if data['type'] == 'timeline':
            for entry in data['TimelineEntry']:
                if entry.get('identifier', 'com.plexapp.plugins.library') == 'com.plexapp.plugins.library':
                    # Missed mediaState means that media was processed (analyzed & thumbnailed)
                    if 'mediaState' not in entry and entry['type'] in expected_media_type:
                        # state=5 means record processed, applicable only when metadata source was set
                        if entry['state'] == 5:
                            cnt = 1
                            # Workaround for old Plex versions which not reports individual episodes' progress
                            if entry['type'] == SEARCHTYPES['show']:
                                show = server.library.sectionByID(str(entry['sectionID'])).get(entry['title'])
                                cnt = show.leafCount
                            bar.update(cnt)
                        # state=1 means record processed, when no metadata source was set
                        elif entry['state'] == 1 and entry['type'] == SEARCHTYPES['photo']:
                            bar.update()

    runtime = 0
    start = time.time()
    bar = tqdm(desc='Scanning section ' + section['name'], total=expected_media_count)
    notifier = server.startAlertListener(alert_callback)
    add_library_section(server, section)
    while bar.n < bar.total:
        if runtime >= opts.bootstrap_timeout:
            print('Metadata scan taking too long, probably something went really wrong')
            exit(1)
        time.sleep(3)
        runtime = time.time() - start
    bar.close()
    notifier.stop()


if __name__ == '__main__':
    default_ip = get_default_ip()
    parser = argparse.ArgumentParser(description=__doc__)
    # Authentication arguments
    mg = parser.add_mutually_exclusive_group()
    g = mg.add_argument_group()
    g.add_argument('--username', help='Your Plex username')
    g.add_argument('--password', help='Your Plex password')
    mg.add_argument('--token', help='Plex.tv authentication token', default=plexapi.CONFIG.get('auth.server_token'))
    mg.add_argument('--unclaimed', help='Do not claim the server', default=False, action='store_true')
    # Test environment arguments
    parser.add_argument('--timezone', help='Timezone to set inside plex', default='UTC')  # noqa
    parser.add_argument('--destination', help='Local path where to store all the media', default=os.path.join(os.getcwd(), 'plex'))  # noqa
    parser.add_argument('--advertise-ip', help='IP address which should be advertised by new Plex instance', required=default_ip is None, default=default_ip)  # noqa
    parser.add_argument('--docker-tag', help='Docker image tag to install', default='latest')  # noqa
    parser.add_argument('--bootstrap-timeout', help='Timeout for each step of bootstrap, in seconds (default: %(default)s)', default=180, type=int)  # noqa
    parser.add_argument('--server-name', help='Name for the new server', default='plex-test-docker-%s' % str(uuid4()))  # noqa
    parser.add_argument('--accept-eula', help='Accept Plex`s EULA', default=False, action='store_true')  # noqa
    parser.add_argument('--without-movies', help='Do not create Movies section', default=True, dest='with_movies', action='store_false')  # noqa
    parser.add_argument('--without-shows', help='Do not create TV Shows section', default=True, dest='with_shows', action='store_false')  # noqa
    parser.add_argument('--without-music', help='Do not create Music section', default=True, dest='with_music', action='store_false')  # noqa
    parser.add_argument('--without-photos', help='Do not create Photos section', default=True, dest='with_photos', action='store_false')  # noqa
    parser.add_argument('--show-token', help='Display access token after bootstrap', default=False, action='store_true')  # noqa
    opts = parser.parse_args()

    # Download the Plex Docker image
    print('Creating Plex instance named %s with advertised ip %s' % (opts.server_name, opts.advertise_ip))
    if which('docker') is None:
        print('Docker is required to be available')
        exit(1)
    if call(['docker', 'pull', 'plexinc/pms-docker:%s' % opts.docker_tag]) != 0:
        print('Got an error when executing docker pull!')
        exit(1)

    # Start the Plex Docker container
    account = get_plex_account(opts)
    path = os.path.realpath(os.path.expanduser(opts.destination))
    makedirs(os.path.join(path, 'media'), exist_ok=True)
    arg_bindings = {
        'destination': path,
        'hostname': opts.server_name,
        'claim_token': account.claimToken() if account else '',
        'timezone': opts.timezone,
        'advertise_ip': opts.advertise_ip,
        'image_tag': opts.docker_tag,
        'container_name_extra': '' if account else 'unclaimed-'
    }
    docker_cmd = [c % arg_bindings for c in DOCKER_CMD]
    exit_code = call(docker_cmd)
    if exit_code != 0:
        raise SystemExit('Error %s while starting the Plex docker container' % exit_code)

    # Wait for the Plex container to start
    print('Waiting for the Plex container to start..')
    start = time.time()
    runtime = 0
    server = None
    while not server and (runtime < opts.bootstrap_timeout):
        try:
            if account:
                server = account.device(opts.server_name).connect()
            else:
                server = PlexServer('http://%s:32400' % opts.advertise_ip)
            if opts.accept_eula:
                server.settings.get('acceptedEULA').set(True)
                server.settings.save()
        except Exception as err:
            print(err)
            time.sleep(1)
        runtime = time.time() - start
    if not server:
        raise SystemExit('Server didnt appear in your account after %ss' % opts.bootstrap_timeout)
    print('Plex container started after %ss, downloading content' % runtime)

    # Download video_stub.mp4
    print('Downloading video_stub.mp4..')
    if opts.with_movies or opts.with_shows:
        media_stub_path = os.path.join(path, 'media', 'video_stub.mp4')
        if not os.path.isfile(media_stub_path):
            download('http://www.mytvtestpatterns.com/mytvtestpatterns/Default/GetFile?p=PhilipsCircleMP4', '',
                filename='video_stub.mp4', savepath=os.path.join(path, 'media'), showstatus=True)

    sections = []
    # Prepare Movies section
    if opts.with_movies:
        print('Preparing movie section..')
        movies_path = os.path.join(path, 'media', 'Movies')
        makedirs(movies_path, exist_ok=True)
        required_movies = {
            'Elephants Dream': 2006,
            'Sita Sings the Blues': 2008,
            'Big Buck Bunny': 2008,
            'Sintel': 2010,
        }
        expected_media_count = 0
        for name, year in required_movies.items():
            expected_media_count += 1
            if not os.path.isfile(get_movie_path(name, year)):
                copyfile(media_stub_path, get_movie_path(name, year))
        sections.append(dict(name='Movies', type='movie', location='/data/Movies', agent='com.plexapp.agents.imdb',
            scanner='Plex Movie Scanner', expected_media_count=expected_media_count))

    # Prepare TV Show section
    if opts.with_shows:
        print('Preparing TV-Shows section..')
        tvshows_path = os.path.join(path, 'media', 'TV-Shows')
        makedirs(os.path.join(tvshows_path, 'Game of Thrones'), exist_ok=True)
        makedirs(os.path.join(tvshows_path, 'The 100'), exist_ok=True)
        required_tv_shows = {
            'Game of Thrones': [list(range(1, 11)), list(range(1, 11))],
            'The 100': [list(range(1, 14)), list(range(1, 17))]
        }
        expected_media_count = 0
        for show_name, seasons in required_tv_shows.items():
            for season_id, episodes in enumerate(seasons, start=1):
                for episode_id in episodes:
                    expected_media_count += 1
                    episode_path = get_tvshow_path(show_name, season_id, episode_id)
                    if not os.path.isfile(episode_path):
                        copyfile(get_movie_path('Sintel', 2010), episode_path)
        sections.append(dict(name='TV Shows', type='show', location='/data/TV-Shows',
            agent='com.plexapp.agents.thetvdb', scanner='Plex Series Scanner',
            expected_media_count=expected_media_count))

    # Prepare Music section
    if opts.with_music:
        print('Preparing Music section..')
        music_path = os.path.join(path, 'media', 'Music')
        makedirs(music_path, exist_ok=True)
        expected_media_count = 0
        artist_dst = os.path.join(music_path, 'Infinite State')
        dest_path = os.path.join(artist_dst, 'Unmastered Impulses')
        if not os.path.isdir(dest_path):
            zip_path = os.path.join(artist_dst, 'Unmastered Impulses.zip')
            if os.path.isfile(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as handle:
                    handle.extractall(artist_dst)
            else:
                download('https://github.com/kennethreitz/unmastered-impulses/archive/master.zip', '',
                    filename='Unmastered Impulses.zip', savepath=artist_dst, unpack=True, showstatus=True)
            os.rename(os.path.join(artist_dst, 'unmastered-impulses-master', 'mp3'), dest_path)
            rmtree(os.path.join(artist_dst, 'unmastered-impulses-master'))
        expected_media_count += len(glob(os.path.join(dest_path, '*.mp3'))) + 2  # wait for artist & album
        artist_dst = os.path.join(music_path, 'Broke For Free')
        dest_path = os.path.join(artist_dst, 'Layers')
        if not os.path.isdir(dest_path):
            zip_path = os.path.join(artist_dst, 'Layers.zip')
            if not os.path.isfile(zip_path):
                download('https://archive.org/compress/Layers-11520/formats=VBR%20MP3&file=/Layers-11520.zip', '',
                    filename='Layers.zip', savepath=artist_dst, showstatus=True)
            makedirs(dest_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as handle:
                handle.extractall(dest_path)
        expected_media_count += len(glob(os.path.join(dest_path, '*.mp3'))) + 2  # wait for artist & album
        sections.append(dict(name='Music', type='artist', location='/data/Music',
            agent='com.plexapp.agents.lastfm', scanner='Plex Music Scanner',
            expected_media_count=expected_media_count))

    # Prepare Photos section
    if opts.with_photos:
        print('Preparing Photos section..')
        photos_path = os.path.join(path, 'media', 'Photos')
        makedirs(photos_path, exist_ok=True)
        expected_photo_count = 0
        folders = {
            ('Cats', ): 3,
            ('Cats', 'Cats in bed'): 7,
            ('Cats', 'Cats not in bed'): 1,
            ('Cats', 'Not cats in bed'): 1,
        }
        has_photos = 0
        for folder_path, required_cnt in folders.items():
            folder_path = os.path.join(photos_path, *folder_path)
            photos_in_folder = len(glob(os.path.join(folder_path, '*.jpg')))
            while photos_in_folder < required_cnt:
                photos_in_folder += 1
                download('https://picsum.photos/800/600/?random', '',
                    filename='photo%d.jpg' % photos_in_folder, savepath=folder_path)
            has_photos += photos_in_folder
        sections.append(dict(name='Photos', type='photo', location='/data/Photos',
            agent='com.plexapp.agents.none', scanner='Plex Photo Scanner',
            expected_media_count=has_photos))

    # Create the Plex library in our instance
    if sections:
        print('Creating the Plex libraries in our instance')
        for section in sections:
            create_section(server, section, opts)

    # Share this instance with the specified username
    if account:
        shared_username = os.environ.get('SHARED_USERNAME', 'PKKid')
        try:
            user = account.user(shared_username)
            account.updateFriend(user, server)
            print('The server was shared with user %s' % shared_username)
        except NotFound:
            pass

    # Finished: Display our Plex details
    print('Base URL is %s' % server.url('', False))
    if account and opts.show_token:
        print('Auth token is %s' % account.authenticationToken)
    print('Server %s is ready to use!' % opts.server_name)
