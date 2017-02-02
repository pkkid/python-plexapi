# -*- coding: utf-8 -*-
from os.path import basename
from utils import log, register
from plexapi import CONFIG


@register()
def test_partial_video(account, plex):
    result = plex.search(CONFIG.movie_foreign)
    log(2, 'Title: %s' % result[0].title)
    log(2, 'Original Title: %s' % result[0].originalTitle)
    assert(result[0].originalTitle != None)


@register()
def test_list_media_files(account, plex):
    # Fetch file names from the tv show
    episode_files = []
    episode = plex.library.section(CONFIG.show_section).get(CONFIG.show_title).episodes()[-1]
    log(2, 'Episode Files: %s' % episode)
    for media in episode.media:
        for part in media.parts:
            log(4, part.file)
            episode_files.append(part.file)
    assert filter(None, episode_files), 'No show files have been listed.'
    # Fetch file names from the movie
    movie_files = []
    movie = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
    log(2, 'Movie Files: %s' % movie)
    for media in movie.media:
        for part in media.parts:
            log(4, part.file)
            movie_files.append(part.file)
    assert filter(None, movie_files), 'No movie files have been listed.'


@register()
def test_list_video_tags(account, plex):
    movies = plex.library.section(CONFIG.movie_section)
    movie = movies.get(CONFIG.movie_title)
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


@register()
def test_list_video_streams(account, plex):
    movie = plex.library.section(CONFIG.movie_section).get('John Wick')
    videostreams = [s.language for s in movie.videoStreams]
    audiostreams = [s.language for s in movie.audioStreams]
    subtitlestreams = [s.language for s in movie.subtitleStreams]
    log(2, 'Video Streams: %s' % ', '.join(videostreams[0:5]))
    log(2, 'Audio Streams: %s' % ', '.join(audiostreams[0:5]))
    log(2, 'Subtitle Streams: %s' % ', '.join(subtitlestreams[0:5]))
    assert filter(None, videostreams), 'No video streams listed for movie.'
    assert filter(None, audiostreams), 'No audio streams listed for movie.'
    assert filter(None, subtitlestreams), 'No subtitle streams listed for movie.'


@register()
def test_list_audio_tags(account, plex):
    section = plex.library.section(CONFIG.audio_section)
    artist = section.get(CONFIG.audio_artist)
    track = artist.get(CONFIG.audio_track)
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


@register()
def test_is_watched(account, plex):
    show = plex.library.section(CONFIG.show_section).get(CONFIG.show_title)
    episode = show.get(CONFIG.show_episode)
    log(2, '%s isWatched: %s' % (episode.title, episode.isWatched))
    movie = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
    log(2, '%s isWatched: %s' % (movie.title, movie.isWatched))


@register()
def test_fetch_details_not_in_search_result(account, plex):
    # Search results only contain 3 actors per movie. This text checks there
    # are more than 3 results in the actor list (meaning it fetched the detailed
    # information behind the scenes).
    result = plex.search(CONFIG.movie_title)[0]
    actors = result.actors
    assert len(actors) >= 4, 'Unable to fetch detailed movie information'
    log(2, '%s actors found.' % len(actors))


@register()
def test_stream_url(account, plex):
    movie = plex.library.section(CONFIG.movie_section).get(CONFIG.movie_title)
    episode = plex.library.section(CONFIG.show_section).get(CONFIG.show_title).episodes()[-1]
    track = plex.library.section(CONFIG.audio_section).get(CONFIG.audio_artist).get(CONFIG.audio_track)
    log(2, 'Movie: vlc "%s"' % movie.getStreamURL())
    log(2, 'Episode: vlc "%s"' % episode.getStreamURL())
    log(2, 'Track: cvlc "%s"' % track.getStreamURL())
    

@register()
def test_list_audioalbums(account, plex):
    music = plex.library.section(CONFIG.audio_section)
    albums = music.albums()
    for album in albums[:10]:
        log(2, '%s - %s [%s]' % (album.artist().title, album.title, album.year))


@register()
def test_list_photoalbums(account, plex):
    photosection = plex.library.section(CONFIG.photo_section)
    photoalbums = photosection.all()
    log(2, 'Listing albums..')
    for album in photoalbums[:10]:
        log(4, '%s' % album.title)
    assert len(photoalbums), 'No photoalbums found.'
    album = photosection.get(CONFIG.photo_album)
    photos = album.photos()
    for photo in photos[:10]:
        filename = basename(photo.media[0].parts[0].file)
        width, height = photo.media[0].width, photo.media[0].height
        log(4, '%s (%sx%s)' % (filename, width, height))
    assert len(photoalbums), 'No photos found.'