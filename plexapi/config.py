"""
PlexConfig
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
        self.data = self._as_dict()

    def get(self, key, default=None, cast=None):
        try:
            section, name = key.split('.')
            value = self.data.get(section.lower(), {}).get(name.lower(), default)
            return cast(value) if cast else value
        except:
            return default

    def _as_dict(self):
        config = defaultdict(dict)
        for section in self._sections:
            for name, value in self._sections[section].items():
                if name != '__name__':
                    config[section.lower()][name.lower()] = value
        return dict(config)
