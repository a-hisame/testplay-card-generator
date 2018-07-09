#!/usr/bin/python
# -*- coding: utf-8 -*-

''' distutils/setuptools install script. '''

import os

from setuptools import setup, find_packages

here = os.path.dirname(__file__)

setup(
    name='tcgen',
    version='0.0.1',
    packages=find_packages(exclude=['tests', 'tests.*', 'docs']),
    data_files=[
        ('fonts', ['data/fonts/NotoSansCJKjp-Bold.ttf',
                   'data/fonts/NotoSansCJKjp-Light.ttf']),
    ],
    entry_points={
        'console_scripts': [
            'tcgen = tcgen:main',
        ]
    }
)
