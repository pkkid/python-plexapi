# -*- coding: utf-8 -*-


class CollectionMixin(object):
    """ Mixin for Plex objects that can have collections. """

    def addCollection(self, collections, locked=True):
        """ Add a collection tag(s).

           Parameters:
                collections (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('collection', collections, locked=locked)

    def removeCollection(self, collections, locked=True):
        """ Remove a collection tag(s).

           Parameters:
                collections (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('collection', collections, locked=locked, remove=True)


class CountryMixin(object):
    """ Mixin for Plex objects that can have countries. """

    def addCountry(self, countries, locked=True):
        """ Add a country tag(s).

           Parameters:
                countries (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('country', countries, locked=locked)

    def removeCountry(self, countries, locked=True):
        """ Remove a country tag(s).

           Parameters:
                countries (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('country', countries, locked=locked, remove=True)


class DirectorMixin(object):
    """ Mixin for Plex objects that can have directors. """

    def addDirector(self, directors, locked=True):
        """ Add a director tag(s).

           Parameters:
                directors (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('director', directors, locked=locked)

    def removeDirector(self, directors, locked=True):
        """ Remove a director tag(s).

           Parameters:
                directors (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('director', directors, locked=locked, remove=True)


class GenreMixin(object):
    """ Mixin for Plex objects that can have genres. """

    def addGenre(self, genres, locked=True):
        """ Add a genre tag(s).

           Parameters:
                genres (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('genre', genres, locked=locked)

    def removeGenre(self, genres, locked=True):
        """ Remove a genre tag(s).

           Parameters:
                genres (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('genre', genres, locked=locked, remove=True)


class LabelMixin(object):
    """ Mixin for Plex objects that can have labels. """

    def addLabel(self, labels, locked=True):
        """ Add a label tag(s).

           Parameters:
                labels (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('label', labels, locked=locked)

    def removeLabel(self, labels, locked=True):
        """ Remove a label tag(s).

           Parameters:
                labels (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('label', labels, locked=locked, remove=True)


class MoodMixin(object):
    """ Mixin for Plex objects that can have moods. """

    def addMood(self, moods, locked=True):
        """ Add a mood tag(s).

           Parameters:
                moods (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('mood', moods, locked=locked)

    def removeMood(self, moods, locked=True):
        """ Remove a mood tag(s).

           Parameters:
                moods (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('mood', moods, locked=locked, remove=True)


class ProducerMixin(object):
    """ Mixin for Plex objects that can have producers. """

    def addProducer(self, producers, locked=True):
        """ Add a producer tag(s).

           Parameters:
                producers (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('producer', producers, locked=locked)

    def removeProducer(self, producers, locked=True):
        """ Remove a producer tag(s).

           Parameters:
                producers (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('producer', producers, locked=locked, remove=True)


class SimilarArtistMixin(object):
    """ Mixin for Plex objects that can have similar artists. """

    def addSimilarArtist(self, artists, locked=True):
        """ Add a similar artist tag(s).

           Parameters:
                artists (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('similar', artists, locked=locked)

    def removeSimilarArtist(self, artists, locked=True):
        """ Remove a similar artist tag(s).

           Parameters:
                artists (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('similar', artists, locked=locked, remove=True)


class StyleMixin(object):
    """ Mixin for Plex objects that can have styles. """

    def addStyle(self, styles, locked=True):
        """ Add a style tag(s).

           Parameters:
                styles (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('style', styles, locked=locked)

    def removeStyle(self, styles, locked=True):
        """ Remove a style tag(s).

           Parameters:
                styles (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('style', styles, locked=locked, remove=True)


class TagMixin(object):
    """ Mixin for Plex objects that can have tags. """

    def addTag(self, tags, locked=True):
        """ Add a tag(s).

           Parameters:
                tags (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('tag', tags, locked=locked)

    def removeTag(self, tags, locked=True):
        """ Remove a tag(s).

           Parameters:
                tags (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('tag', tags, locked=locked, remove=True)


class EditWriter(object):
    """ Mixin for Plex objects that can have writers. """

    def addWriter(self, writers, locked=True):
        """ Add a writer tag(s).

           Parameters:
                writers (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('writer', writers, locked=locked)

    def removeWriter(self, writers, locked=True):
        """ Remove a writer tag(s).

           Parameters:
                writers (list): List of strings.
                locked (bool): True (default) to lock the field, False to unlock the field.
        """
        self._edit_tags('writer', writers, locked=locked, remove=True)
