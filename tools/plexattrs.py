#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script loops through all media items to build a collection of attributes on
each media type. The resulting list can be compared with the current object 
implementation in python-plex api to track new attributes and depricate old ones.
"""
import argparse, copy, pickle, plexapi, os, sys
from collections import defaultdict
from datetime import datetime
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.utils import NA

CACHEPATH = '/tmp/findattrs.pickle'
NAMESPACE =  {
    'xml': defaultdict(int),
    'obj': defaultdict(int),
    'examples': defaultdict(set),
    'total': 0
}
IGNORES = {
    'server.PlexServer': ['baseurl', 'token', 'session'],
    'myplex.ResourceConnection': ['httpuri'],
    'client.PlexClient': ['baseurl'],
}

class PlexAttributes():

    def __init__(self, opts):
        self.opts = opts                                            # command line options
        self.clsnames = [c for c in opts.clsnames.split(',') if c]  # list of clsnames to report (blank=all)
        self.account = MyPlexAccount.signin()                       # MyPlexAccount instance
        self.plex = PlexServer()                                    # PlexServer instance
        self.attrs = defaultdict(dict)                              # Attrs result set

    def run(self):
        # MyPlex
        self._load_attrs(self.account)
        self._load_attrs(self.account.devices())
        for resource in self.account.resources():
            self._load_attrs(resource)
            self._load_attrs(resource.connections)
        self._load_attrs(self.account.users())
        # Server
        self._load_attrs(self.plex)
        self._load_attrs(self.plex.account())
        self._load_attrs(self.plex.history()[:20])
        self._load_attrs(self.plex.playlists())
        for search in ('cre', 'ani', 'mik', 'she'):
            self._load_attrs(self.plex.search('cre'))
        self._load_attrs(self.plex.sessions())
        # Library
        self._load_attrs(self.plex.library)
        self._load_attrs(self.plex.library.sections())
        self._load_attrs(self.plex.library.all()[:20])
        self._load_attrs(self.plex.library.onDeck()[:20])
        self._load_attrs(self.plex.library.recentlyAdded()[:20])
        for search in ('cat', 'dog', 'rat'):
            self._load_attrs(self.plex.library.search(search)[:20])
        # Client
        self._load_attrs(self.plex.clients())
        return self

    def _load_attrs(self, obj):
        if isinstance(obj, (list, tuple)):
            return [self._parse_objects(x) for x in obj]
        return self._parse_objects(obj)

    def _parse_objects(self, obj):
        clsname = '%s.%s' % (obj.__module__, obj.__class__.__name__)
        clsname = clsname.replace('plexapi.', '')
        if self.clsnames and clsname not in self.clsnames:
            return None
        sys.stdout.write('.'); sys.stdout.flush()
        if clsname not in self.attrs:
            self.attrs[clsname] = copy.deepcopy(NAMESPACE)
        self.attrs[clsname]['total'] += 1
        self._load_xml_attrs(clsname, obj._data, self.attrs[clsname]['xml'], self.attrs[clsname]['examples'])
        self._load_obj_attrs(clsname, obj, self.attrs[clsname]['obj'])

    def _load_xml_attrs(self, clsname, elem, attrs, examples):
        if elem in (None, NA): return None
        for attr in sorted(elem.attrib.keys()):
            attrs[attr] += 1
            if elem.attrib[attr] and len(examples[attr]) <= self.opts.examples:
                examples[attr].add(elem.attrib[attr])

    def _load_obj_attrs(self, clsname, obj, attrs):
        for attr, value in obj.__dict__.items():
            if value in (None, NA) or isinstance(value, (str, bool, float, int, datetime)):
                if not attr.startswith('_') and attr not in IGNORES.get(clsname, []):
                    attrs[attr] += 1

    def print_report(self):
        total_attrs = 0
        for clsname in sorted(self.attrs.keys()):
            meta = self.attrs[clsname]
            count = meta['total']
            print(_('\n%s (%s)\n%s' % (clsname, count, '-'*(len(clsname)+8)), 'yellow'))
            attrs = sorted(set(list(meta['xml'].keys()) + list(meta['obj'].keys())))
            for attr in attrs:
                state = self._attr_state(attr, meta)
                count = meta['xml'].get(attr, 0)
                example = list(meta['examples'].get(attr, ['--']))[0][:80]
                print('%-4s %4s  %-30s  %s' % (state, count, attr, example))
                total_attrs += count
        print(_('\nSUMMARY\n------------', 'yellow'))
        print('Plex Version     %s' % self.plex.version)
        print('PlexAPI Version  %s' % plexapi.VERSION)
        print('Total Objects    %s\n' % sum([x['total'] for x in self.attrs.values()]))
        for clsname in sorted(self.attrs.keys()):
            print('%-34s %s' % (clsname, self.attrs[clsname]['total']))
        print()

    def _attr_state(self, attr, meta):
        if attr in meta['xml'].keys() and attr not in meta['obj'].keys(): return _('new', 'blue')
        if attr not in meta['xml'].keys() and attr in meta['obj'].keys(): return _('old', 'red')
        return _('   ', 'green')

    

def _(text, color):
    FMTSTR = '\033[%dm%s\033[0m'
    COLORS = {'blue':34, 'cyan':36, 'green':32, 'grey':30, 'magenta':35, 'red':31, 'white':37, 'yellow':33}
    return FMTSTR % (COLORS[color], text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='resize and copy starred photos')
    parser.add_argument('-f', '--force', default=False, action='store_true', help='force a full refresh of attributes.')
    parser.add_argument('-m', '--max', default=99999, help='max number of objects to load.')
    parser.add_argument('-e', '--examples', default=10, help='max number of example values to load.')
    parser.add_argument('-c', '--clsnames', default='', help='only report the following class names')
    opts = parser.parse_args()
    # Load the plexattrs object
    plexattrs = None
    if not opts.force and os.path.exists(CACHEPATH):
        with open(CACHEPATH, 'rb') as handle:
            plexattrs = pickle.load(handle)
    if not plexattrs:
        plexattrs = PlexAttributes(opts).run()
        with open(CACHEPATH, 'wb') as handle:
            pickle.dump(plexattrs, handle)
    # Print Report
    plexattrs.print_report()





# MAX_SEEN = 9999
# MAX_EXAMPLES = 10
# PICKLE_PATH = '/tmp/findattrs.pickle'
# ETYPES = ['artist', 'album', 'track', 'movie', 'show', 'season', 'episode']
# COLORS = {'blue':34, 'cyan':36, 'green':32, 'grey':30, 'magenta':35, 'red':31, 'white':37, 'yellow':33}
# RESET = '\033[0m'

# def color(text, color=None):
#     """ Colorize text {red, green, yellow, blue, magenta, cyan, white}. """
#     fmt_str = '\033[%dm%s'
#     if color is not None:
#         text = fmt_str % (COLORS[color], text)
#     text += RESET
#     return text

# def find_attrs(plex, key, result, examples, seen, indent=0):
#     for elem in plex.query(key):
#         attrs = sorted(elem.attrib.keys())
#         etype = elem.attrib.get('type')
#         if not etype or seen[etype] >= MAX_SEEN:
#             continue
#         seen[etype] += 1
#         sys.stdout.write('.'); sys.stdout.flush()
#         # find all attriutes in this element
#         for attr in attrs:                
#             result[attr].add(etype)
#             if elem.attrib[attr] and len(examples[attr]) <= MAX_EXAMPLES:
#                 examples[attr].add(elem.attrib[attr])
#         # iterate all subelements
#         for subelem in elem:
#             if subelem.tag not in ETYPES:
#                 subattr = subelem.tag + '[]'
#                 result[subattr].add(etype)
#                 if len(examples[subattr]) <= MAX_EXAMPLES:
#                     xmlstr = ElementTree.tostring(subelem, encoding='utf8').split('\n')[1]
#                     examples[subattr].add(xmlstr)
#         # recurse into the main element (loading its key)
#         if etype in ETYPES:
#             subkey = elem.attrib['key']
#             if key != subkey and seen[etype] < MAX_SEEN:
#                 find_attrs(plex, subkey, result, examples, seen, indent+2)
#     return result

# def find_all_attrs():
#     try:
#         result = defaultdict(set)
#         examples = defaultdict(set)
#         seen = defaultdict(int)
#         plex = PlexServer()
#         find_attrs(plex, '/status/sessions', result, examples, seen)
#         for section in plex.library.sections():
#             for elem in section.all():
#                 # check weve seen too many of this type of elem
#                 if seen[elem.type] >= MAX_SEEN:
#                     continue
#                 seen[elem.type] += 1
#                 # fetch the xml for this elem
#                 key = elem.key.replace('/children', '')
#                 find_attrs(plex, key, result, examples, seen)
#     except KeyboardInterrupt:
#         pass
#     return result, examples, seen
    
# def print_results(result, examples, seen):
#     print_general_summary(result, examples)
#     print_summary_by_etype(result, examples)
#     print_seen_etypes(seen)
    
# def print_general_summary(result, examples):
#     print(color('\n--- general summary ---', 'cyan'))
#     for attr, etypes in sorted(result.items(), key=lambda x: x[0].lower()):
#         args = [attr]
#         args += [etype if etype in etypes else '--' for etype in ETYPES]
#         args.append(list(examples[attr])[0][:30] if examples[attr] else '_NA_')
#         print('%-23s  %-8s  %-8s  %-8s  %-8s  %-8s  %-8s  %-8s  %s' % tuple(args))

# def print_summary_by_etype(result, examples):
#     # find super attributes (in all etypes)
#     result['super'] = set(['librarySectionID', 'index', 'titleSort'])
#     for attr, etypes in result.items():
#         if len(etypes) == 7:
#             result['super'].add(attr)
#     # print the summary
#     for etype in ['super'] + ETYPES:
#         print(color('\n--- %s ---' % etype, 'cyan'))
#         for attr in sorted(result.keys(), key=lambda x:x[0].lower()):
#             if (etype in result[attr] and attr not in result['super']) or (etype == 'super' and attr in result['super']):
#                 example = list(examples[attr])[0][:80] if examples[attr] else '_NA_'
#                 print('%-23s  %s' % (attr, example))
        
# def print_seen_etypes(seen):
#     print('\n')
#     for etype, count in seen.items():
#         print('%-8s %s' % (etype, count))
