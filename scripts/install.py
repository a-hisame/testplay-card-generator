#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import shutil


here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, '..')
os.chdir(root)


def _run(command):
    subprocess.check_call(command, shell=True)


# install tcgen project by pip
requirements = ['requirements.txt'] + [req for req in sys.argv[1:]]
_run('pip install {}'.format(
    ' '.join(['-r {}'.format(req) for req in requirements])
))


# pack to wheel
if all([os.path.exists('dist'), os.path.isdir('dist')]):
    shutil.rmtree('dist')
_run('python setup.py bdist_wheel')

# install built whl
wheel_dist = os.listdir('dist')[0]
wheel_path = os.path.join('dist', wheel_dist)

_run('pip install {} --upgrade'.format(wheel_path))
