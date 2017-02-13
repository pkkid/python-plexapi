# -*- coding: utf-8 -*-
import pytest
import plexapi.utils as utils
from plexapi.exceptions import NotFound


def test_utils_toDatetime():
    assert str(utils.toDatetime('2006-03-03', format='%Y-%m-%d')) == '2006-03-03 00:00:00'
    assert str(utils.toDatetime('0'))[:-9] in ['1970-01-01', '1969-12-31']
    # should this handle args as '0' # no need element attrs are strings.


def _test_utils_threaded():
    # TODO: Implement test_utils_threaded
    pass


def test_utils_searchType():
    st = utils.searchType('movie')
    assert st == 1
    movie = utils.searchType(1)
    assert movie == '1'
    with pytest.raises(NotFound):
        utils.searchType('kekekekeke')


def _test_utils_listItems():
    # TODO: Implement test_utils_listItems
    pass


def _test_utils_listChoices(pms):
    # TODO: Implement test_utils_listChoices
    pass


def test_utils_joinArgs():
    test_dict = {'genre': 'action', 'type': 1337}
    assert utils.joinArgs(test_dict) == '?genre=action&type=1337'


def test_utils_isInt():
    assert utils.isInt(1) is True
    assert utils.isInt('got_you') is False
    assert utils.isInt('1337') is True


def _test_utils_findUsername():
    # TODO: Implement test_utils_findUsername
    pass


def _test_utils_findStreams():
    # TODO: Implement test_utils_findStreams
    pass


def _test_utils_findPlayer():
    # TODO: Implement test_utils_findPlayer
    pass


def _test_utils_findLocations():
    # TODO: Implement test_utils_findLocations
    pass


def _test_utils_findItem():
    # TODO: Implement test_utils_findItem
    pass


def test_utils_cast():
    t_int_int = utils.cast(int, 1)
    t_int_str_int = utils.cast(int, '1')
    t_bool_str_int = utils.cast(bool, '1')
    t_bool_int = utils.cast(bool, 1)
    t_float_int = utils.cast(float, 1)
    t_float_float = utils.cast(float, 1)
    t_float_str = utils.cast(float, 'kek')
    assert t_int_int == 1 and isinstance(t_int_int, int)
    assert t_int_str_int == 1 and isinstance(t_int_str_int, int)
    assert t_bool_str_int is True
    assert t_bool_int is True
    assert t_float_float == 1.0 and isinstance(t_float_float, float)
    assert t_float_str != t_float_str  # nan is never equal
    with pytest.raises(ValueError):
        t_bool_str = utils.cast(bool, 'kek')  # should we catch this in cast?


def test_utils_download(a_episode):
    without_session = utils.download(a_episode.getStreamURL(),
                                     filename=a_episode.location,
                                     mocked=True)
    assert without_session
    with_session = utils.download(a_episode.getStreamURL(),
                                  filename=a_episode.location,
                                  session=a_episode._server._session,
                                  mocked=True)
    assert with_session
    img = utils.download(a_episode.thumbUrl, filename=a_episode.title, mocked=True)
    assert img
