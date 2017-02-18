# -*- coding: utf-8 -*-
import os
import shlex
import subprocess

import pytest

# Uncomments when a make.bat file has been added to docs.
#@pytest.mark.xfail("os.environ.get('PLEX_TEST_TOKEN') is None",
#                   reason='Allow this to fail but not for devs or travis')
@pytest.mark.skipif(os.name == 'nt',
                    reason='Skipping this test for windows as there there is no make.bat.')
def test_build_documentation():
    docroot = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')

    cmd = shlex.split('/usr/bin/make html')

    proc = subprocess.Popen(cmd, cwd=docroot)
    status = proc.wait()
    assert status == 0
