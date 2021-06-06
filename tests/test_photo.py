# -*- coding: utf-8 -*-
from . import test_media, test_mixins


def test_photo_Photoalbum(photoalbum):
    assert len(photoalbum.albums()) == 3
    assert len(photoalbum.photos()) == 3
    cats_in_bed = photoalbum.album("Cats in bed")
    assert len(cats_in_bed.photos()) == 7
    a_pic = cats_in_bed.photo("photo7")
    assert a_pic


def test_photo_Photoalbum_mixins_images(photoalbum):
    test_mixins.edit_art(photoalbum)
    test_mixins.edit_poster(photoalbum)
    test_mixins.attr_artUrl(photoalbum)
    test_mixins.attr_posterUrl(photoalbum)


def test_photo_Photoalbum_mixins_rating(photoalbum):
    test_mixins.edit_rating(photoalbum)


def test_photo_Photo_mixins_rating(photo):
    test_mixins.edit_rating(photo)


def test_photo_Photo_mixins_tags(photo):
    test_mixins.edit_tag(photo)


def test_photo_Photo_media_tags(photo):
    photo.reload()
    test_media.tag_tag(photo)
