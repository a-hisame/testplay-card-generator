#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from .. import *
from PIL import Image

from tcgen.cardcanvas import CardCanvas


class CardCanvasTest(unittest.TestCase):
    ''' This class responsibility is drawing so it basically supports code coverage. '''

    def test_drawtext(self):
        canvas = CardCanvas()
        call_(canvas.draw_text(
            'SingleLine', 0, 0, color='#000000',
            shadowcolor='#FFFFFF'))
        call_(canvas.draw_text(
            'MultiLine\n\nMultiLine', 0, 0, color='#000000',
            maxwidth=canvas.width, maxheight=canvas.height))
        call_(canvas.draw_text(
            '[SAMPLE]' + 'SingleLine' * 30,
            0, 0, color='#000000',
            maxwidth=canvas.width, maxheight=canvas.height,
            breakseparator=']', fontsize=48))

    def test_draw_oneline_text(self):
        canvas = CardCanvas()
        call_(canvas.draw_oneline_text(
            'SingleLine', 0, 0,
            canvas.width, canvas.height, color='#000000'))
        call_(canvas.draw_oneline_text(
            'SingleLine', 0, 0,
            canvas.width, canvas.height,
            color='#000000', shadowcolor='#FFFFFF'))

    def test_draw_rect(self):
        canvas = CardCanvas()
        call_(canvas.draw_rect(
            0, 0, 100, 100,
            bordercolor=None, fillcolor=None))
        call_(canvas.draw_rect(
            0, 0, 100, 100,
            bordercolor='#000000', fillcolor='#FFFFFF'))
        call_(canvas.draw_rect(
            100, 100, 100, 100,
            bordercolor='#00000080', fillcolor='#FFFFFF80',
            border=4, alpha_enable=True))

    def test_draw_ellipse(self):
        canvas = CardCanvas()
        call_(canvas.draw_ellipse(
            0, 0, 100, 100,
            bordercolor=None, fillcolor=None))
        call_(canvas.draw_ellipse(
            0, 0, 100, 100,
            bordercolor='#000000', fillcolor='#FFFFFF'))
        call_(canvas.draw_ellipse(
            100, 100, 100, 100,
            bordercolor='#00000080', fillcolor='#FFFFFF80',
            border=4, alpha_enable=True))

    def test_draw_line(self):
        canvas = CardCanvas()
        call_(canvas.draw_line(
            0, 0, 100, 100, color='#FFFFFF'))
        call_(canvas.draw_line(
            0, 0, 100, 100, color='#FFFFFF80', alpha_enable=True))

    def test_draw_image(self):
        clip = Image.new(mode='RGBA', size=(32, 32), color=(255, 255, 255))
        canvas = CardCanvas()
        call_(canvas.draw_image(
            clip, 0, 0))
        call_(canvas.draw_image(
            clip, 0, 0, width=64, centerize=True))
        call_(canvas.draw_image(
            clip, 0, 0, height=64, centerize=True))

        clip2 = Image.new(mode='RGB', size=(32, 32), color=(255, 255, 255))
        call_(canvas.draw_image(
            clip2, 0, 0, width=64, height=64))
