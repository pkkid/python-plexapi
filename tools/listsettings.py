# -*- coding: utf-8 -*-
from plexapi.server import PlexServer


def list_settings():
    plex = PlexServer()
    groups = sorted(plex.settings.groups().items())
    for group, settings in groups:
        title = group.title()
        print('%s Settings' % (title or 'Misc'))
        print('---------------------------')
        for s in settings:
            label = '%s. ' % s.label if s.label else ''
            summary = '%s '  % s.summary if s.summary else ''
            enums = '; available: %s' % s._data.attrib['enumValues'] if 'enumValues' in s._data.attrib else ''
            default = '(default: %s%s)' % (s.default, enums) if s.default else ''
            desc = '%s%s%s' % (label, summary, default)
            print('* **%s** (%s): %s' % (s.id, s.type, desc))
        print('')


if __name__ == '__main__':
    list_settings()
