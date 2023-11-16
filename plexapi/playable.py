import re
from urllib.parse import urlencode

from plexapi import media, utils
from plexapi.base import PlexPartialObject
from plexapi.exceptions import Unsupported


class Playable(PlexPartialObject):
    """This is a general place to store functions specific to media that is Playable.
    Things were getting mixed up a bit when dealing with Shows, Season, Artists,
    Albums which are all not playable.

    Attributes:
        playlistItemID (int): Playlist item ID (only populated for :class:`~plexapi.playlist.Playlist` items).
        playQueueItemID (int): PlayQueue item ID (only populated for :class:`~plexapi.playlist.PlayQueue` items).
    """

    def _loadData(self, data):
        self.playlistItemID = utils.cast(int, data.attrib.get("playlistItemID"))
        self.playQueueItemID = utils.cast(int, data.attrib.get("playQueueItemID"))
        self.media = self.findItems(data, media.Media)
        self.duration = utils.cast(int, data.attrib.get("duration"))

    # @abstractmethod
    def _prettyfilename(self):
        """Returns a pretty filename for this media item."""

    def getStreamURL(self, **kwargs):
        """Returns a stream url that may be used by external applications such as VLC.

        Parameters:
            **kwargs (dict): optional parameters to manipulate the playback when accessing
                the stream. A few known parameters include: maxVideoBitrate, videoResolution
                offset, copyts, protocol, mediaIndex, partIndex, platform.

        Raises:
            :exc:`~plexapi.exceptions.Unsupported`: When the item doesn't support fetching a stream URL.
        """
        if self.TYPE not in ("movie", "episode", "track", "clip"):
            raise Unsupported(f"Fetching stream URL for {self.TYPE} is unsupported.")

        mvb = kwargs.pop("maxVideoBitrate", None)
        vr = kwargs.pop("videoResolution", "")
        protocol = kwargs.pop("protocol", None)

        params = {
            "path": self.key,
            "mediaIndex": kwargs.pop("mediaIndex", 0),
            "partIndex": kwargs.pop("mediaIndex", 0),
            "protocol": protocol,
            "fastSeek": kwargs.pop("fastSeek", 1),
            "copyts": kwargs.pop("copyts", 1),
            "offset": kwargs.pop("offset", 0),
            "maxVideoBitrate": max(mvb, 64) if mvb else None,
            "videoResolution": vr if re.match(r"^\d+x\d+$", vr) else None,
            "X-Plex-Platform": kwargs.pop("platform", "Chrome"),
        }
        params.update(kwargs)

        # remove None values
        params = {k: v for k, v in params.items() if v is not None}
        streamtype = "audio" if self.TYPE in ("track", "album") else "video"
        ext = "mpd" if protocol == "dash" else "m3u8"

        return self._server.url(
            f"/{streamtype}/:/transcode/universal/start.{ext}?{urlencode(params)}",
            includeToken=True,
        )

    def iterParts(self):
        """Iterates over the parts of this media item."""
        for item in self.media:
            for part in item.parts:
                yield part

    def play(self, client):
        """Start playback on the specified client.

        Parameters:
            client (:class:`~plexapi.client.PlexClient`): Client to start playing on.
        """
        client.playMedia(self)

    def download(self, savepath=None, keep_original_name=False, **kwargs):
        """Downloads the media item to the specified location. Returns a list of
        filepaths that have been saved to disk.

        Parameters:
            savepath (str): Defaults to current working dir.
            keep_original_name (bool): True to keep the original filename otherwise
                a friendlier filename is generated. See filenames below.
            **kwargs (dict): Additional options passed into :func:`~plexapi.audio.Track.getStreamURL`
                to download a transcoded stream, otherwise the media item will be downloaded
                as-is and saved to disk.

        **Filenames**

        * Movie: ``<title> (<year>)``
        * Episode: ``<show title> - s00e00 - <episode title>``
        * Track: ``<artist title> - <album title> - 00 - <track title>``
        * Photo: ``<photoalbum title> - <photo/clip title>`` or ``<photo/clip title>``
        """
        filepaths = []
        parts = [i for i in self.iterParts() if i]

        for part in parts:
            if not keep_original_name:
                filename = utils.cleanFilename(
                    f"{self._prettyfilename()}.{part.container}"
                )
            else:
                filename = part.file

            if kwargs:
                # So this seems to be a a lot slower but allows transcode.
                download_url = self.getStreamURL(**kwargs)
            else:
                download_url = self._server.url(f"{part.key}?download=1")

            filepath = utils.download(
                download_url,
                self._server._token,
                filename=filename,
                savepath=savepath,
                session=self._server._session,
            )

            if filepath:
                filepaths.append(filepath)

        return filepaths

    def updateProgress(self, time, state="stopped"):
        """Set the watched progress for this video.

        Note that setting the time to 0 will not work.
        Use :func:`~plexapi.mixins.PlayedUnplayedMixin.markPlayed` or
        :func:`~plexapi.mixins.PlayedUnplayedMixin.markUnplayed` to achieve
        that goal.

        Parameters:
            time (int): milliseconds watched
            state (string): state of the video, default 'stopped'
        """
        key = f"/:/progress?key={self.ratingKey}&identifier=com.plexapp.plugins.library&time={time}&state={state}"
        self._server.query(key)
        return self

    def updateTimeline(self, time, state="stopped", duration=None):
        """Set the timeline progress for this video.

        Parameters:
            time (int): milliseconds watched
            state (string): state of the video, default 'stopped'
            duration (int): duration of the item
        """
        durationStr = "&duration="
        if duration is not None:
            durationStr = durationStr + str(duration)
        else:
            durationStr = durationStr + str(self.duration)
        key = (
            f"/:/timeline?ratingKey={self.ratingKey}&key={self.key}&"
            f"identifier=com.plexapp.plugins.library&time={int(time)}&state={state}{durationStr}"
        )
        self._server.query(key)
        return self
