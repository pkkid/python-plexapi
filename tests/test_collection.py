# -*- coding: utf-8 -*-
import pytest
from plexapi.exceptions import BadRequest, NotFound

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
    assert collection.contentRating is None
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
    assert collection.title == "Test Collection"
    assert collection.titleSort == collection.title
    assert collection.type == "collection"
    assert utils.is_datetime(collection.updatedAt)
    assert collection.listType == "video"
    assert collection.metadataType == collection.subtype
    assert collection.isVideo is True
    assert collection.isAudio is False
    assert collection.isPhoto is False


def test_Collection_section(collection, movies):
    assert collection.section() == movies


def test_Collection_item(collection):
    item1 = collection.item("Elephants Dream")
    assert item1.title == "Elephants Dream"
    item2 = collection.get("Elephants Dream")
    assert item2.title == "Elephants Dream"
    assert item1 == item2
    with pytest.raises(NotFound):
        collection.item("Does not exist")


def test_Collection_items(collection):
    items = collection.items()
    assert len(items) == 1


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
    sort_dict = {"release": 0, "alpha": 1}
    for key, value in sort_dict.items():
        collection.sortUpdate(sort=key)
        collection.reload()
        assert collection.collectionSort == value
    with pytest.raises(BadRequest):
        collection.sortUpdate(sort="bad-sort")
    collection.sortUpdate("release")


def test_Collection_add_move_remove(collection, movies, show):
    movie = movies.get("Big Buck Bunny")
    assert movie not in collection
    collection.addItems(movie)
    collection.reload()
    assert movie in collection
    items = collection.items()
    collection.moveItem(items[1])
    items_moved = collection.reload().items()
    assert items_moved[0] == items[1]
    assert items_moved[1] == items[0]
    collection.moveItem(items[1], after=items[0])
    items_moved = collection.reload().items()
    assert items_moved[0] == items[0]
    assert items_moved[1] == items[1]
    collection.removeItems(movie)
    collection.reload()
    assert movie not in collection
    # Reset collection sort due to bug with corrupted XML response
    # for movies that have been moved in a collection and have
    # progress (updateProgress) or marked as played (markWatched)
    collection.sortUpdate("release")


def test_Collection_edit(collection, movies):
    fields = {"title", "titleSort", "contentRating", "summary"}
    title = collection.title
    titleSort = collection.titleSort
    contentRating = collection.contentRating
    summary = collection.summary

    newTitle = "New Title"
    newTitleSort = "New Title Sort"
    newContentRating = "New Content Rating"
    newSummary = "New Summary"
    collection.edit(
        title=newTitle,
        titleSort=newTitleSort,
        contentRating=newContentRating,
        summary=newSummary
    )
    collection.reload()
    assert collection.title == newTitle
    assert collection.titleSort == newTitleSort
    assert collection.contentRating == newContentRating
    assert collection.summary == newSummary
    lockedFields = [f.locked for f in collection.fields if f.name in fields]
    assert all(lockedFields)

    collection.edit(
        title=title,
        titleSort=titleSort,
        contentRating=contentRating or "",
        summary=summary,
        **{
            "title.locked": 0,
            "titleSort.locked": 0,
            "contentRating.locked": 0,
            "summary.locked": 0
        }
    )
    collection.reload()
    assert collection.title == title
    assert collection.titleSort == titleSort
    assert collection.contentRating is None
    assert collection.summary == summary
    lockedFields = [f.locked for f in collection.fields if f.name in fields]
    assert not any(lockedFields)


def test_Collection_create(plex, tvshows):
    title = "test_Collection_create"
    try:
        collection = plex.createCollection(
            title=title,
            section=tvshows,
            items=tvshows.all()
        )
        assert collection in tvshows.collections()
        assert collection.smart is False
    finally:
        collection.delete()


def test_Collection_createSmart(plex, tvshows):
    title = "test_Collection_createSmart"
    try:
        collection = plex.createCollection(
            title=title,
            section=tvshows,
            smart=True,
            limit=3,
            libtype="episode",
            sort="episode.index:desc",
            filters={"show.title": "Game of Thrones"}
        )
        assert collection in tvshows.collections()
        assert collection.smart is True
        assert len(collection.items()) == 3
        assert all([e.type == "episode" for e in collection.items()])
        assert all([e.grandparentTitle == "Game of Thrones" for e in collection.items()])
        assert collection.items() == sorted(collection.items(), key=lambda e: e.index, reverse=True)
        collection.updateFilters(limit=5, libtype="episode", filters={"show.title": "The 100"})
        collection.reload()
        assert len(collection.items()) == 5
        assert all([e.grandparentTitle == "The 100" for e in collection.items()])
    finally:
        collection.delete()


def test_Collection_exceptions(plex, movies, movie, artist):
    title = 'test_Collection_exceptions'
    try:
        collection = plex.createCollection(title, section=movies.title, items=movie)
        with pytest.raises(BadRequest):
            collection.updateFilters()
        with pytest.raises(BadRequest):
            collection.addItems(artist)
    finally:
        collection.delete()

    with pytest.raises(BadRequest):
        plex.createCollection(title, section=movies, items=[])
    with pytest.raises(BadRequest):
        plex.createCollection(title, section=movies, items=[movie, artist])

    try:
        collection = plex.createCollection(title, smart=True, section=movies.title, **{'year>>': 2000})
        with pytest.raises(BadRequest):
            collection.addItems(movie)
        with pytest.raises(BadRequest):
            collection.removeItems(movie)
        with pytest.raises(BadRequest):
            collection.moveItem(movie)
    finally:
        collection.delete()


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
