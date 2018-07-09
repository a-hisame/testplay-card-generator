#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from .. import *

import tcgen


def test_entrypoint_call():
    return
    call_(tcgen.main([
        '--layout', 'layout-sample.yml',
        '--data', 'data-sample.csv',
        '--dryrun'
    ]))
    call_(tcgen.main([
        '--layout', 'layout-sample.yml',
        '--data', 'data-sample.csv',
        '--dryrun', '--quiet'
    ]))
