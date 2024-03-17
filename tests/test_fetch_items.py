from plexapi.audio import Track
from plexapi.base import MediaContainer


def test_media_container_is_list():
    container = MediaContainer(None, None, Track(None, None))
    assert isinstance(container, list)
    assert len(container) == 1
    container.append(Track(None, None))
    assert len(container) == 2


def test_media_container_extend():
    container_1 = MediaContainer(None, None, Track(None, None))
    container_2 = MediaContainer(
        None, None, [Track(None, None), Track(None, None)]
    )
    container_1.size, container_2.size = 1, 2
    container_1.offset, container_2.offset = 3, 4
    container_1.totalSize = container_2.totalSize = 10
    container_1.extend(container_2)
    assert container_1.size == 1 + 2
    assert container_1.offset == min(3, 4)
    assert container_1.totalSize == 10


def test_fetch_items_with_media_container(show):
    all_episodes = show.episodes()
    some_episodes = show.episodes(maxresults=2)
    assert some_episodes.size == 2
    assert some_episodes.offset == 0
    assert some_episodes.totalSize == len(all_episodes)
