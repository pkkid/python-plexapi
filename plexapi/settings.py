# -*- coding: utf-8 -*-
from collections import defaultdict
from plexapi import log, utils
from plexapi.base import PlexObject
from plexapi.compat import string_type, quote
from plexapi.exceptions import BadRequest, NotFound


class Settings(PlexObject):
    """ Container class for all settings. Allows getting and setting PlexServer settings.

        Attributes:
            key (str): '/:/prefs'
            __AUTODOC_SETTINGS__
    """
    key = '/:/prefs'

    def __init__(self, server, data, initpath=None):
        self._settings = {}
        super(Settings, self).__init__(server, data, initpath)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            return self.__dict__[attr]
        return self.get(attr).value

    def __setattr__(self, attr, value):
        if not attr.startswith('_'):
            return self.get(attr).set(value)
        self.__dict__[attr] = value
            
    def _loadData(self, data):
        self._data = data
        for elem in data:
            id = utils.lowerFirst(elem.attrib['id'])
            if id in self._settings:
                self._settings[id]._loadData(elem)
                continue
            self._settings[id] = Setting(self._server, elem, self._initpath)

    def all(self):
        """ Returns a list of all :any:`~Setting` objects available. """
        return list(self._settings.values())

    def get(self, id):
        """ Return the setting with the specified id. """
        id = utils.lowerFirst(id)
        if id in self._settings:
            return self._settings[id]
        raise NotFound('Invalid setting id: %s' % id)

    def groups(self):
        """ Returns a dict of lists for all :any:`~Setting` objects grouped by setting group. """
        groups = defaultdict(list)
        for setting in self.all():
            groups[setting.group].append(setting)
        return dict(groups)

    def group(self, group):
        return self.groups().get(group, [])

    def save(self):
        params = {}
        for setting in self.all():
            if setting._setValue:
                log.info('Saving PlexServer setting %s = %s' % (setting.id, setting._setValue))
                params[setting.id] = quote(setting._setValue)
        if not params:
            raise BadRequest('No setting have been modified.')
        querystr = '&'.join(['%s=%s' % (k,v) for k,v in params.items()])
        url = '%s?%s' % (self.key, querystr)
        self._server.query(url, self._server._session.put)
        self.reload()


class Setting(PlexObject):
    _bool_cast = lambda x: True if x == 'true' else False
    _bool_str = lambda x: str(x).lower()
    TYPES = {
        'bool': {'type': bool, 'cast': _bool_cast, 'tostr': _bool_str},
        'double': {'type': float, 'cast': float, 'tostr': string_type},
        'int': {'type': int, 'cast': int, 'tostr': string_type},
        'text': {'type': string_type, 'cast': string_type, 'tostr': string_type},
    }

    def _loadData(self, data):
        self._setValue = None
        self.id = data.attrib.get('id')
        self.label = data.attrib.get('label')
        self.default = data.attrib.get('default')
        self.summary = data.attrib.get('summary')
        self.type = data.attrib.get('type')
        self.value = data.attrib.get('value')
        self.hidden = utils.cast(bool, data.attrib.get('hidden'))
        self.advanced = utils.cast(bool, data.attrib.get('advanced'))
        self.group = data.attrib.get('group')
        self.enumValues = self._getEnumValues(data)

    def _getEnumValues(self, data):
        enumstr = data.attrib.get('enumValues')
        if not enumstr:
            return None
        if ':' in enumstr:
            cast = self.TYPES[self.type]['cast']
            return {cast(k):v for k,v in [kv.split(':') for kv in enumstr.split('|')]}
        return enumstr.split('|')

    def set(self, value):
        # check a few things up front
        if not isinstance(value, self.TYPES[self.type]['type']):
            badtype = type(value).__name__
            raise BadRequest('Invalid value for %s: a %s is required, not %s' % (self.id, self.type, badtype))
        if self.enumValues and value not in self.enumValues:
            raise BadRequest('Invalid value for %s: %s not in %s' % (self.id, value, list(self.enumValues)))
        # store value off to the side until we call settings.save()
        tostr = self.TYPES[self.type]['tostr']
        self._setValue = tostr(value)
