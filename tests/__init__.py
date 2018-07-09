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
