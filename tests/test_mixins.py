# -*- coding: utf-8 -*-
from plexapi.utils import tag_singular

TEST_MIXIN_TAG = "Test Tag"


def _test_mixins_tag(obj, attr, tag_method):
    add_tag_method = getattr(obj, "add" + tag_method)
    remove_tag_method = getattr(obj, "remove" + tag_method)
    field_name = tag_singular(attr)
    _tags = lambda: [t.tag for t in getattr(obj, attr)]
    _fields = lambda: [f for f in obj.fields if f.name == field_name]
    # Check tag is not present to begin with
    tags = _tags()
    assert TEST_MIXIN_TAG not in tags
    # Add tag and lock the field
    add_tag_method(TEST_MIXIN_TAG)
    obj.reload()
    tags = _tags()
    fields = _fields()
    assert TEST_MIXIN_TAG in tags
    assert fields and fields[0].locked
    # Remove tag and unlock to field to restore the clean state
    remove_tag_method(TEST_MIXIN_TAG, locked=False)
    obj.reload()
    tags = _tags()
    fields = _fields()
    assert TEST_MIXIN_TAG not in tags
    assert not fields


def edit_collection(obj):
    _test_mixins_tag(obj, "collections", "Collection")


def edit_country(obj):
    _test_mixins_tag(obj, "countries", "Country")


def edit_director(obj):
    _test_mixins_tag(obj, "directors", "Director")


def edit_genre(obj):
    _test_mixins_tag(obj, "genres", "Genre")


def edit_label(obj):
    _test_mixins_tag(obj, "labels", "Label")


def edit_mood(obj):
    _test_mixins_tag(obj, "moods", "Mood")


def edit_producer(obj):
    _test_mixins_tag(obj, "producers", "Producer")


def edit_similar_artist(obj):
    _test_mixins_tag(obj, "similar", "SimilarArtist")


def edit_style(obj):
    _test_mixins_tag(obj, "styles", "Style")


def edit_tag(obj):
    _test_mixins_tag(obj, "tags", "Tag")


def edit_writer(obj):
    _test_mixins_tag(obj, "writers", "Writer")
