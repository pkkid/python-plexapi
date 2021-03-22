# -*- coding: utf-8 -*-
import os
from collections import defaultdict
from configparser import ConfigParser


class PlexConfig(ConfigParser):
    """ PlexAPI configuration object. Settings are stored in an INI file within the
        user's home directory and can be overridden after importing plexapi by simply
        setting the value. See the documentation section 'Configuration' for more
        details on available options.

        Parameters:
            path (str): Path of the configuration file to load.
    """

    def __init__(self, path):
        ConfigParser.__init__(self)
        self.read(path)
        self.data = self._asDict()

    def get(self, key, default=None, cast=None):
        """ Returns the specified configuration value or <default> if not found.

            Parameters:
                key (str): Configuration variable to load in the format '<section>.<variable>'.
                default: Default value to use if key not found.
                cast (func): Cast the value to the specified type before returning.
        """
        try:
            # First: check environment variable is set
            envkey = f"PLEXAPI_{key.upper().replace('.', '_')}"
            value = os.environ.get(envkey)
            if value is None:
                # Second: check the config file has attr
                section, name = key.lower().split('.')
                value = self.data.get(section, {}).get(name, default)
            return cast(value) if cast else value
        except:  # noqa: E722
            return default

    def _asDict(self):
        """ Returns all configuration values as a dictionary. """
        config = defaultdict(dict)
        config.update(self._defaults())
        for section in self._sections:
            for name, value in self._sections[section].items():
                if name != '__name__':
                    config[section.lower()][name.lower()] = value
        return dict(config)

    def _defaults(self):
        from uuid import getnode
        from platform import uname
        from plexapi import PROJECT, VERSION

        platform_name, device_name, platform_version = uname()[0:3]

        return {
            'header': {
                'provides': 'controller',
                'platform': platform_name,
                'platform_version': platform_version,
                'product': PROJECT,
                'version': VERSION,
                'device': platform_name,
                'device_name': device_name,
                'identifier': str(hex(getnode())),
            }
        }


def reset_base_headers():
    """ Convenience function returns a dict of all base X-Plex-* headers for session requests. """
    from plexapi import CONFIG

    return {
        'X-Plex-Platform': CONFIG.get('header.platorm', CONFIG.get('header.platform')),
        'X-Plex-Platform-Version': CONFIG.get('header.platform_version'),
        'X-Plex-Provides': CONFIG.get('header.provides'),
        'X-Plex-Product': CONFIG.get('header.product'),
        'X-Plex-Version': CONFIG.get('header.version'),
        'X-Plex-Device': CONFIG.get('header.device'),
        'X-Plex-Device-Name': CONFIG.get('header.device_name'),
        'X-Plex-Client-Identifier': CONFIG.get('header.identifier'),
        'X-Plex-Sync-Version': '2',
        'X-Plex-Features': 'external-media',
    }
