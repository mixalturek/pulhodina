#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
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

import argparse
import sys
import os
import re
import time
from decimal import *


###############################################################################

APP_NAME = 'Pulhodina'
VERSION = '1.1-SNAPSHOT'
WEBSITE = 'https://github.com/mixalturek/pulhodina'

INPUT_FILE_ENCODING = 'utf-16-le'
FILES_ENCODING = 'utf-8'
RECORDS_DELIMITER = "\t"
SAVED_MINUTES_PER_RUN = 30


###############################################################################

def parse_arguments(argv):
    """Parse all command line arguments and return them in object form."""
    parser = argparse.ArgumentParser(
            prog=argv[0],
            description='Format text/plain tab-delimited table with a very \
                custom structure to HTML which is importable to MS Excel \
                and OpenOffice/LibreOffice Calc.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
            '-V', '--version',
            help='show version and exit',
            action='version',
            version='%(prog)s ' + VERSION
    )

    parser.add_argument(
            '-w', '--owners',
            metavar='FILE',
            dest='owners_file',
            help='file with tab-delimited accounts and their owners',
            required=False
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

    parser.add_argument(
            '-c', '--counter',
            metavar='FILE',
            dest='counter_file',
            help='file with counter of saved time',
            required=False
    )

    return parser.parse_args(argv[1:])


###############################################################################

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
        """Test if the section is empty"""
        return len(self.records) == 0

    def is_same_values(self, param):
        """Test if a parameter has the same value in all records."""
        first = getattr(self.records[0], param)

        for record in self.records[1:]:
            if first != getattr(record, param):
                return False

        return True


###############################################################################

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

class HtmlFormatter(object):
    """Format table in a file to HTML form."""

    def __init__(self, account_owners):
        """Constructor."""
        self.account_owners = account_owners


    def transform_in_place(self, data):
        """Transform records data in place."""
        for section in data.sections:
            for record in section.records:
                open_del     = Decimal(record.open_del.replace(',', '')) * 1000
                receivables  = Decimal(record.receivables.replace(',', ''))
                special_liab = Decimal(record.special_liab.replace(',', ''))
                cred_limit   = Decimal(record.cred_limit.replace(',', '')) * 1000

                saldo = receivables + special_liab
                available = cred_limit - (saldo + open_del)

                # ',' is thousands delimiter
                record.open_del   = "{:,}".format(open_del).rstrip('0').rstrip('.')
                record.saldo      = "{:,}".format(saldo).rstrip('0').rstrip('.')
                record.cred_limit = "{:,}".format(cred_limit).rstrip('0').rstrip('.')
                record.available  = "{:,}".format(available).rstrip('0').rstrip('.')


    def format(self, data, fw):
        """Apply tranformation and format data to HTML table."""
        self.write_header(fw)
        self.write_data(fw, data)
        self.write_footer(fw)


    def write_header(self, fw):
        """Write HTML header."""
        print(
'''<!DOCTYPE html>
<html lang="en" dir="ltr">
    <head>
        <meta charset="{0}">
        <title>{1} Report</title>

        <style>
            body {{ font-size: 8pt; font-family: sans-serif; }}
            table {{ border-collapse: collapse; text-align: center; }}
            thead {{ background-color: yellow; }}
            th, td {{ border: 1px solid black; padding: 0 0.5em 0 0.5em; }}
            td:hover {{ background-color: #C0C0FF; }}
            .space {{ height: 1em; }}
            footer {{ margin: 2em 0 1em 0; }}
        </style>
    </head>
    <body>
        <main>
            <table>
                <thead>
                    <tr>
                        <th>Cred. acct</th>
                        <th>Name 1</th>
                        <th>PO Number</th>
                        <th>Credit value</th>
                        <th>Open del</th>
                        <th>Saldo</th>
                        <th>Cred.limit</th>
                        <th>Available</th>
                        <th>Use</th>
                        <th>Next date</th>
                        <th>Status</th>
                        <th>Approver</th>
                        <th>Accnt owner</th>
                    </tr>
                </thead>
                <tbody>
'''.format(FILES_ENCODING.upper(), APP_NAME), file=fw)


    def write_data(self, fw, data):
        """Write data."""
        for section in data.sections:
            self.write_section(fw, section)
            print('                    <tr class="space"><td colspan="13"></td></tr>', file=fw)


    def write_section(self, fw, section):
        """Write data of a section."""
        first_row = True
        rowspan = len(section.records)
        same_cred_acct    = section.is_same_values('cred_acct')
        same_name1        = section.is_same_values('name1')
        same_po_number    = section.is_same_values('po_number')
        same_credit_value = section.is_same_values('credit_value')
        same_open_del     = section.is_same_values('open_del')
        same_saldo        = section.is_same_values('saldo')
        same_cred_limit   = section.is_same_values('cred_limit')
        same_available    = section.is_same_values('available')
        same_use          = section.is_same_values('use')
        same_next_date    = section.is_same_values('next_date')

        for record in section.records:
            print('                    <tr>', file=fw)
            self.write_cell(fw, first_row, rowspan, same_cred_acct,    record.cred_acct)
            self.write_cell(fw, first_row, rowspan, same_name1,        record.name1)
            self.write_cell(fw, first_row, rowspan, same_po_number,    record.po_number)
            self.write_cell(fw, first_row, rowspan, same_credit_value, record.credit_value)
            self.write_cell(fw, first_row, rowspan, same_open_del,     record.open_del)
            self.write_cell(fw, first_row, rowspan, same_saldo,        record.saldo)
            self.write_cell(fw, first_row, rowspan, same_cred_limit,   record.cred_limit)
            self.write_cell(fw, first_row, rowspan, same_available,    record.available)
            self.write_cell(fw, first_row, rowspan, same_use,          record.use)
            self.write_cell(fw, first_row, rowspan, same_next_date,    record.next_date)

            self.write_cell(fw, first_row, rowspan, True, '')
            self.write_cell(fw, first_row, rowspan, True, '')

            try:
                owner = self.account_owners[record.cred_acct]
            except KeyError as e:
                owner = 'UNKNOWN'

            self.write_cell(fw, first_row, rowspan, same_cred_acct, owner)

            print('                    </tr>', file=fw)
            first_row = False


    def write_cell(self, fw, first_row, rowspan, same, value):
        """Write value of one cell."""
        if first_row and same:
            print('                        <td rowspan="{0}">{1}</td>'.format(rowspan, value), file=fw)
        elif not same:
            print('                        <td>{0}</td>'.format(value), file=fw)


    def write_footer(self, fw):
        """Write HTML footer."""
        print(
'''
                </tbody>
            </table>
        </main>
        <footer>
            The report was formatted using <a href="{2}">{0}</a> version {1}.
            Feel free to contact the author and donate further development.
        </footer>
    </body>
</html>
'''.format(APP_NAME, VERSION, WEBSITE), file=fw)


###############################################################################

def get_files_in_directory(dir):
    """Get names of files in a directory, non-recursive."""
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]


