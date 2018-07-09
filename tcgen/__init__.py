#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Simple Entry Point for Testplay Card Generator on CLI '''


import sys
import os
import argparse
import traceback

here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(here)

from tcgen.engine import TestCardGeneratorEngine


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description='testplay card generator (alpha version)',
        add_help=True)
    parser.add_argument('--layout', required=True,
                        help='Card layout file (only utf8 yml format supported)')
    parser.add_argument('--data', required=True,
                        help='Card contents file (only utf8 csv supported)')
    parser.add_argument('--output', default='output.pdf',
                        help='Output file name')
    parser.add_argument('--quiet', action='store_true',
                        help='If enabled, no output the progress')
    parser.add_argument('--dryrun', action='store_true',
                        help='If enabled, not generate output file')
    return parser.parse_args(argv)


def main(argv=sys.argv[1:]):
    args = _parse_args(argv)
    TestCardGeneratorEngine.run(
        layoutfile=args.layout, datafile=args.data,
        output=args.output, is_quiet=args.quiet, dryrun=args.dryrun)


if __name__ == '__main__':
    main()
