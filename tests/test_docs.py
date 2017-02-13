# -*- coding: utf-8 -*-
import shlex, subprocess
from os.path import abspath, dirname, join


def test_build_documentation():
    docroot = join(dirname(dirname(abspath(__file__))), 'docs')
    cmd = shlex.split('/usr/bin/make html')
    proc = subprocess.Popen(cmd, cwd=docroot)
    status = proc.wait()
    assert status == 0
