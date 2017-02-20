# -*- coding: utf-8 -*-
import os, pytest, shlex, subprocess
from os.path import abspath, dirname, join


@pytest.mark.skipif(os.name == 'nt', reason='No make.bat specified for Windows')
def test_build_documentation():
    docroot = join(dirname(dirname(abspath(__file__))), 'docs')
    cmd = shlex.split('/usr/bin/make html --warn-undefined-variables')
    proc = subprocess.Popen(cmd, cwd=docroot)
    status = proc.wait()
    assert status == 0
