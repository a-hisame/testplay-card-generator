#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import codecs
import logging

import yaml
from dotmap import DotMap
from PIL import Image

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .cardcanvas import CardCanvas

logger = logging.getLogger(__name__)


class TestCardGeneratorEngine:
    ''' Create testplay card printing file from layout configuration and data source '''

    @staticmethod
    def run(layoutfile, datafile, output,
            from_index=0, to_index=None, is_quiet=False, dryrun=False):
        ''' Most basically usage '''
        engine = TestCardGeneratorEngine.load(layoutfile, is_quiet, dryrun)
        records = TestCardGeneratorEngine.csv2records(datafile)
        if to_index is None:
            to_index = len(records)
        engine.save(output, records[from_index:to_index])

    @staticmethod
    def load(ymlpath, is_quiet=False, dryrun=False, encoding='utf8'):
        ''' engine instance factory method '''
        with codecs.open(ymlpath, 'r', encoding=encoding) as fh:
            layout = yaml.load(fh)
        return TestCardGeneratorEngine(
            layout=layout, is_quiet=is_quiet, dryrun=dryrun)

    @staticmethod
    def csv2records(csvpath, encoding='utf8'):
        ''' create row items from csv data source '''
        with codecs.open(csvpath, 'r', encoding=encoding) as fh:
            reader = csv.DictReader(fh)
            return [row for row in reader]

    def __init__(self, layout=None, is_quiet=False, dryrun=False):
        ''' not recommend to use constractor directly, use TestCardGeneratorEngine.load'''
        self.definition = DotMap(layout)

        # build engine console
        self.is_quiet = is_quiet

        def _console(*argv, **kwargv):
            if not self.is_quiet:
                print(*argv, **kwargv)
                logger.debug('%s %s', argv, kwargv)
        self.console = _console

        # build dryrun engine
        self.dryrun = dryrun

        def _dryrun_wrapper(name, func):
            if not self.dryrun:
                func()
            else:
                self.console('dryrun: {}'.format(name))

        self.dryrun_wrapper = _dryrun_wrapper

    def _layer2kwargv(self, layer):
        ''' Generate arguments for rendering functions.
        This result function also valicates required parameters from layer on yml fileself.

        # basically usage. layer arguments are passed same key-values.
        # but 2nd function validates requires parameters are never None.
        kwargv = self._layer2kwargv(layer)(
            x=layer.get('x'),
            y=layer.get('y'),
            width=layer.get('width'),
            height=layer.get('height'),
        )
        '''
        def _merge(**kwargv):
            merged = kwargv.copy()
            missings = [(k, v) for (k, v) in merged.items() if v is None]
            if len(missings) > 0:
                msg = 'Required Keyword(s) "{}" are missing'.format(
                    ', '.join([k for (k, _) in missings])
                )
                self.console(msg)
                raise ValueError(msg)
            for (k, v) in layer.items():
                if k not in merged:
                    merged[k] = v
            return merged
        return _merge

    def _draw_image(self, canvas, layer, filename):
        imagefile = layer.source if layer.source else filename
        kwargv = self._layer2kwargv(layer)(
            image=Image.open(imagefile),
            x=layer.get('x'),
            y=layer.get('y'),
        )
        canvas.draw_image(**kwargv)

    def _draw_rectangle(self, canvas, layer, content):
        kwargv = self._layer2kwargv(layer)(
            x=layer.get('x'),
            y=layer.get('y'),
            width=layer.get('width'),
            height=layer.get('height'),
        )
        canvas.draw_rect(**kwargv)

    def _draw_ellipse(self, canvas, layer, content):
        kwargv = self._layer2kwargv(layer)(
            x=layer.get('x'),
            y=layer.get('y'),
            width=layer.get('width'),
            height=layer.get('height'),
        )
        canvas.draw_ellipse(**kwargv)

    def _draw_text(self, canvas, layer, content):
        kwargv = self._layer2kwargv(layer)(
            text=layer.get('text', content),
            x=layer.get('x'),
            y=layer.get('y'),
            color=layer.get('color'),
        )
        canvas.draw_text(**kwargv)

    def _draw_title_text(self, canvas, layer, content):
        kwargv = self._layer2kwargv(layer)(
            text=layer.get('label', content),
            x=layer.get('x'),
            y=layer.get('y'),
            width=layer.get('width'),
            height=layer.get('height'),
            color=layer.get('color'),
        )
        canvas.draw_oneline_text(**kwargv)

    def _find_render_impl(self, layer):
        ''' return rendering implementation, like function method '''
        name = layer.get('name', 'NO NAME')

        if layer.type == 'text':
            return (name, self._draw_text)
        if layer.type == 'title':
            return (name, self._draw_title_text)
        if layer.type == 'rectangle':
            return (name, self._draw_rectangle)
        if layer.type == 'ellipse':
            return (name, self._draw_ellipse)
        if layer.type == 'image':
            return (name, self._draw_image)

        # not implemented
        return (name, None)

    def _get_content(self, name, layer, record):
        ''' get layer content from layer and record information '''
        key = layer.ref if 'ref' in layer else name
        return record.get(key)

    def _skip_rendering(self, layer, record, content):
        ''' return render should be skipped or not '''
        if layer.get('always'):
            # if always set, to render anyway
            return (False, '')
        if content in [None, '']:
            return (True, 'content for rendring not found')
        return (False, '')

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
            content = self._get_content(name, layer, record)
            (is_skip, skip_reason) = self._skip_rendering(layer, record, content)
            if is_skip:
                logger.debug('skipped: layer %s rendering skipped (reason: %s)',
                             name, skip_reason)
                continue

            try:
                logger.debug('render: layer named {} (type={})'.format(
                             name, layer.type))
                render_impl(canvas, layer, content)
            except Exception as e:
                self.console('command failed so skipped: name={}, type={}'.format(
                    name, layer.type))
                # logger.exception(e)

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

    def _is_render_cards(self, record):
        ''' a card itself should be rendered or not '''
        ref = self.definition.card.render_only.get('ref')
        if ref is None:
            return True
        values = self.definition.card.render_only.get('values', None)
        if values is None:
            return True

        def comp(obj):
            return str(record.get(ref)) == str(obj)

        if isinstance(values, list):
            return any([comp(v) for v in values])
        else:
            return comp(values)

    def render_all(self, records, w=3, h=3):
        ''' Generate card image list by using config and each record data.
        It returns list of PIL.Image object which was located as tile layout w x h.  '''
        if w < 1 or h < 1:
            raise ValueError('w and h are 1 or more than 1')
        self.console('- generate card candidates: {n}'.format(n=len(records)))
        (rendered, cards, pages) = (0, [], [])
        for record in records:
            if self._is_render_cards(record):
                cards.append(self.render(record))
                rendered = rendered + 1
            if len(cards) >= w * h:
                pages.append(self._composite_as_tile(cards, w, h))
                cards = []
            self.console('.', end='', flush=True)
        if len(cards) > 0:
            pages.append(self._composite_as_tile(cards, w, h))
        self.console('')
        self.console('- generated, rendered = {}, total page = {}'.format(
            rendered, len(pages)))
        return pages

    def save_as_images(self, filename_without_ext, records, w=3, h=3):
        ''' Save results of render_all as indexed image name and PNG format.
        If you want to use tile layout, set w and h are grater than 1 or equals 1. '''
        for (page_no, image) in enumerate(self.render_all(records, w, h), start=1):
            filename = '{0}{1:04d}.png'.format(filename_without_ext, page_no)
            self.dryrun_wrapper(
                'save {}'.format(filename),
                lambda: image.save(filename, 'PNG'))
        self.console('- save all png images succeeded')
        return True

    def save_as_pdf(self, filename, records, w=3, h=3):
        ''' Save a pdf file.
        Each page expresses an element of render_all result list.
        Note that this method is specialized for (w, h) = (3, 3). '''
        pdf = canvas.Canvas(filename, pagesize=A4)
        pages = self.render_all(records, w, h)
        if len(pages) <= 0:
            pdf.showPage()  # insert empty page
            self.dryrun_wrapper(
                'save {}'.format(filename), lambda: pdf.save())
            self.console('.', end='', flush=True)
            return True

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
            if self.definition.output.tile.get('left_upper', 'normal') == 'centerize':
                x = (A4[0] - width) // 2
                y = (A4[1] - height) // 2
            else:
                x = 0
                y = (A4[1] - height)
            # write
            pdf.drawInlineImage(image, x, y, width=width, height=height)

        self.dryrun_wrapper(
            'save {}'.format(filename), lambda: pdf.save())
        self.console('- save pdf succeeded')
        return True

    def _output_ext(self, filename):
        (basename, ext) = os.path.splitext(filename)
        if ext.lower() in ['.pdf', '.png']:
            return ext.lower()[1:]
        return self.definition.output.get('format', 'pdf')

    def save(self, filename, records):
        ''' Create resouces and save them following setting file '''
        self.console('start: Testplay Card Generator')
        w = self.definition.output.tile.get('width', 3)
        h = self.definition.output.tile.get('height', 3)
        file_format = self._output_ext(filename)
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
