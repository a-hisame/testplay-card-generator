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
        TestCardGeneratorEngine.run(
            datapath('min-layout.yml'), datapath('min-data.csv'),
            'output.png', from_index=0, to_index=1,
            is_quiet=False, dryrun=True)
        TestCardGeneratorEngine.run(
            datapath('min-layout.yml'), datapath('min-data.csv'),
            'output.png', from_index=0, to_index=1,
            for_data=True, is_quiet=False, dryrun=True)

    def _test_engine(self, format='pdf', left_upper='normal', size=None, layers=None, border=2,
                     renderonly_ref=None, renderonly_values=None):
        return TestCardGeneratorEngine({
            'output': dict(
                format=format,
                tile=dict(left_upper=left_upper),
            ),
            'card': dict(
                size=dict(width=size[0], height=size[1]) if size else None,
                border=dict(width=border),
                layers=layers if layers else [],
                render_only=dict(ref=renderonly_ref, values=renderonly_values)
            )
        }, is_quiet=False, dryrun=True)

    def test_engine_basic_usage(self):
        call_(self._test_engine(format='png').save('output.png', []))
        self.assertRaises(
            ValueError,
            lambda: self._test_engine(format='jpg').save('output.jpg', []))

    def test_save_as_pdf(self):
        e1 = self._test_engine()
        # for just 0 page
        call_(e1.save_as_pdf('output.pdf', [], w=3, h=3))
        rows = [
            dict(header='value1'), dict(header='value2'),
            dict(header='value3'), dict(header='value4'),
            dict(header='value5'), dict(header='value6'),
            dict(header='value7'), dict(header='value8'),
            dict(header='value9'), dict(header='value10'),
        ]
        # for just 1 page
        call_(e1.save_as_pdf('output.pdf', rows[:9], w=3, h=3))
        # for 2 pages
        call_(e1.save_as_pdf('output.pdf', rows, w=1, h=1))
        call_(e1.save_as_pdf('output.pdf', rows, w=3, h=3))
        # for width is large more than height
        e2 = self._test_engine(left_upper='centerize')
        call_(e2.save_as_pdf('output.pdf', rows, w=2, h=4))
        self.assertRaises(
            ValueError,
            lambda: e2.save_as_pdf('output.pdf', rows, w=0, h=1))

    def test_save_as_images(self):
        e1 = self._test_engine(format='png')
        rows = [
            dict(header='value1'), dict(header='value2'),
            dict(header='value3'), dict(header='value4'),
            dict(header='value5'), dict(header='value6'),
            dict(header='value7'), dict(header='value8'),
            dict(header='value9'), dict(header='value10'),
        ]
        call_(e1.save_as_images('output', []))
        call_(e1.save_as_images('output', rows))
        self.assertRaises(
            ValueError,
            lambda: e1.save_as_images('output', rows, w=-1, h=-1))

    def test_renderonly(self):
        rows = [
            dict(header='value1'), dict(header='value2'),
            dict(header='value3'), dict(header='value4'),
            dict(header=10), dict(header='10'),
        ]
        # render all
        e1 = self._test_engine(renderonly_ref='header')
        eq_(len(e1.render_all(rows, w=1, h=1)), 6)

        # render if and only if header = value1
        e2 = self._test_engine(renderonly_ref='header',
                               renderonly_values='value1')
        eq_(len(e2.render_all(rows, w=1, h=1)), 1)

        # render if and only if header in [values2, values4, values5]
        e3 = self._test_engine(renderonly_ref='header',
                               renderonly_values=['value2', 'value4', 'value3'])
        eq_(len(e3.render_all(rows, w=1, h=1)), 3)

        e4 = self._test_engine(renderonly_ref='header', renderonly_values=10)
        eq_(len(e4.render_all(rows, w=1, h=1)), 2)

    def test_render(self):
        test_render_layers = [
            dict(
                type='image', always=True,
                x=0, y=0, source=datapath('dummy.png'),
            ),
            dict(
                type='rectangle', always=True,
                x=0, y=0, width=100, height=100,
                fillcolor='#FFFFFF80', bordercolor='#000000'
            ),
            dict(
                type='ellipse', always=True,
                x=0, y=0, width=100, height=100,
                fillcolor='#FFFFFF80', bordercolor='#000000'
            ),
            dict(
                type='text', always=True, label='FIXED',
                x=0, y=0, color='#000000'
            ),
            dict(
                type='text', ref='header',
                x=0, y=0, color='#000000'
            ),
            dict(
                type='text', ref='header?',
                x=0, y=0, color='#000000'
            ),
            dict(
                type='title', always='true', label='TITLE',
                x=0, y=0, width=200, height=40, color='#000000'
            ),
            dict(type='__invalid__'),  # ignored
        ]
        e1 = self._test_engine(size=(400, 600), layers=test_render_layers)
        call_(e1.save_as_pdf('output.pdf', [dict(header='value1')]))
        e2 = self._test_engine(layers=test_render_layers, border=0)
        call_(e2.save_as_pdf('output.pdf', [dict(header='value1')]))
