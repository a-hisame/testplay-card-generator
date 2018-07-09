#!/usr/bin/python
# -*- coding: utf-8 -*-

''' static file reader which can switch before and after installed by setup.py '''

import sys
import os

_dir_candidates = [
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'data'),  # project local path
    sys.prefix,  # distutils data_files path
]


def staticfile_path(mapping, raise_if_not_found=True):
    ''' Get validate static file path '''
    pathes = {}
    for (key, relative_path) in mapping.items():
        for dirname in _dir_candidates:
            path = os.path.join(dirname, relative_path)
            if os.path.exists(path):
                pathes[key] = path
                break
        if raise_if_not_found and (key not in pathes):
            raise IOError('File not found: {}'.format(relative_path))
    return pathes
