#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Card Rendering Engine Implementation '''
import sys
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

from . import staticdata

__FONT_PATH = staticdata.staticfile_path(dict(
    bold=os.path.join('fonts', 'NotoSansCJKjp-Bold.ttf'),
    plain=os.path.join('fonts', 'NotoSansCJKjp-Light.ttf'),
), True)


def _fontpath(is_bold=False):
    path = __FONT_PATH['bold'] if is_bold else __FONT_PATH['plain']
    return path


class CardCanvas:
    ''' express a card image and its canvas '''

    def __init__(self, width=372, height=520):
        ''' create canvas '''
        self.width = width
        self.height = height
        self.size = (width, height)
        self.image = Image.new(
            mode='RGBA', size=self.size, color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

    def _split_lines(self, font, text, maxwidth, breakseparator):
        if maxwidth is None:
            return text
        results = []
        for ch in breakseparator:
            text = text.replace(ch, ch + '\n')
        for _line in text.replace('\r', '').split('\n'):
            line = _line
            while len(line) > 0:
                (width, _) = font.getsize(line)
                if width <= maxwidth:
                    results.append(line)
                    break
                # search from left because it is fast normally
                # to find split point from left more than 3 lines
                right = len(line)
                for r in range(2, len(line)):
                    (width, _) = font.getsize(line[0:r])
                    if width > maxwidth:
                        right = r - 1
                        break
                results.append(line[0:right])
                line = line[right:]
        return '\n'.join(results)

    def _alpha_context(self, context, alpha_enable):
        ''' Draw with transparent mode '''
        if alpha_enable:
            image = Image.new(mode='RGBA', size=self.size,
                              color=(255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            context(draw)
            self.image.alpha_composite(image)
        else:
            context(self.draw)

    def draw_text(self, text, x, y, color,
                  maxwidth=None, maxheight=None,
                  breakseparator='', bold=False,
                  fontsize=24, minfontsize=4, fontdiff=2,
                  shadowcolor=None, shadow_dx=4, shadow_dy=4):
        ''' write text on draw objcet by keeping never over maxwidth pixel '''
        fontpath = _fontpath(bold)
        font = ImageFont.truetype(fontpath, fontsize, encoding='utf-8')
        multiline = self._split_lines(font, text, maxwidth, breakseparator)

        if maxheight is not None:
            # if out of bounds, call more small draw_text
            total_height = sum([
                font.getsize(s)[1] + 1 for s in multiline.split('\n')
            ])
            if (fontsize > minfontsize) and (total_height > maxheight):
                return self.draw_text(
                    text, x, y, color,
                    breakseparator=breakseparator, bold=bold,
                    maxwidth=maxwidth, maxheight=maxheight,
                    fontsize=fontsize - fontdiff, minfontsize=minfontsize, fontdiff=fontdiff,
                    shadowcolor=shadowcolor, shadow_dx=shadow_dx, shadow_dy=shadow_dy)

        if shadowcolor is not None:
            xy = (x + shadow_dx, y + shadow_dy)
            self.draw.text(xy, multiline, font=font, fill=shadowcolor)
        self.draw.text((x, y), multiline, font=font, fill=color)

    def draw_oneline_text(self, text, x, y, width, height, color,
                          ignore_offset=True,
                          bold=False, maxfontsize=24, minfontsize=4,
                          shadowcolor=None, shadow_dx=4, shadow_dy=4):
        ''' draw one line text in (x, y, width, height) bounding '''
        fontpath = _fontpath(bold)
        bestfont = ImageFont.truetype(fontpath, minfontsize, encoding='utf-8')
        bestfontsize = minfontsize
        for fontsize in range(maxfontsize, minfontsize, -1):
            font = ImageFont.truetype(fontpath, fontsize, encoding='utf-8')
            (w, _) = font.getsize(text)
            if w <= width:
                bestfont = font
                bestfontsize = fontsize
                break

        # centerize for bounding
        # adhoc: offset calculation may be for specific font
        (w, h) = bestfont.getsize(text)
        (_, offset) = bestfont.getmask2(text)
        xoffset = offset[0] if ignore_offset else 0
        yoffset = offset[1] if ignore_offset else 0
        x = round(x + (width - w - xoffset) / 2)
        y = round(y + (height - h - yoffset) / 2)

        if shadowcolor is not None:
            xy = (x + shadow_dx, y + shadow_dy)
            self.draw.multiline_text(
                xy, text, font=bestfont, fill=shadowcolor)
        self.draw.multiline_text((x, y), text, font=bestfont, fill=color)

    def draw_rect(self, x, y, width, height,
                  bordercolor=None, fillcolor=None, border=1, alpha_enable=False):
        ''' draw rectangle with border '''
        if fillcolor is not None:
            def _context(draw):
                xy = [x, y, x + width, y + height]
                draw.rectangle(xy, fill=fillcolor)
            self._alpha_context(_context, alpha_enable)
        if bordercolor is not None:
            for (idx, _) in enumerate(range(border)):
                def _context(draw):
                    xy = [x + idx, y + idx, x + width - idx, y + height - idx]
                    draw.rectangle(xy, outline=bordercolor)
                self._alpha_context(_context, alpha_enable)

    def draw_ellipse(self, x, y, width, height,
                     bordercolor=None, fillcolor=None, border=1, alpha_enable=False):
        ''' draw ellipse with border '''
        if fillcolor is not None:
            def _context(draw):
                xy = [x, y, x + width, y + height]
                draw.ellipse(xy, fill=fillcolor)
            self._alpha_context(_context, alpha_enable)
        if bordercolor is not None:
            for (idx, _) in enumerate(range(border)):
                def _context(draw):
                    xy = [x + idx, y + idx, x + width - idx, y + height - idx]
                    draw.ellipse(xy, outline=bordercolor)
                self._alpha_context(_context, alpha_enable)

    def draw_line(self, x1, y1, x2, y2, color,
                  width=1, alpha_enable=False):
        ''' draw ellipse with border '''
        def _context(draw):
            xy = [x1, y1, x2, y2]
            draw.line(xy, fill=color, width=width)
        self._alpha_context(_context, alpha_enable)

    def draw_image(self, image, x, y, width=None, height=None, centerize=False):
        ''' put image (PIL.Image) on this canvas as (x, y, width, height) size '''
        if (width is not None) and (height is not None):
            size = (width, height)
            layer = image.resize(size)
        elif (width is not None) and (height is None):
            ratio = float(width) / float(image.width)
            size = (width, round(image.height * ratio))
            layer = image.resize(size)
            y = y + round((self.size[1] - size[1]) / 2) if centerize else y
        elif (width is None) and (height is not None):
            ratio = float(height) / float(image.height)
            size = (round(image.width * ratio), height)
            layer = image.resize(size)
            x = x + round(size[0] / 2) if centerize else x
        else:
            layer = image
        if layer.mode != 'RGBA':
            layer = layer.convert('RGBA')
        self.image.alpha_composite(layer, dest=(x, y))
