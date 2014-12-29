## PlexAPI ##
Python bindings for the Plex API.

* Navigate local or remote shared libraries.
* Mark shows watched or unwatched.
* Request rescan, analyze, empty trash.
* Play media on connected clients.
* Plex Sync Support.

Planned features:

* Create and maintain playlists.
* List active sessions.
* Play trailers and extras.
* Provide useful utility scripts.
* Better support for Music and Photos?

#### Install ###

    pip install plexapi

#### Getting a PlexServer Instance ####

There are two types of authentication.  If running the PlexAPI on the same
network as the Plex Server (and you are not using Plex Users), you can
authenticate without a username and password.  Getting a PlexServer
instance is as easy as the following:

    from plexapi.server import PlexServer
    plex = PlexServer()   # Defaults to localhost:32400

If you are running on a separate network or using Plex Users you need to log
into MyPlex to get a PlexServer instance.  An example of this is below. NOTE:
Servername below is the name of the server (not the hostname and port).  If
logged into Plex Web you can see the server name in the top left above your
available libraries.

    from plexapi.myplex import MyPlexUser
    user = MyPlexUser('<USERNAME>', '<PASSWORD>')
    plex = user.getServer('<SERVERNAME>').connect()

#### Usage Examples ####

    # Example 1: List all unwatched content in library.
    for section in plex.library.sections():
        print 'Unwatched content in %s:' % section.title
        for video in section.unwatched():
            print '  %s' % video.title

    # Example 2: Mark all Conan episodes watched.
    plex.library.get('Conan (2010)').markWatched()

    # Example 3: List all Clients connected to the Server.
    for client in plex.clients():
        print client.name

    # Example 4: Play the Movie Avatar on my iPhone.
    avatar = plex.library.section('Movies').get('Avatar')
    client = plex.client("Michael's iPhone")
    client.playMedia(avatar)

    # Example 5: List all content with the word 'Game' in the title.
    for video in plex.search('Game'):
        print '%s (%s)' % (video.title, video.TYPE)

    # Example 6: List all movies directed by the same person as Jurassic Park.
    jurassic_park = plex.library.section('Movies').get('Jurassic Park')
    director = jurassic_park.directors[0]
    for movie in director.related():
        print movie.title

    # Example 7: List files for the latest episode of Friends.
    the_last_one = plex.library.get('Friends').episodes()[-1]
    for part in the_last_one.iter_parts():
        print part.file

#### FAQs ####

**Q. Why are you using camelCase and not following PEP8 guidelines?**

A. This API reads XML documents provided by MyPlex and the Plex Server.
We decided to conform to their style so that the API variable names directly
match with the provided XML documents.