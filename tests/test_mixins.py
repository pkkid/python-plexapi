# -*- coding: utf-8 -*-
TEST_MIXIN_TAG = "Test Tag"


def _test_mixins_tag(obj, attr, tag_method):
    add_tag_method = getattr(obj, 'add' + tag_method)
    remove_tag_method = getattr(obj, 'remove' + tag_method)
    assert TEST_MIXIN_TAG not in [tag.tag for tag in getattr(obj, attr)]
    add_tag_method(TEST_MIXIN_TAG)
    obj.reload()
    assert TEST_MIXIN_TAG in [tag.tag for tag in getattr(obj, attr)]
    remove_tag_method(TEST_MIXIN_TAG)
    # obj.reload()
    obj = obj._server.fetchItem(obj.ratingKey)  # Workaround for issue #660
    assert TEST_MIXIN_TAG not in [tag.tag for tag in getattr(obj, attr)]


def edit_collection(obj):
    _test_mixins_tag(obj, 'collections', 'Collection')


def edit_country(obj):
    _test_mixins_tag(obj, 'countries', 'Country')


def edit_director(obj):
    _test_mixins_tag(obj, 'directors', 'Director')


def edit_genre(obj):
    _test_mixins_tag(obj, 'genres', 'Genre')


def edit_label(obj):
    _test_mixins_tag(obj, 'labels', 'Label')


def edit_mood(obj):
    _test_mixins_tag(obj, 'moods', 'Mood')


def edit_producer(obj):
    _test_mixins_tag(obj, 'producers', 'Producer')


def edit_similar_artist(obj):
    _test_mixins_tag(obj, 'similar', 'SimilarArtist')


def edit_style(obj):
    _test_mixins_tag(obj, 'styles', 'Style')


def edit_tag(obj):
    _test_mixins_tag(obj, 'tags', 'Tag')


def edit_writer(obj):
    _test_mixins_tag(obj, 'writers', 'Writer')
