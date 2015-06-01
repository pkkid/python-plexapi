#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# the Copyright © 2015 simonwjackson <simonwjackson@bowser>
#
# Distributed under terms of the MIT license.

"""

"""

import urllib.parse


class StreamUrl:
    def __init__(self, server, key, max_bitrate=None, max_resolution=None,
                 offset=0, platform="Chrome"):
        """Represents a URL that allows the user to stream a video direclty
        from plex.

        server -- an instance of the plex server (required)
        key -- the numeric identifier of the requested video (required)
        max_bitrate -- sets the maximum bitrate of the video and audio stream
        max_resolution -- sets the maximum resolution of a video stream
        offset -- sets the start time (in seconds) that the video stream will
        start from (defaults to 0)
        """
        self.server = server
        self.key = key
        self.max_resolution = max_resolution
        self.offset = offset
        self.platform = platform
        self.max_bitrate = max_bitrate

    def __str__(self):
        return self._build_url()

    @property
    def key(self):
        """Get the key for the video stream."""
        return self.__key

    @key.setter
    def key(self, key):
        """Set the key for the video stream.

        Notes:
        * Can also be specified as plex metadata path: /library/metadata/234
        """
        if key is not None:
            if isinstance(key, str):
                key = key.replace("/library/metadata/", '')

        self.__key = key

    @property
    def max_resolution(self):
        """Get the maximium resolution for the video stream."""
        return self.__max_resolution

    @max_resolution.setter
    def max_resolution(self, max_resolution):
        """Set the maximium resolution for the video stream. If a single
        integer is specified it will be squared (eg. 500 -> 500x500)

        Notes:
        * If the reqested resolution is larger than the original video, the
        original resolution will be used instead.
        """
        if isinstance(max_resolution, str):
            max_resolution = max_resolution.split('x')
            """Make sure we have integers"""
            max_resolution = [int(i) for i in max_resolution]

            if len(max_resolution) == 2:
                max_resolution = "{0}x{1}".format(max_resolution[0], max_resolution[1])

            if len(max_resolution) == 1:
                max_resolution = int(max_resolution[0])

        self.__max_resolution = max_resolution

    @property
    def max_bitrate(self):
        """Get the maximium bitrate for the video stream."""
        return self.__max_bitrate

    @max_bitrate.setter
    def max_bitrate(self, max_bitrate):
        """Set the maximium bitrate for the video stream.

        Notes:
        * 64kbps is the minimum bitrate allowed, anything lower will be reset
        to 64kbps.
        """
        if isinstance(max_bitrate, int):
            max_bitrate = int(max_bitrate)

            if max_bitrate < 64:
                max_bitrate = 64

        self.__max_bitrate = max_bitrate

    def _build_url(self):
        """Build a url for streaming a video"""
        full_uri = "http://{address}:{port}/video/:/transcode/universal/start?{params}"
        local_media_uri = "http://127.0.0.1:32400/library/metadata/" + str(self.key)

        params = {
            "path": local_media_uri,
            "mediaIndex": 0,
            "offset": self.offset,
            "copyts": 1,
            "X-Plex-Platform": self.platform
        }

        if self.max_bitrate:
            params["maxVideoBitrate"] = self.max_bitrate

        if self.max_resolution:
            params["videoResolution"] = self.max_resolution

        params_string = urllib.parse.urlencode(params)
        self.url = full_uri.format(address=self.server.address, port=self.server.port,
                                   params=params_string)

        return self.url
