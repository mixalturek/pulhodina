#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Michal Turek
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

###############################################################################
####

import argparse
import sys


###############################################################################
####

VERSION = '0.1.0-SNAPSHOT'


###############################################################################
####

def parse_arguments(argv):
    """
    Parse all command line arguments and return them in object form.
    """

    parser = argparse.ArgumentParser(
            prog=argv[0],
            description='Save half an hour to Zuzana',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
            '-V', '--version',
            help='show version and exit',
            action='version',
            version='%(prog)s ' + VERSION
    )

    parser.add_argument(
            '-v', '--verbose',
            help='increase output verbosity',
            action='store_true',
            default=False
    )

    parser.add_argument(
            '-i', '--in',
            metavar='DIR',
            dest='input_dir',
            help='path to directory with input files',
            required=True
    )

    parser.add_argument(
            '-o', '--out',
            metavar='DIR',
            dest='output_dir',
            help='path to directory with output files',
            required=True
    )

    return parser.parse_args(argv[1:])


###############################################################################
####

def main(argv):
    arguments = parse_arguments(argv)

    if arguments.verbose:
        print("Raw arguments: {0}".format(argv))
        print("Verbose: {0}".format(arguments.verbose))
        print("Input directory: {0}".format(arguments.input_dir))
        print("Output directory: {0}".format(arguments.output_dir))


###############################################################################
####

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt as keyboard_exception:
        sys.exit('ERROR: Interrupted by user')
