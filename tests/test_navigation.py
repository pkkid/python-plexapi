# -*- coding: utf-8 -*-


def test_navigate_around_show(account, plex):
    show = plex.library.section("TV Shows").get("The 100")
    seasons = show.seasons()
    season = show.season("Season 1")
    episodes = show.episodes()
    episode = show.episode("Pilot")
    assert "Season 1" in [s.title for s in seasons], "Unable to list season:"
    assert "Pilot" in [e.title for e in episodes], "Unable to list episode:"
    assert show.season(1) == season
    assert show.episode("Pilot") == episode, "Unable to get show episode:"
    assert season.episode("Pilot") == episode, "Unable to get season episode:"
    assert season.show() == show, "season.show() doesnt match expected show."
    assert episode.show() == show, "episode.show() doesnt match expected show."
    assert episode.season() == season, "episode.season() doesnt match expected season."


def test_navigate_around_artist(account, plex):
    artist = plex.library.section("Music").get("Broke For Free")
    albums = artist.albums()
    album = artist.album("Layers")
    tracks = artist.tracks()
    track = artist.track("As Colourful as Ever")
    print("Navigating around artist: %s" % artist)
    print("Album: %s" % album)
    print("Tracks: %s..." % tracks)
    print("Track: %s" % track)
    assert artist.track("As Colourful as Ever") == track, "Unable to get artist track."
    assert album.track("As Colourful as Ever") == track, "Unable to get album track."
    assert album.artist() == artist, "album.artist() doesnt match expected artist."
    assert track.artist() == artist, "track.artist() doesnt match expected artist."
    assert track.album() == album, "track.album() doesnt match expected album."
