#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Define unittest tools for other unitetest.
usage: from (this path) import *
'''

import sys
import os
import unittest


try:
    # python 3
    from unittest import mock
except ImportError:
    # python 2
    import mock

from nose.tools import eq_, ok_


def call_(val):
    ''' procedure (means does not have valid return value) call test simple wrapper '''
    pass


def fail_():
    ''' fail unittest forcely '''
    ok_(False)


def datapath(filename):
    ''' return absolute path for unittest localfile '''
    return os.path.join(os.path.dirname(__file__), 'data', filename)
