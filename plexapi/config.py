# -*- coding: utf-8 -*-
"""
PlexConfig
Settings are stored in an INI file and can be overridden after import
plexapi by simply setting the value.
"""
from collections import defaultdict
try:
    from ConfigParser import ConfigParser  # Python2
except ImportError:
    from configparser import ConfigParser  # Python3


class PlexConfig(ConfigParser):

    def __init__(self, path):
        ConfigParser.__init__(self)
        self.read(path)
        self.data = self._asDict()

    def get(self, key, default=None, cast=None):
        try:
            section, name = key.split('.')
            value = self.data.get(section.lower(), {}).get(name.lower(), default)
            return cast(value) if cast else value
        except:
            return default

    def _asDict(self):
        config = defaultdict(dict)
        for section in self._sections:
            for name, value in self._sections[section].items():
                if name != '__name__':
                    config[section.lower()][name.lower()] = value
        return dict(config)


def reset_base_headers():
    import plexapi
    return {
        'X-Plex-Platform': plexapi.X_PLEX_PLATFORM,
        'X-Plex-Platform-Version': plexapi.X_PLEX_PLATFORM_VERSION,
        'X-Plex-Provides': plexapi.X_PLEX_PROVIDES,
        'X-Plex-Product': plexapi.X_PLEX_PRODUCT,
        'X-Plex-Version': plexapi.X_PLEX_VERSION,
        'X-Plex-Device': plexapi.X_PLEX_DEVICE,
        'X-Plex-Device-Name': plexapi.X_PLEX_DEVICE_NAME,
        'X-Plex-Client-Identifier': plexapi.X_PLEX_IDENTIFIER,
    }
