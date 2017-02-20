# -*- coding: utf-8 -*-
import os
import pytest
import shlex
import subprocess
from collections import defaultdict
from os.path import abspath, dirname, join

SKIP_EXAMPLES = ['Example 4']


@pytest.mark.skipif(os.name == 'nt', reason='No make.bat specified for Windows')
def test_build_documentation():
    docroot = join(dirname(dirname(abspath(__file__))), 'docs')
    cmd = shlex.split('/usr/bin/make html --warn-undefined-variables')
    proc = subprocess.Popen(cmd, cwd=docroot)
    status = proc.wait()
    assert status == 0


def test_readme_examples(pms):
    failed = 0
    examples = _fetch_examples(pms)
    assert len(examples), 'No examples found in README.md'
    for title, example in examples:
        if _check_run_example(title):
            try:
                print('\n%s\n%s' % (title, '-' * len(title)))
                exec('\n'.join(example))
            except Exception as err:
                failed += 1
                print('Error running test: %s\nError: %s' % (title, err))
    assert not failed, '%s examples raised an exception.' % failed


def _fetch_examples(pms):
    parsing = False
    examples = []
    filepath = join(dirname(dirname(abspath(__file__))), 'README.md')
    with open(filepath, 'r') as handle:
        for line in handle.read().split('\n'):
            if line.startswith('# Example '):
                parsing = True
                title = line.lstrip('# ')
                examples.append([title, ['plex = pms']])
            elif parsing and line == '```':
                parsing = False
            elif parsing:
                examples[-1][1].append(line)
    return examples


def _check_run_example(title):
    for skip_example in SKIP_EXAMPLES:
        if skip_example in title:
            return False
    return True
