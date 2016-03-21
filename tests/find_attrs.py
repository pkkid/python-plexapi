# -*- coding: utf-8 -*-
"""
Find all attributes for each library type
"""
import pickle, os, sys
from collections import defaultdict
from plexapi.server import PlexServer

MAX_SEEN = 9999
PICKLE_PATH = '/tmp/find_attrs.pickle'


def find_attrs(plex, key, result, examples, seen, indent=0):
    for elem in plex.query(key):
        attrs = sorted(elem.attrib.keys())
        etype = elem.attrib.get('type')
        if not etype: continue
        seen[etype] += 1
        sys.stdout.write('.'); sys.stdout.flush()
        for attr in attrs:                
            result[attr].add(etype)
            if elem.attrib[attr] and len(examples[attr]) <= 10:
                examples[attr].add(elem.attrib[attr])
        for subelem in elem:
            if subelem.tag not in ('artist', 'album', 'track', 'show', 'season', 'episode'):
                subattr = subelem.tag + '[]'
                result[subattr].add(etype)
                subtag = subelem.attrib.get('tag')
                if subtag and len(examples[subattr]) <= 10:
                    examples[subattr].add(subtag)
        if etype in ('artist', 'album', 'track', 'show', 'season', 'episode'):
            subkey = elem.attrib['key']
            if key != subkey:
                find_attrs(plex, subkey, result, examples, seen, indent+2)
    return result


def find_all_attrs():
    try:
        result = defaultdict(set)
        examples = defaultdict(set)
        seen = defaultdict(int)
        plex = PlexServer()
        find_attrs(plex, '/status/sessions', result, examples, seen)
        for section in plex.library.sections():
            for elem in section.all():
                # check weve seen too many of this type of elem
                if seen[elem.type] >= MAX_SEEN:
                    continue
                seen[elem.type] += 1
                # fetch the xml for this elem
                key = elem.key.replace('/children', '')
                find_attrs(plex, key, result, examples, seen)
    except KeyboardInterrupt:
        pass
    return result, examples, seen
    
def print_results(result, examples, seen):
    print_general_summary(result, examples)
    print_summary_by_etype(result, examples)
    print_seen_etypes(seen)
    
def print_general_summary(result, examples):
    print('\n--- general summary ---')
    sorted_attrs = sorted(result.items(), key=lambda x: x[0])
    for attr, etypes in sorted_attrs:
        print('%-23s  %-8s  %-8s  %-8s  %-8s  %-8s  %-8s  %-8s  %s' % (attr,
            'artist' if 'artist' in etypes else '--',
            'album' if 'album' in etypes else '--',
            'track' if 'track' in etypes else '--',
            'movie' if 'movie' in etypes else '--',
            'show' if 'show' in etypes else '--',
            'season' if 'season' in etypes else '--',
            'episode' if 'episode' in etypes else '--',
            list(examples[attr])[0][:30] if examples[attr] else '_NA_',
        ))  # noqa

def print_summary_by_etype(result, examples):
    # find super attributes (in all etypes)
    super_attrs = set(['librarySectionID', 'index', 'titleSort'])
    for attr, etypes in result.items():
        if len(etypes) == 7:
            super_attrs.add(attr)
    # print the summary
    for etype in ('super', 'artist', 'album', 'track', 'movie', 'show', 'season', 'episode'):
        print('\n--- %s ---' % etype)
        if etype == 'super':
            for attr in sorted(super_attrs):
                example = list(examples[attr])[0][:50] if examples[attr] else '_NA_'
                print('%-23s  %s' % (attr, example))
        else:
            for attr in sorted(result.keys()):
                if attr not in super_attrs and etype in result[attr]:
                    example = list(examples[attr])[0][:50] if examples[attr] else '_NA_'
                    print('%-23s  %s' % (attr, example))
        
def print_seen_etypes(seen):
    print('\n')
    for etype, count in seen.items():
        print('%-8s %s' % (etype, count))
        

def save_pickle(result, examples, seen):
    with open(PICKLE_PATH, 'w') as handle:
        pickle.dump({'result':result, 'examples':examples, 'seen':seen}, handle)


def load_pickle():
    if not os.path.exists(PICKLE_PATH):
        return None, None, None
    with open(PICKLE_PATH, 'r') as handle:
        data = pickle.load(handle)
        return data['result'], data['examples'], data['seen']

    
if __name__ == '__main__':
    result, examples, seen = load_pickle()
    if not result:
        result, examples, seen = find_all_attrs()
        save_pickle(result, examples, seen)
    print_results(result, examples, seen)
