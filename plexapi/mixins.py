# -*- coding: utf-8 -*-
from urllib.parse import quote_plus

from plexapi import media


class ArtMixin(object):
    """ Mixin for Plex objects that can have artwork."""

    def arts(self):
        """ Returns list of available :class:`~plexapi.media.Art` objects. """
        return self.fetchItems('/library/metadata/%s/arts' % self.ratingKey, cls=media.Art)

    def uploadArt(self, url=None, filepath=None):
        """ Upload art from url or filepath and set it as the selected art.
        
            Parameters:
                url (str): The full URL to the image to upload.
                filepath (str): The full file path the the image to upload.
        """
        if url:
            key = '/library/metadata/%s/arts?url=%s' % (self.ratingKey, quote_plus(url))
            self._server.query(key, method=self._server._session.post)
        elif filepath:
            key = '/library/metadata/%s/arts?' % self.ratingKey
            data = open(filepath, 'rb').read()
            self._server.query(key, method=self._server._session.post, data=data)

    def setArt(self, art):
        """ Set the artwork for a Plex object.
        
            Parameters:
                art (:class:`~plexapi.media.Art`): The art object to select.
        """
        art.select()


class PosterMixin(object):
    """ Mixin for Plex objects that can have posters."""

    def posters(self):
        """ Returns list of available :class:`~plexapi.media.Poster` objects. """
        return self.fetchItems('/library/metadata/%s/posters' % self.ratingKey, cls=media.Poster)

    def uploadPoster(self, url=None, filepath=None):
        """ Upload poster from url or filepath and set it as the selected poster.

            Parameters:
                url (str): The full URL to the image to upload.
                filepath (str): The full file path the the image to upload.
        """
        if url:
            key = '/library/metadata/%s/posters?url=%s' % (self.ratingKey, quote_plus(url))
            self._server.query(key, method=self._server._session.post)
        elif filepath:
            key = '/library/metadata/%s/posters?' % self.ratingKey
            data = open(filepath, 'rb').read()
            self._server.query(key, method=self._server._session.post, data=data)

    def setPoster(self, poster):
        """ Set the poster for a Plex object.
        
            Parameters:
                poster (:class:`~plexapi.media.Poster`): The poster object to select.
        """
        poster.select()
