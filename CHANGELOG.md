# Python-PlexAPI Change Log #

### Version 2.0.0 ###
* Added support for audio.
* Ability to compare NA value with None.
* Use a session for requests to get advantages of keepalive.
* Add tagging to tests to more easily run tests for a specific category.
* Bugfix: Level for a media object might not always be an integer.

### NAME CHANGES IN VERSION 2.0.0 (this will only ever happen on a major version increment) ###
* MediaPart.select_stream() renamed to MediaPart.selectedStream()
* MyPlexResource.fetch_resources() renamed to MyPlexResource.fetchResources()
* MyPlexDevice.fetch_resources() renamed to MyPlexDevice.fetchResources()
* MyPlexResource.fetch_resources() renamed to MyPlexResource.fetchResources()
* media.VideoTag() renamed to media.MediaTag()
* build_tem() renamed to buildItem() and moved to utils.py
* list_items() renamed to listItems() and moved to utils.py
* find_item() renamed to findItem() and moved to utils.py
* find_key() renamed to findKey() and moved to utils.py
* search_type() renamed to searchType() and moved to utils.py
* PlexConfig._as_dict() renamed to PlexConfig._asDict()
