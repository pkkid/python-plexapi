def test_mark_movie_watched(a_movie):
    a_movie.markUnwatched()
    print('Marking movie watched: %s' % a_movie)
    print('View count: %s' % a_movie.viewCount)
    a_movie.markWatched()
    print('View count: %s' % a_movie.viewCount)
    assert a_movie.viewCount == 1, 'View count 0 after watched.'
    a_movie.markUnwatched()
    print('View count: %s' % a_movie.viewCount)
    assert a_movie.viewCount == 0, 'View count 1 after unwatched.'


def test_refresh_section(pms):
    shows = pms.library.section('TV Shows')
    #shows.refresh()


def test_refresh_video(pms):
    result = pms.search('16 blocks')
    #result[0].refresh()
