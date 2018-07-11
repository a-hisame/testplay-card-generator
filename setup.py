#!/usr/bin/python
# -*- coding: utf-8 -*-

''' distutils/setuptools install script. '''

import os
import codecs

from setuptools import setup, find_packages

here = os.path.dirname(__file__)

with codecs.open(os.path.join(here, 'requirements.txt'), 'r') as fh:
    requirements = [line.replace('\n', '') for line in fh.readlines()]

setup(
    name='tcgen',
    version='0.0.2',
    packages=find_packages(exclude=['tests', 'tests.*', 'docs']),
    install_requires=requirements,
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
