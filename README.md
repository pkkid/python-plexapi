## PlexAPI ##
<a href="https://badge.fury.io/py/PlexAPI">
  <img align="right" src="https://badge.fury.io/py/PlexAPI.svg"/></a>
<a href='https://coveralls.io/github/mjs7231/python-plexapi'>
  <img align="right" src='https://coveralls.io/repos/github/mjs7231/python-plexapi/badge.svg' alt='Coverage Status' /></a>
<a href="https://travis-ci.org/pkkid/python-plexapi">
  <img align="right" src="https://travis-ci.org/pkkid/python-plexapi.svg?branch=master"/></a>
<a href='http://python-plexapi.readthedocs.io/en/latest/?badge=latest'>
  <img align="right"  src='https://readthedocs.org/projects/python-plexapi/badge/?version=latest' alt='Documentation Status' /></a>
Python bindings for the Plex API.

* Navigate local or remote shared libraries.
* Mark shows watched or unwatched.
* Request rescan, analyze, empty trash.
* Play media on connected clients.
* Get URL to stream stream h264/aac video (playable in VLC,MPV,etc).
* Plex Sync Support.
* Plex Audio Support.

#### Install ###

    pip install plexapi


#### Getting a PlexServer Instance ####

There are two types of authentication. If you are running on a separate network
or using Plex Users you can log into MyPlex to get a PlexServer instance. An
example of this is below. NOTE: Servername below is the name of the server (not
the hostname and port).  If logged into Plex Web you can see the server name in
the top left above your available libraries.

```python
from plexapi.myplex import MyPlexAccount
account = MyPlexAccount('<USERNAME>', '<PASSWORD>')
plex = account.resource('<SERVERNAME>').connect()  # returns a PlexServer instance
```

If you want to avoid logging into MyPlex and you already know your auth token
string, you can use the PlexServer object directly as above, but passing in
the baseurl and auth token directly.

```python
from plexapi.server import PlexServer
baseurl = 'http://plexserver:32400'
token = '2ffLuB84dqLswk9skLos'
plex = PlexServer(baseurl, token)
```


#### Usage Examples ####

```python
# Example 1: List all unwatched movies.
movies = plex.library.section('Movies')
for video in movies.search(unwatched=True):
    print(video.title)
```
```python
# Example 2: Mark all Game of Thrones episodes watched.
plex.library.section('TV Shows').get('Game of Thrones').markWatched()
```
```python
# Example 3: List all clients connected to the Server.
for client in plex.clients():
    print(client.title)
```
```python
# Example 4: Play the movie Cars on another client.
# Note: Client must be on same network as server.
cars = plex.library.section('Movies').get('Cars')
client = plex.client("Michael's iPhone")
client.playMedia(cars)
```
```python
# Example 5: List all content with the word 'Game' in the title.
for video in plex.search('Game'):
    print('%s (%s)' % (video.title, video.TYPE))
```
```python
# Example 6: List all movies directed by the same person as Die Hard.
movies = plex.library.section('Movies')
die_hard = movies.get('Die Hard')
director = die_hard.directors[0]
for movie in movies.search(None, director=director):
    print(movie.title)
```
```python
# Example 7: List files for the latest episode of The 100.
last_episode = plex.library.section('TV Shows').get('The 100').episodes()[-1]
for part in last_episode.iterParts():
    print(part.file)
```
```python
# Example 8: Get a URL to stream a movie or show in another client
die_hard = plex.library.section('Movies').get('Die Hard')
print('Run running the following command to play in VLC:')
print('vlc "%s"' % die_hard.getStreamURL(videoResolution='800x600'))
```
```python
# Example 9: Get audio/video/all playlists
for playlist in plex.playlists():
    print(playlist.title)
```

#### FAQs ####

**Q. Why are you using camelCase and not following PEP8 guidelines?**

A. This API reads XML documents provided by MyPlex and the Plex Server.
We decided to conform to their style so that the API variable names directly
match with the provided XML documents.


**Q. Why don't you offer feature XYZ?**

A. This library is meant to be a wrapper around the XML pages the Plex
server provides. If we are not providing an API that is offerered in the
XML pages, please let us know! -- Adding additional features beyond that
should be done outside the scope of this library.

**Q. What are some helpful links if trying to understand the raw Plex API?**

* https://github.com/plexinc/plex-media-player/wiki/Remote-control-API
* https://forums.plex.tv/discussion/104353/pms-web-api-documentation
* https://github.com/Arcanemagus/plex-api/wiki
