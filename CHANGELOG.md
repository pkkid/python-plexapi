# Python-PlexAPI Change Log #

### Version 2.0.0 ###
* Added support for audio.
* Ability to compare NA value with None.
* Use a session for requests to get advantages of keepalive.
* Add tagging to tests to more easily run tests for a specific category.
* Bugfix: Level for a media object might not always be an integer.

### NAME CHANGES IN VERSION 2.0.0 (this will only ever happen on a major version increment) ###
* myplex.MyPlexResource.fetch_resources() renamed to myplex.MyPlexResource.fetchResources()
* myplex.MyPlexDevice.fetch_resources() renamed to myplex.MyPlexDevice.fetchResources()
* myplex.MyPlexResource.fetch_resources() renamed to myplex.MyPlexResource.fetchResources()
* media.VideoTag() renamed to media.MediaTag()
* media.MediaPart.select_stream() renamed to media.MediaPart.selectedStream()
* video.iter_parts() was renamed to video.iterParts()
* config.PlexConfig._as_dict() renamed to config.PlexConfig._asDict()
* build_item() renamed to buildItem() and moved to utils.py
* list_items() renamed to listItems() and moved to utils.py
* find_item() renamed to findItem() and moved to utils.py
* find_key() renamed to findKey() and moved to utils.py
* search_type() renamed to searchType() and moved to utils.py
