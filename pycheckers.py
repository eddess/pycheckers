#!/usr/bin/env python
"""Combines pylint and pep8 for checking"""

# Copyright (c) 2002-present, Damn Simple Solutions Ltd.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of the Damn Simple Solutions Ltd. nor the names
#       of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function
from re import compile as re_compile
from optparse import OptionParser
import sys
from StringIO import StringIO
from os.path import exists as file_exists

from pep8 import _main as pep8main
from pylint import run_pylint as pylintmain


class LintRunner(object):
    """The base class for a lint object"""
    def __init__(self, debug=False):
        self._debug = debug
        self.sane_default_ignore_codes = set([])
        self.command = None
        self.run_command = None
        self.env = None
        self._debug = debug
        self.output_matcher = re_compile(
            r'^(([a-zA-Z]:){0,1}[^:]+):(\d+):(\d+): ([a-zA-Z]\d+) (.*)$')

    @property
    def run_flags(self):  # pylint: disable=R0201
        """Return flags for running the linter"""
        return ()

    def process_line(self, line, filename):
        """Parse output line"""
        line_m = self.output_matcher.match(line)
        output = ''
        if line_m is not None:
            column = int(line_m.group(4)) + 1
            code = line_m.group(5)[0]
            if code in ['C', 'E', 'R', 'W']:
                output = filename + ':' + line_m.group(3) + ':' \
                    + str(column) + ':' \
                    + line_m.group(5)[0] + ':' \
                    + '(' + line_m.group(5) + ') ' + line_m.group(6)
            else:
                return
            print(output)

    def run(self, filenames):
        """Execute the linter"""
        args = [self.command]
        args.extend(self.run_flags)
        args.extend(filenames)
        if self._debug:
            print("DEBUG: command = ", ' '.join(args))

        sysargv = sys.argv
        sys.argv = args
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        new_stdout = StringIO()
        new_stderr = StringIO()
        try:
            sys.stdout = new_stdout
            sys.stderr = new_stderr
            if callable(self.run_command):
                self.run_command()  # pylint: disable=E1102
        except SystemExit:
            pass
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        sys.argv = sysargv

        new_stdout = new_stdout.getvalue().split('\n')
        new_stderr = new_stderr.getvalue().split('\n')
        for line in new_stdout:
            if self._debug:
                print(self.command, 'STDOUT:', line)
                print('\n\n')
            self.process_line(line, filenames[0])

        for line in new_stderr:
            if self._debug:
                print(self.command, 'STDERR:', line)


class PylintRunner(LintRunner):
    """Linting with the pylint linter"""

    def __init__(self, debug=False):
        super(PylintRunner, self).__init__(debug=debug)
        self.command = 'pylint'
        self.run_command = pylintmain
        self.sane_default_ignore_codes = set([
            'F0401',  # Unable to import
            'E0611',  # module does not contain symbol. Handled by Jedi
            'E1123',  # unexpected argument in constructor
            'E1101',  # does not have member. Jedi handles this
            'W0232',  # no init method in class
            'E1120',  # no constructor for
            'C0330',  # wrong indentation handled by pep8
        ])

    @property
    def run_flags(self):
        return ('--reports=no',
                '--msg-template="{path}:{line}:{column}: {msg_id} {msg}"',
                '--disable=' + ','.join(self.sane_default_ignore_codes))


class Pep8Runner(LintRunner):
    """Linting with pep8"""

    def __init__(self, debug=False):
        super(Pep8Runner, self).__init__(debug=debug)
        self.command = 'pep8'
        self.run_command = pep8main
        self.sane_default_ignore_codes = set([
        ])

    @property
    def run_flags(self):
        return ('--repeat',
                '--filename=*py',
                '--ignore=%s' % ','.join(self.sane_default_ignore_codes))


def main():
    """Execution entry point"""
    usage = "usage: %prog [options] [PY_MODULE_OR_PACKAGE]..."
    parser = OptionParser(usage=usage)

    parser.add_option(
        "-d", "--debug",
        action="store_true",
        default=False,
        help=("show debug output"))
    parser.add_option(
        '-r', "--reports",
        default='y',
        help=("Just for flycheck's sake"))
    parser.add_option(
        "--msg-template",
        help=("Just for flycheck's sake"))
    parser.add_option(
        "--rcfile",
        help=("Just for flycheck's sake"))
    options, filenames = parser.parse_args()

    if len(filenames) < 1:
        parser.print_help()
        exit(1)

    for filename in filenames:
        if not file_exists(filename):
            print('Error: ' + filename + ' does not exist')
            exit(1)

    for RunnerClass in {Pep8Runner, PylintRunner}:  # pylint: disable=C0103
        runner = RunnerClass(debug=options.debug)
        try:
            runner.run(filenames)
        except TypeError:
            pass

if __name__ == '__main__':
    main()