###############################################################################

def format_one_file(input_path, output_path, account_owners):
    """Format a file."""
    with open(input_path, mode='r', encoding=INPUT_FILE_ENCODING) as fr:
        input_lines = fr.readlines()

    parser = Parser()
    data_file = parser.parse(input_lines)

    formatter = HtmlFormatter(account_owners)
    formatter.transform_in_place(data_file)

    with open(output_path, mode='w', encoding=FILES_ENCODING) as fw:
        formatter.format(data_file, fw)


###############################################################################

def read_account_owners(owners_file):
    """Read account owners from a file if it is defined."""
    if owners_file is None:
        return dict()

    with open(owners_file, mode='r', encoding=FILES_ENCODING) as fr:
        input_lines = fr.readlines()

    account_owners = dict()

    for line in input_lines:
        parts = [part.strip() for part in line.split(RECORDS_DELIMITER)]

        try:
            account_owners[parts[0]] = parts[1]
        except IndexError as e:
            print("ERROR: Too less parts for account owner, skipping:", parts, file=sys.stderr)

    return account_owners


###############################################################################

def format_multiple_files(args, file_names):
    """Format files very specially."""
    account_owners = read_account_owners(args.owners_file)

    for file in file_names:
        input_path = os.path.join(args.input_dir, file)
        output_path = os.path.join(args.output_dir, file)

        if file.rfind(".") == -1:
            output_path += ".html"
        else:
            output_path = re.sub(r'[^.]+$', 'html', output_path)

        format_one_file(input_path, output_path, account_owners)


###############################################################################

def inc_saved_time(counter_file):
    """Increment persisted counter of saved time and return the updated value."""
    try:
        with open(counter_file, mode='r', encoding=FILES_ENCODING) as fr:
            saved_time = int(fr.read().strip())
    except IOError as e:
        print('WARNING: Reading of saved time failed', e, file=sys.stderr)
        saved_time = 0
    except ValueError as e:
        print('WARNING: Broken saved time', e, file=sys.stderr)
        saved_time = 0

    saved_time += SAVED_MINUTES_PER_RUN

    try:
        with open(counter_file, mode='w', encoding=FILES_ENCODING) as fw:
            print(saved_time, file=fw)
    except IOError as e:
        print('WARNING: Writing of saved time failed', e, file=sys.stderr)

    return saved_time


###############################################################################

def prety_print_saved_time(saved_time, elapsed_time):
    """Prety print the saved time."""
    print('Executions:', saved_time // SAVED_MINUTES_PER_RUN)
    print('Execution time: {0:.2} ms'.format(elapsed_time))
    print('Saved time:', SAVED_MINUTES_PER_RUN, 'minutes')

    units   = ['years', 'months', 'days', 'hours', 'minutes']
    factors = [12*30*24*60, 30*24*60, 24*60, 60, 1]

    remainder = saved_time
    pretty_total = []

    for i in range(0, len(factors)):
        if remainder == 0:
            break

        count = remainder // factors[i]
        remainder = remainder % factors[i]

        if count > 0:
            pretty_total.append("{0} {1}".format(count, units[i]))

    print('Total saved time:', saved_time, 'minutes', '(' + ', '.join(pretty_total) + ')')


###############################################################################

def main(argv):
    """Application enter."""
    print(APP_NAME, VERSION)
    start_time = time.time()

    args = parse_arguments(argv)
    file_names = get_files_in_directory(args.input_dir)

    if len(file_names) > 0:
        # Only Python >= 3.4.1 is supported
        os.makedirs(args.output_dir, mode=0o755, exist_ok=True)
        format_multiple_files(args, file_names)

        if args.counter_file is not None:
            saved_time = inc_saved_time(args.counter_file)
            elapsed_time = time.time() - start_time
            prety_print_saved_time(saved_time, elapsed_time)


###############################################################################

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt as keyboard_exception:
        sys.exit('ERROR: Interrupted by user')
    except FileNotFoundError as not_found_exception:
        sys.exit('ERROR: ' + str(not_found_exception))
