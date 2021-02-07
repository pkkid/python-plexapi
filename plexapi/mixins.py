# -*- coding: utf-8 -*-


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
