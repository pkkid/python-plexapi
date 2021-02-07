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


class CollectionMixin(object):
    """ Mixin for Plex objects that can have collections. """

    def addCollection(self, collections):
        """ Add a collection tag(s).

           Parameters:
                collections (list): List of strings.
        """
        self._edit_tags('collection', collections)

    def removeCollection(self, collections):
        """ Remove a collection tag(s).

           Parameters:
                collections (list): List of strings.
        """
        self._edit_tags('collection', collections, remove=True)


class CountryMixin(object):
    """ Mixin for Plex objects that can have countries. """

    def addCountry(self, countries):
        """ Add a country tag(s).

           Parameters:
                countries (list): List of strings.
        """
        self._edit_tags('country', countries)

    def removeCountry(self, countries):
        """ Remove a country tag(s).

           Parameters:
                countries (list): List of strings.
        """
        self._edit_tags('country', countries, remove=True)


class DirectorMixin(object):
    """ Mixin for Plex objects that can have directors. """

    def addDirector(self, directors):
        """ Add a director tag(s).

           Parameters:
                directors (list): List of strings.
        """
        self._edit_tags('director', directors)

    def removeDirector(self, directors):
        """ Remove a director tag(s).

           Parameters:
                directors (list): List of strings.
        """
        self._edit_tags('director', directors, remove=True)


class GenreMixin(object):
    """ Mixin for Plex objects that can have genres. """

    def addGenre(self, genres):
        """ Add a genre tag(s).

           Parameters:
                genres (list): List of strings.
        """
        self._edit_tags('genre', genres)

    def removeGenre(self, genres):
        """ Remove a genre tag(s).

           Parameters:
                genres (list): List of strings.
        """
        self._edit_tags('genre', genres, remove=True)


class LabelMixin(object):
    """ Mixin for Plex objects that can have labels. """

    def addLabel(self, labels):
        """ Add a label tag(s).

           Parameters:
                labels (list): List of strings.
        """
        self._edit_tags('label', labels)

    def removeLabel(self, labels):
        """ Remove a label tag(s).

           Parameters:
                labels (list): List of strings.
        """
        self._edit_tags('label', labels, remove=True)


class MoodMixin(object):
    """ Mixin for Plex objects that can have moods. """

    def addMood(self, moods):
        """ Add a mood tag(s).

           Parameters:
                moods (list): List of strings.
        """
        self._edit_tags('mood', moods)

    def removeMood(self, moods):
        """ Remove a mood tag(s).

           Parameters:
                moods (list): List of strings.
        """
        self._edit_tags('mood', moods, remove=True)


class ProducerMixin(object):
    """ Mixin for Plex objects that can have producers. """

    def addProducer(self, producers):
        """ Add a producer tag(s).

           Parameters:
                producers (list): List of strings.
        """
        self._edit_tags('producer', producers)

    def removeProducer(self, producers):
        """ Remove a producer tag(s).

           Parameters:
                producers (list): List of strings.
        """
        self._edit_tags('producer', producers, remove=True)


class SimilarArtistMixin(object):
    """ Mixin for Plex objects that can have similar artists. """

    def addSimilarArtist(self, artists):
        """ Add a similar artist tag(s).

           Parameters:
                artists (list): List of strings.
        """
        self._edit_tags('similar', artists)

    def removeSimilarArtist(self, artists):
        """ Remove a similar artist tag(s).

           Parameters:
                artists (list): List of strings.
        """
        self._edit_tags('similar', artists, remove=True)


class StyleMixin(object):
    """ Mixin for Plex objects that can have styles. """

    def addStyle(self, styles):
        """ Add a style tag(s).

           Parameters:
                styles (list): List of strings.
        """
        self._edit_tags('style', styles)

    def removeStyle(self, styles):
        """ Remove a style tag(s).

           Parameters:
                styles (list): List of strings.
        """
        self._edit_tags('style', styles, remove=True)


class TagMixin(object):
    """ Mixin for Plex objects that can have tags. """

    def addTag(self, tags):
        """ Add a tag(s).

           Parameters:
                tags (list): List of strings.
        """
        self._edit_tags('tag', tags)

    def removeTag(self, tags):
        """ Remove a tag(s).

           Parameters:
                tags (list): List of strings.
        """
        self._edit_tags('tag', tags, remove=True)


class EditWriter(object):
    """ Mixin for Plex objects that can have writers. """

    def addWriter(self, writers):
        """ Add a writer tag(s).

           Parameters:
                writers (list): List of strings.
        """
        self._edit_tags('writer', writers)

    def removeWriter(self, writers):
        """ Remove a writer tag(s).

           Parameters:
                writers (list): List of strings.
        """
        self._edit_tags('writer', writers, remove=True)
