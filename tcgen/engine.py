#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import codecs
import logging
import traceback

import yaml
from dotmap import DotMap
from PIL import Image

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .cardcanvas import CardCanvas

logger = logging.getLogger(__name__)


def _s(elem, else_value=None):
    return elem if elem else else_value


class TestCardGeneratorEngine:
    ''' Create testplay card printing file from layout configuration and data source '''

    @staticmethod
    def run(layoutfile, datafile, output, is_quiet=False):
        ''' Most basically usage '''
        try:
            engine = TestCardGeneratorEngine.load(layoutfile, is_quiet)
            records = TestCardGeneratorEngine.csv2records(datafile)
            engine.save(output, records)
        except:
            traceback.print_exc()

    @staticmethod
    def load(ymlpath, is_quiet=False, encoding='utf8'):
        ''' engine instance factory method '''
        with codecs.open(ymlpath, 'r', encoding=encoding) as fh:
            layout = yaml.load(fh)
        return TestCardGeneratorEngine(layout=layout, is_quiet=is_quiet)

    @staticmethod
    def csv2records(csvpath, encoding='utf8'):
        ''' create row items from csv data source '''
        with codecs.open(csvpath, 'r', encoding=encoding) as fh:
            reader = csv.DictReader(fh)
            return [row for row in reader]

    def __init__(self, layout=None, is_quiet=False):
        ''' not recommend to use constractor directly, use TestCardGeneratorEngine.load'''
        self.definition = DotMap(layout)
        self.is_quiet = is_quiet
        if is_quiet:
            def _console(*arvg, **kwargv):
                pass
            self.console = _console
        else:
            self.console = print

    def _draw_image(self, canvas, layer, filename):
        imagefile = layer.source if layer.source else filename
        canvas.draw_image(
            image=Image.open(imagefile),
            x=layer.get('x', 0),
            y=layer.get('y', 0),
            width=layer.get('width', None),
            height=layer.get('height', None),
            centerize=layer.get('centerize', False),
        )

    def _draw_rectangle(self, canvas, layer, content):
        if layer.skip_empty and (not content):
            logger.debug('%s skip_empty is enable and content is empty',
                         layer.name)
            return
        canvas.draw_rect(
            x=layer.get('x', 0),
            y=layer.get('y', 0),
            width=layer.get('width', 0),
            height=layer.get('height', 0),
            bordercolor=layer.get('bordercolor', None),
            fillcolor=layer.get('fillcolor'),
            border=layer.get('border', 1),
            alpha_enable=layer.get('alpha_enable', False)
        )

    def _draw_ellipse(self, canvas, layer, content):
        if layer.skip_empty and (not content):
            logger.debug('%s skip_empty is enable and content is empty',
                         layer.name)
            return
        canvas.draw_ellipse(
            x=layer.get('x', 0),
            y=layer.get('y', 0),
            width=layer.get('width', 0),
            height=layer.get('height', 0),
            bordercolor=layer.get('bordercolor', None),
            fillcolor=layer.get('fillcolor'),
            border=layer.get('border', 1),
            alpha_enable=layer.get('alpha_enable', False)
        )

    def _draw_text(self, canvas, layer, content):
        canvas.draw_text(
            text=_s(layer.label, content),
            x=layer.get('x', 0),
            y=layer.get('y', 0),
            color=layer.get('color', '#000000'),
            maxwidth=layer.get('maxwidth', None),
            maxheight=layer.get('maxheight', None),
            breakseparator=layer.get('breakseparator', ''),
            minfontsize=layer.get('minfontsize', 4),
            fontdiff=layer.get('fontdiff', 2),
            fontsize=layer.get('fontsize', 24),
            bold=layer.get('bold', False),
            shadowcolor=layer.get('shadowcolor', None),
            shadow_dx=layer.get('shadow_dx', 4),
            shadow_dy=layer.get('shadow_dy', 4),
        )

    def draw_oneline_text(self, canvas, layer, content):
        canvas.draw_oneline_text(
            text=_s(layer.label, content),
            x=layer.get('x', 0),
            y=layer.get('y', 0),
            width=layer.get('width', 0),
            height=layer.get('height', 0),
            color=layer.get('color', '#000000'),
            ignore_offset=layer.get('ignore_offset', True),
            maxfontsize=layer.get('maxfontsize', 24),
            minfontsize=layer.get('minfontsize', 4),
            bold=layer.get('bold', False),
            shadowcolor=layer.get('shadowcolor', None),
            shadow_dx=layer.get('shadow_dx', 4),
            shadow_dy=layer.get('shadow_dy', 4),
        )

    def _find_render_impl(self, layer):
        ''' return rendering implementation, like function method '''
        name = _s(layer.name, '(no name)')

        if layer.type == 'image':
            return (name, self._draw_image)
        if layer.type == 'rectangle':
            return (name, self._draw_rectangle)
        if layer.type == 'ellipse':
            return (name, self._draw_ellipse)
        if layer.type == 'text':
            return (name, self._draw_text)
        if layer.type == 'linetext':
            return (name, self.draw_oneline_text)

        # not implemented
        return (name, None)

    def render(self, record):
        ''' generate card image by using config and record data.
        It returns PIL.Image object as a result.  '''
        if self.definition.card.size:
            canvas = CardCanvas(self.definition.card.size.width,
                                self.definition.card.size.height)
        else:
            canvas = CardCanvas()
        logger.debug('canvas initialized: %s x %s px',
                     canvas.width, canvas.height)
        for (idx, layer) in enumerate(self.definition.card.layers):
            (name, render_impl) = self._find_render_impl(layer)
            if render_impl is None:
                logger.warn('skipped: (%s, %s) is not implemented', idx, name)
                continue
            logger.debug('render layer named %s', name)
            content_key = layer.get('ref', name)
            layer_content = record.get(content_key)
            if (not layer.always) and (layer_content in ['', None]):
                logger.debug('skipped: content for layer %s is empty',
                             content_key)
                continue
            try:
                render_impl(canvas, layer, layer_content)
            except Exception as e:
                logger.exception(e)

        # draw card border
        border = self.definition.card.border.get('width', 2)
        if border > 0:
            width = canvas.image.width - 1
            height = canvas.image.height - 1
            canvas.draw_rect(
                0, 0, width=width, height=height, border=border,
                bordercolor=self.definition.card.border.get('color', '#000000'))
        return canvas.image

    def _composite_as_tile(self, cards, w, h):
        ''' Composite card images as tile layout '''
        if w <= 1 and h <= 1:
            return cards[0]
        (width, height) = (cards[0].width, cards[0].height)
        interspace = self.definition.output.tile.get('interspace', 10)
        size = (w * width + (w - 1) * interspace,
                h * height + (h - 1) * interspace)
        image = Image.new(mode='RGBA', size=size, color=(255, 255, 255))
        for (idx, card) in enumerate(cards):
            (x, y) = (idx % w, idx // w)
            dest = ((width + interspace) * x, (height + interspace) * y)
            image.alpha_composite(card, dest=dest)
        return image

    def render_all(self, records, w=3, h=3):
        ''' Generate card image list by using config and each record data.
        It returns list of PIL.Image object which was located as tile layout w x h.  '''
        self.console('- generate card count: {n}'.format(n=len(records)))
        (cards, pages) = ([], [])
        for record in records:
            cards.append(self.render(record))
            if len(cards) >= w * h:
                pages.append(self._composite_as_tile(cards, w, h))
                cards = []
            self.console('.', end='', flush=True)
        if len(cards) > 0:
            pages.append(self._composite_as_tile(cards, w, h))
        self.console('')
        self.console('- generated, total page = {n}'.format(n=len(pages)))
        return pages

    def save_as_images(self, filename_without_ext, records, w=1, h=1):
        ''' Save results of render_all as indexed image name and PNG format.
        If you want to use tile layout, set w and h more than 1. '''
        for (page_no, image) in enumerate(self.render_all(records, w, h), start=1):
            filename = '{0}{1:04d}.png'.format(filename_without_ext, page_no)
            image.save(filename, 'PNG')
        self.console('- save all png images succeeded')

    def save_as_pdf(self, filename, records, w=3, h=3):
        ''' Save a pdf file.
        Each page expresses an element of render_all result list.
        Note that this method is specialized for (w, h) = (3, 3). '''
        pdf = canvas.Canvas(filename, pagesize=A4)
        pages = self.render_all(records, w, h)
        if len(pages) <= 0:
            pdf.showPage()  # insert empty page
            pdf.save()
            self.console('.', end='', flush=True)
            return

        # small edge is based to print
        is_width_based = (A4[0] / pages[0].width < A4[1] / pages[0].height)
        scale = self.definition.output.tile.get('scale', 1.0)
        for (index, image) in enumerate(pages):
            if index > 0:
                pdf.showPage()  # go next page
            if is_width_based:
                width = round((A4[0] if image.width > A4[0]
                               else image.width) * scale)
                height = round(image.height * width / image.width)
            else:
                height = round((A4[1] if image.height > A4[1]
                                else image.height) * scale)
                width = round(image.width * height / image.height)
            if self.definition.output.tile.get('lu', 'normal') == 'centerize':
                x = (A4[0] - width) // 2
                y = (A4[1] - height) // 2
            else:
                x = 0
                y = (A4[1] - height)
            # write
            pdf.drawInlineImage(image, x, y, width=width, height=height)

        pdf.save()
        self.console('- save pdf succeeded')

    def save(self, filename, records):
        ''' Create resouces and save them following setting file '''
        self.console('start: Testplay Card Generator')
        w = self.definition.output.tile.get('width', 3)
        h = self.definition.output.tile.get('height', 3)
        file_format = self.definition.output.format
        if file_format == 'pdf':
            self.console(
                '- target file and format: {f} (pdf)'.format(f=filename))
            return self.save_as_pdf(filename, records, w, h)
        elif file_format == 'png':
            (basename, _) = os.path.splitext(filename)
            self.console(
                '- target file and format: {f}0000.png (png)'.format(f=basename))
            return self.save_as_images(basename, records, w, h)
        raise ValueError(
            'Setting file format is wrong, only "pdf" and "png" are supported. ')
