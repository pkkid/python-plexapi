# -*- coding: utf-8 -*-
import shlex, subprocess
from os.path import abspath, dirname, join


def test_build_documentation():
    # TODO: assert no WARNING messages in sphinx output
    docroot = join(dirname(dirname(abspath(__file__))), 'docs')
    cmd = shlex.split('/usr/bin/make html --warn-undefined-variables')
    proc = subprocess.Popen(cmd, cwd=docroot)
    status = proc.wait()
    assert status == 0
