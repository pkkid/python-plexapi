def test_photo_Photoalbum(photoalbum):
    assert len(photoalbum.albums()) == 3
    assert len(photoalbum.photos()) == 3
    cats_in_bed = photoalbum.album("Cats in bed")
    assert len(cats_in_bed.photos()) == 7
    a_pic = cats_in_bed.photo("photo7")
    assert a_pic
