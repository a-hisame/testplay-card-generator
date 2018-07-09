#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from .. import *

from tcgen.engine import TestCardGeneratorEngine


class EngineTest(unittest.TestCase):
    def test_load_with_dryrun(self):
        TestCardGeneratorEngine.run(
            datapath('min-layout.yml'), datapath('min-data.csv'),
            'output.pdf', is_quiet=True, dryrun=True)
