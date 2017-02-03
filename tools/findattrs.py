#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find all attributes for each library type
"""
import pickle, os, sys
from collections import defaultdict
from plexapi.server import PlexServer
from xml.etree import ElementTree

MAX_SEEN = 9999
MAX_EXAMPLES = 10
PICKLE_PATH = '/tmp/findattrs.pickle'
ETYPES = ['artist', 'album', 'track', 'movie', 'show', 'season', 'episode']


def find_attrs(plex, key, result, examples, seen, indent=0):
    for elem in plex.query(key):
        attrs = sorted(elem.attrib.keys())
        etype = elem.attrib.get('type')
        if not etype or seen[etype] >= MAX_SEEN:
            continue
        seen[etype] += 1
        sys.stdout.write('.'); sys.stdout.flush()
        # find all attriutes in this element
        for attr in attrs:                
            result[attr].add(etype)
            if elem.attrib[attr] and len(examples[attr]) <= MAX_EXAMPLES:
                examples[attr].add(elem.attrib[attr])
        # iterate all subelements
        for subelem in elem:
            if subelem.tag not in ETYPES:
                subattr = subelem.tag + '[]'
                result[subattr].add(etype)
                if len(examples[subattr]) <= MAX_EXAMPLES:
                    xmlstr = ElementTree.tostring(subelem, encoding='utf8').split('\n')[1]
                    examples[subattr].add(xmlstr)
        # recurse into the main element (loading its key)
        if etype in ETYPES:
            subkey = elem.attrib['key']
            if key != subkey and seen[etype] < MAX_SEEN:
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
    for attr, etypes in sorted(result.items(), key=lambda x: x[0].lower()):
        args = [attr]
        args += [etype if etype in etypes else '--' for etype in ETYPES]
        args.append(list(examples[attr])[0][:30] if examples[attr] else '_NA_')
        print('%-23s  %-8s  %-8s  %-8s  %-8s  %-8s  %-8s  %-8s  %s' % tuple(args))

def print_summary_by_etype(result, examples):
    # find super attributes (in all etypes)
    result['super'] = set(['librarySectionID', 'index', 'titleSort'])
    for attr, etypes in result.items():
        if len(etypes) == 7:
            result['super'].add(attr)
    # print the summary
    for etype in ['super'] + ETYPES:
        print('\n--- %s ---' % etype)
        for attr in sorted(result.keys(), key=lambda x:x[0].lower()):
            if (etype in result[attr] and attr not in result['super']) or (etype == 'super' and attr in result['super']):
                example = list(examples[attr])[0][:80] if examples[attr] else '_NA_'
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
