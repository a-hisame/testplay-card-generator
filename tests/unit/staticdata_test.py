#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from .. import *

from tcgen import staticdata


class StaticDataTest(unittest.TestCase):
    def test_staticfile_path(self):
        # found
        pathes = staticdata.staticfile_path({
            'bold': 'fonts/NotoSansCJKjp-Bold.ttf'
        })
        ok_('bold' in pathes)
        # not found
        self.assertRaises(IOError, lambda: staticdata.staticfile_path({
            'bold': 'fonts/NotoSansCJKjp-Bold.ttf.notfound'
        }))
