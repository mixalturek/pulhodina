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
import os
import re


###############################################################################
####

VERSION = '0.1.0-SNAPSHOT'
INPUT_FILE_ENCODING='utf-16-le'
OUTPUT_FILE_ENCODING='utf-8'
RECORDS_DELIMITER="\t"


###############################################################################
####

def parse_arguments(argv):
    """Parse all command line arguments and return them in object form."""
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

def debug_show_arguments(argv, arguments):
    """Show parsed command line arguments if verbose is enabled."""
    if arguments.verbose:
        print("Raw arguments:   ", argv)
        print("Verbose:         ", arguments.verbose)
        print("Input directory: ", arguments.input_dir)
        print("Output directory:", arguments.output_dir)


###############################################################################
####

class Record(object):
    """Data of a record."""

    def __init__(self, line):
        """Constructor."""
        parts = [part.strip() for part in line.split(RECORDS_DELIMITER)]

        try:
            self.sorg         = parts[0]
            self.cred_acct    = parts[1]
            self.name1        = parts[2]
            self.po_number    = parts[3]
            self.credit_value = parts[4]
            self.open_del     = parts[5]
            self.receivables  = parts[6]
            self.special_liab = parts[7]
            self.cred_limit   = parts[8]
            self.use          = parts[9]
            self.next_date    = parts[10]
        except IndexError as e:
            print("ERROR: Too less parts for record, skipping:", parts, file=sys.stderr)

    def __str__(self):
        """Format object to a string."""
        attrs = vars(self)
        return ', '.join("'{0}'".format(v[1]) for v in attrs.items())


###############################################################################
####

class Section(object):
    """Data stored in a section."""

    def __init__(self):
        """Constructor."""
        self.records = []

    def __str__(self):
        """Format object to a string."""
        return "\n".join([str(r) for r in self.records])

    def add_record(self, record):
        """Add a new record."""
        self.records.append(record)

    def is_empty(self):
        """Is the section empty?"""
        return len(self.records) == 0


###############################################################################
####

class DataFile(object):
    """Data stored in a file."""

    def __init__(self):
        """Constructor."""
        self.sections = []

    def __str__(self):
        """Format object to a string."""
        return "\n\n".join([str(s) for s in self.sections])

    def add_section(self, section):
        """Add a new section."""
        if section.is_empty():
            return

        self.sections.append(section)


###############################################################################
####

class Parser(object):
    """Parse input data to the internal representation."""

    def __init__(self):
        """Constructor."""
        pass

    def parse(self, lines):
        data_file = DataFile()
        current_section = Section()

        for line in lines[2:]:
            line = line.strip()

            if len(line) == 0:
                continue

            if line.startswith('*'):
                data_file.add_section(current_section)
                current_section = Section()
                continue

            record = Record(line)
            current_section.add_record(record)

        # Add unfinished one if any
        data_file.add_section(current_section)

        return data_file


###############################################################################
####

class VerySpecialHtmlFormatter(object):
    """Format table in a file to HTML form."""

    def __init__(self):
        """Constructor."""
        pass

    def format(self, data_file):
        """Apply tranformation and format data to HTML table."""
        return str(data_file)


###############################################################################
####

def get_files_in_directory(dir):
    """Get names of files in a directory, non-recursive."""
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]


###############################################################################
####

def format_one_file(input_path, output_path):
    """Format a file very specially."""
    with open(input_path, mode='r', encoding=INPUT_FILE_ENCODING) as fr:
        input_lines = fr.readlines()

    parser = Parser()
    data_file = parser.parse(input_lines)

    formatter = VerySpecialHtmlFormatter()
    output = formatter.format(data_file)

    with open(output_path, mode='w', encoding=OUTPUT_FILE_ENCODING) as fw:
        fw.write(output)


###############################################################################
####

def format_multiple_files(args, file_names):
    """Format files very specially."""
    for file in file_names:
        input_path = os.path.join(args.input_dir, file)
        output_path = os.path.join(args.output_dir, file)
        output_path = re.sub(r'[^.]+$', 'html', output_path)

        if args.verbose:
            print(input_path, "->", output_path)

        format_one_file(input_path, output_path)


###############################################################################
####

def main(argv):
    """Application enter."""
    args = parse_arguments(argv)
    debug_show_arguments(argv, args)

    file_names = get_files_in_directory(args.input_dir)

    if len(file_names) > 0:
        # Only Python >= 3.4.1 is supported
        os.makedirs(args.output_dir, mode=0o755, exist_ok=True)
        format_multiple_files(args, file_names)


###############################################################################
####

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt as keyboard_exception:
        sys.exit('ERROR: Interrupted by user')
