# -*- coding: utf-8 -*-
import pytest
from plexapi.exceptions import BadRequest

from . import conftest as utils
from . import test_mixins


def test_Collection_attrs(collection):
    assert utils.is_datetime(collection.addedAt)
    assert collection.art is None
    assert collection.artBlurHash is None
    assert collection.childCount == 1
    assert collection.collectionMode == -1
    assert collection.collectionPublished is False
    assert collection.collectionSort == 0
    assert collection.content is None
    assert collection.contentRating
    assert not collection.fields
    assert collection.guid.startswith("collection://")
    assert utils.is_int(collection.index)
    assert collection.key.startswith("/library/collections/")
    assert not collection.labels
    assert utils.is_int(collection.librarySectionID)
    assert collection.librarySectionKey == "/library/sections/%s" % collection.librarySectionID
    assert collection.librarySectionTitle == "Movies"
    assert utils.is_int(collection.maxYear)
    assert utils.is_int(collection.minYear)
    assert utils.is_int(collection.ratingCount)
    assert utils.is_int(collection.ratingKey)
    assert collection.smart is False
    assert collection.subtype == "movie"
    assert collection.summary == ""
    assert collection.thumb.startswith("/library/collections/%s/composite" % collection.ratingKey)
    assert collection.thumbBlurHash is None
    assert collection.title == "Marvel"
    assert collection.titleSort == collection.title
    assert collection.type == "collection"
    assert utils.is_datetime(collection.updatedAt)


def test_Collection_modeUpdate(collection):
    mode_dict = {"default": -1, "hide": 0, "hideItems": 1, "showItems": 2}
    for key, value in mode_dict.items():
        collection.modeUpdate(mode=key)
        collection.reload()
        assert collection.collectionMode == value
    with pytest.raises(BadRequest):
        collection.modeUpdate(mode="bad-mode")
    collection.modeUpdate("default")


def test_Collection_sortUpdate(collection):
    sort_dict = {"release": 0, "alpha": 1, "custom": 2}
    for key, value in sort_dict.items():
        collection.sortUpdate(sort=key)
        collection.reload()
        assert collection.collectionSort == value
    with pytest.raises(BadRequest):
        collection.sortUpdate(sort="bad-sort")
    collection.sortUpdate("release")


def test_Collection_edit(collection):
    edits = {"titleSort.value": "New Title Sort", "titleSort.locked": 1}
    collectionTitleSort = collection.titleSort
    collection.edit(**edits)
    collection.reload()
    for field in collection.fields:
        if field.name == "titleSort":
            assert collection.titleSort == "New Title Sort"
            assert field.locked is True
    collection.edit(**{"titleSort.value": collectionTitleSort, "titleSort.locked": 0})


def test_Collection_delete(movies):
    delete_collection = "delete_collection"
    movie = movies.get("Sintel")
    movie.addCollection(delete_collection)
    collections = movies.collections(title=delete_collection)
    assert len(collections) == 1
    collections[0].delete()
    collections = movies.collections(title=delete_collection)
    assert len(collections) == 0


def test_Collection_item(collection):
    item1 = collection.item("Elephants Dream")
    assert item1.title == "Elephants Dream"
    item2 = collection.get("Elephants Dream")
    assert item2.title == "Elephants Dream"
    assert item1 == item2


def test_Collection_items(collection):
    items = collection.items()
    assert len(items) == 1


def test_Collection_posters(collection):
    posters = collection.posters()
    assert posters


def test_Collection_art(collection):
    arts = collection.arts()
    assert not arts  # Collection has no default art


def test_Collection_mixins_images(collection):
    test_mixins.edit_art(collection)
    test_mixins.edit_poster(collection)
    test_mixins.attr_artUrl(collection)
    test_mixins.attr_posterUrl(collection)


def test_Collection_mixins_rating(collection):
    test_mixins.edit_rating(collection)


def test_Collection_mixins_tags(collection):
    test_mixins.edit_label(collection)
